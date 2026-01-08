"""
Cost Control - Monitor and limit AI inference costs
"""
from typing import Dict
from datetime import datetime, timedelta

class CostControl:
    """AI inference cost monitoring and limiting"""
    
    def __init__(self):
        self.usage_tracking = {}
        self.budget_limits = {}
    
    def track_inference_cost(self, model_name: str, user_id: str,
                           compute_time: float, tokens: int = 0) -> Dict:
        """Track cost per inference"""
        
        # Simple cost calculation (customize based on actual pricing)
        cost = compute_time * 0.0001 + tokens * 0.000001
        
        key = f"{model_name}:{user_id}"
        if key not in self.usage_tracking:
            self.usage_tracking[key] = {
                'total_cost': 0.0,
                'inference_count': 0,
                'start_date': datetime.utcnow()
            }
        
        self.usage_tracking[key]['total_cost'] += cost
        self.usage_tracking[key]['inference_count'] += 1
        
        return {
            'current_cost': cost,
            'total_cost': self.usage_tracking[key]['total_cost'],
            'remaining_budget': self._get_remaining_budget(model_name, user_id)
        }
    
    def set_budget_limit(self, scope: str, limit: float, period: str = "monthly"):
        """Set cost budget limits"""
        self.budget_limits[scope] = {
            'limit': limit,
            'period': period,
            'set_at': datetime.utcnow()
        }
    
    def _get_remaining_budget(self, model_name: str, user_id: str) -> float:
        """Get remaining budget"""
        scope = f"{model_name}:{user_id}"
        if scope in self.budget_limits:
            limit = self.budget_limits[scope]['limit']
            used = self.usage_tracking.get(scope, {}).get('total_cost', 0.0)
            return limit - used
        return float('inf')

cost_control = CostControl()
