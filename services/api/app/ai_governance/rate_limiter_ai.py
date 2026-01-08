"""
AI Rate Limiter - Rate limiting for AI endpoints
Prevents abuse and controls costs
"""
from typing import Dict, Optional
from datetime import datetime, timedelta

class AIRateLimiter:
    """Rate limiting specifically for AI inference endpoints"""
    
    # Rate limits per tier
    LIMITS = {
        'free': {
            'requests_per_hour': 100,
            'requests_per_day': 1000,
            'tokens_per_day': 100000
        },
        'standard': {
            'requests_per_hour': 1000,
            'requests_per_day': 20000,
            'tokens_per_day': 1000000
        },
        'premium': {
            'requests_per_hour': 10000,
            'requests_per_day': 200000,
            'tokens_per_day': 10000000
        },
        'enterprise': {
            'requests_per_hour': None,  # Unlimited
            'requests_per_day': None,
            'tokens_per_day': None
        }
    }
    
    def __init__(self):
        self.usage_tracking = {}
    
    def check_rate_limit(self, user_id: str, model_name: str,
                        tier: str = 'standard', tokens: int = 0) -> Dict:
        """Check if request is within rate limits"""
        
        key = f"{user_id}:{model_name}"
        now = datetime.utcnow()
        
        # Initialize tracking if needed
        if key not in self.usage_tracking:
            self.usage_tracking[key] = {
                'hourly': {'count': 0, 'window_start': now},
                'daily': {'count': 0, 'tokens': 0, 'window_start': now}
            }
        
        usage = self.usage_tracking[key]
        
        # Reset windows if expired
        if now - usage['hourly']['window_start'] > timedelta(hours=1):
            usage['hourly'] = {'count': 0, 'window_start': now}
        
        if now - usage['daily']['window_start'] > timedelta(days=1):
            usage['daily'] = {'count': 0, 'tokens': 0, 'window_start': now}
        
        # Get limits for tier
        limits = self.LIMITS.get(tier, self.LIMITS['standard'])
        
        # Check hourly limit
        if limits['requests_per_hour']:
            if usage['hourly']['count'] >= limits['requests_per_hour']:
                return {
                    'allowed': False,
                    'reason': 'hourly_limit_exceeded',
                    'limit': limits['requests_per_hour'],
                    'used': usage['hourly']['count'],
                    'reset_at': (usage['hourly']['window_start'] + timedelta(hours=1)).isoformat()
                }
        
        # Check daily limit
        if limits['requests_per_day']:
            if usage['daily']['count'] >= limits['requests_per_day']:
                return {
                    'allowed': False,
                    'reason': 'daily_limit_exceeded',
                    'limit': limits['requests_per_day'],
                    'used': usage['daily']['count'],
                    'reset_at': (usage['daily']['window_start'] + timedelta(days=1)).isoformat()
                }
        
        # Check token limit
        if limits['tokens_per_day'] and tokens > 0:
            if usage['daily']['tokens'] + tokens > limits['tokens_per_day']:
                return {
                    'allowed': False,
                    'reason': 'token_limit_exceeded',
                    'limit': limits['tokens_per_day'],
                    'used': usage['daily']['tokens'],
                    'reset_at': (usage['daily']['window_start'] + timedelta(days=1)).isoformat()
                }
        
        # Update usage
        usage['hourly']['count'] += 1
        usage['daily']['count'] += 1
        usage['daily']['tokens'] += tokens
        
        # Return success
        return {
            'allowed': True,
            'hourly_remaining': limits['requests_per_hour'] - usage['hourly']['count'] if limits['requests_per_hour'] else None,
            'daily_remaining': limits['requests_per_day'] - usage['daily']['count'] if limits['requests_per_day'] else None,
            'tokens_remaining': limits['tokens_per_day'] - usage['daily']['tokens'] if limits['tokens_per_day'] else None
        }

ai_rate_limiter = AIRateLimiter()
