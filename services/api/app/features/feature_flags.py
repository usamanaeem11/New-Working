"""
Feature Flags System
Progressive rollout and feature toggles
"""
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime

class RolloutStrategy(Enum):
    ALL_USERS = "all_users"
    PERCENTAGE = "percentage"
    WHITELIST = "whitelist"
    GRADUAL = "gradual"
    AB_TEST = "ab_test"

class FeatureFlags:
    """
    Feature Flag Management System
    - Progressive rollouts
    - A/B testing
    - Kill switches
    - User targeting
    """
    
    def __init__(self):
        self.flags = {}
        self.user_assignments = {}
    
    def create_flag(self, flag_name: str, description: str,
                   strategy: RolloutStrategy = RolloutStrategy.PERCENTAGE,
                   config: Dict = None) -> Dict:
        """
        Create new feature flag
        
        Args:
            flag_name: Unique flag identifier
            description: Flag description
            strategy: Rollout strategy
            config: Strategy configuration
        
        Returns:
            Flag configuration
        """
        flag = {
            'flag_name': flag_name,
            'description': description,
            'strategy': strategy.value,
            'config': config or {},
            'enabled': False,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        self.flags[flag_name] = flag
        return flag
    
    def is_enabled(self, flag_name: str, user_id: str,
                  context: Dict = None) -> bool:
        """
        Check if feature is enabled for user
        
        Args:
            flag_name: Feature flag name
            user_id: User to check
            context: Additional context (tenant, role, etc.)
        
        Returns:
            True if enabled for user
        """
        if flag_name not in self.flags:
            return False
        
        flag = self.flags[flag_name]
        
        if not flag['enabled']:
            return False
        
        strategy = RolloutStrategy(flag['strategy'])
        
        if strategy == RolloutStrategy.ALL_USERS:
            return True
        
        elif strategy == RolloutStrategy.PERCENTAGE:
            percentage = flag['config'].get('percentage', 0)
            return self._hash_user(user_id, flag_name) < percentage
        
        elif strategy == RolloutStrategy.WHITELIST:
            whitelist = flag['config'].get('whitelist', [])
            return user_id in whitelist
        
        elif strategy == RolloutStrategy.GRADUAL:
            return self._gradual_rollout_check(flag, user_id)
        
        elif strategy == RolloutStrategy.AB_TEST:
            return self._ab_test_assignment(flag, user_id, context)
        
        return False
    
    def enable_flag(self, flag_name: str, strategy_config: Dict = None):
        """Enable feature flag"""
        if flag_name in self.flags:
            self.flags[flag_name]['enabled'] = True
            if strategy_config:
                self.flags[flag_name]['config'].update(strategy_config)
            self.flags[flag_name]['updated_at'] = datetime.utcnow().isoformat()
    
    def disable_flag(self, flag_name: str):
        """Disable feature flag (kill switch)"""
        if flag_name in self.flags:
            self.flags[flag_name]['enabled'] = False
            self.flags[flag_name]['updated_at'] = datetime.utcnow().isoformat()
    
    def gradual_rollout(self, flag_name: str, target_percentage: int,
                       step_percentage: int = 10, 
                       interval_hours: int = 24):
        """
        Gradually increase rollout percentage
        
        Args:
            flag_name: Feature to roll out
            target_percentage: Final target percentage
            step_percentage: Increment per step
            interval_hours: Hours between increments
        """
        if flag_name not in self.flags:
            return
        
        self.flags[flag_name]['config']['gradual_rollout'] = {
            'current_percentage': 0,
            'target_percentage': target_percentage,
            'step_percentage': step_percentage,
            'interval_hours': interval_hours,
            'started_at': datetime.utcnow().isoformat()
        }
    
    def _hash_user(self, user_id: str, flag_name: str) -> int:
        """Hash user ID to percentage (0-100)"""
        import hashlib
        combined = f"{user_id}:{flag_name}"
        hash_value = int(hashlib.md5(combined.encode()).hexdigest(), 16)
        return hash_value % 100
    
    def _gradual_rollout_check(self, flag: Dict, user_id: str) -> bool:
        """Check gradual rollout eligibility"""
        rollout_config = flag['config'].get('gradual_rollout', {})
        current_percentage = rollout_config.get('current_percentage', 0)
        return self._hash_user(user_id, flag['flag_name']) < current_percentage
    
    def _ab_test_assignment(self, flag: Dict, user_id: str, 
                           context: Dict) -> bool:
        """Assign user to A/B test variant"""
        # 50/50 split by default
        return self._hash_user(user_id, flag['flag_name']) < 50
    
    def get_flag_status(self, flag_name: str) -> Dict:
        """Get flag status and statistics"""
        if flag_name not in self.flags:
            return None
        
        flag = self.flags[flag_name]
        
        return {
            'flag_name': flag_name,
            'enabled': flag['enabled'],
            'strategy': flag['strategy'],
            'config': flag['config'],
            'total_users_enabled': self._count_enabled_users(flag_name)
        }
    
    def _count_enabled_users(self, flag_name: str) -> int:
        """Count users with flag enabled"""
        # In production: query actual usage data
        return 0

feature_flags = FeatureFlags()
