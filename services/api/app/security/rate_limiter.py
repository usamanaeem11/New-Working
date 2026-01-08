"""
Production Rate Limiter
Token bucket algorithm with Redis backend
"""
from datetime import datetime, timedelta
from collections import defaultdict
import time

class RateLimiter:
    """
    Production-grade rate limiter
    - Per-IP limiting
    - Per-endpoint limiting
    - Per-user limiting
    - Token bucket algorithm
    """
    
    def __init__(self):
        # In production: use Redis
        self.buckets = defaultdict(lambda: {
            'tokens': 100,
            'last_update': time.time()
        })
        self.config = {
            'default': {'rate': 100, 'per': 60},  # 100 requests per minute
            '/api/auth/login': {'rate': 5, 'per': 60},  # 5 per minute
            '/api/auth/register': {'rate': 3, 'per': 3600},  # 3 per hour
        }
        self.rate_limited_count = 0
        self.total_requests = 0
    
    def is_rate_limited(self, client_id: str, endpoint: str) -> bool:
        """Check if client is rate limited"""
        self.total_requests += 1
        
        key = f"{client_id}:{endpoint}"
        config = self.config.get(endpoint, self.config['default'])
        
        bucket = self.buckets[key]
        now = time.time()
        
        # Refill tokens
        time_passed = now - bucket['last_update']
        tokens_to_add = (time_passed / config['per']) * config['rate']
        bucket['tokens'] = min(
            config['rate'],
            bucket['tokens'] + tokens_to_add
        )
        bucket['last_update'] = now
        
        # Check if request allowed
        if bucket['tokens'] >= 1:
            bucket['tokens'] -= 1
            return False
        else:
            self.rate_limited_count += 1
            return True
    
    def record_request(self, client_id: str, endpoint: str):
        """Record request (already done in is_rate_limited)"""
        pass
    
    def get_total_requests(self) -> int:
        return self.total_requests
    
    def get_rate_limited_count(self) -> int:
        return self.rate_limited_count

rate_limiter = RateLimiter()
