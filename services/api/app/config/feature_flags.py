"""
Feature Flags System
Enable/disable features without deployment
"""

from typing import Dict, Any
import os
import json
import logging

logger = logging.getLogger(__name__)

class FeatureFlags:
    """
    Centralized feature flag management
    """
    
    def __init__(self):
        self.flags = self._load_flags()
    
    def _load_flags(self) -> Dict[str, Any]:
        """
        Load feature flags from environment or config file
        """
        # Default flags
        default_flags = {
            # Core features
            'authentication_enabled': True,
            'rbac_enforcement': True,
            'rate_limiting': True,
            
            # AI features
            'ai_enabled': True,
            'ai_performance_predictor': True,
            'ai_turnover_predictor': True,
            'ai_drift_detection': True,
            
            # Advanced features
            'background_jobs': True,
            'real_time_updates': True,
            'offline_mode': True,
            
            # Experimental
            'advanced_analytics': False,
            'ml_auto_training': False,
            
            # Maintenance
            'maintenance_mode': False,
            'read_only_mode': False,
        }
        
        # Override from environment
        env_flags = os.getenv('FEATURE_FLAGS')
        if env_flags:
            try:
                override = json.loads(env_flags)
                default_flags.update(override)
                logger.info(f"Feature flags overridden from environment")
            except json.JSONDecodeError:
                logger.error("Invalid FEATURE_FLAGS JSON in environment")
        
        return default_flags
    
    def is_enabled(self, flag_name: str) -> bool:
        """
        Check if feature is enabled
        
        Args:
            flag_name: Name of the feature flag
            
        Returns:
            True if enabled, False otherwise
        """
        return self.flags.get(flag_name, False)
    
    def enable(self, flag_name: str):
        """Enable a feature flag"""
        self.flags[flag_name] = True
        logger.info(f"Feature flag enabled: {flag_name}")
    
    def disable(self, flag_name: str):
        """Disable a feature flag"""
        self.flags[flag_name] = False
        logger.info(f"Feature flag disabled: {flag_name}")
    
    def get_all(self) -> Dict[str, Any]:
        """Get all feature flags"""
        return self.flags.copy()
    
    def set_maintenance_mode(self, enabled: bool):
        """Enable/disable maintenance mode"""
        self.flags['maintenance_mode'] = enabled
        logger.warning(f"Maintenance mode: {'ENABLED' if enabled else 'DISABLED'}")

# Global instance
feature_flags = FeatureFlags()

def require_feature(flag_name: str):
    """
    Decorator to require a feature flag
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            if not feature_flags.is_enabled(flag_name):
                from fastapi import HTTPException, status
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Feature not available: {flag_name}"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator
