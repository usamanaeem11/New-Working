"""
AI Kill Switch - Emergency shutdown of AI models
Enterprise requirement: Ability to immediately disable problematic models
"""
from typing import Dict
from datetime import datetime
from enum import Enum

class KillSwitchStatus(Enum):
    ACTIVE = "active"
    DISABLED = "disabled"
    EMERGENCY_STOP = "emergency_stop"

class AIKillSwitch:
    """Emergency shutdown for AI models"""
    
    def __init__(self):
        self.model_status = {}
        self.kill_switch_events = []
    
    def disable_model(self, model_name: str, reason: str,
                     disabled_by: str, severity: str = "high") -> Dict:
        """Immediately disable AI model"""
        
        event = {
            'model_name': model_name,
            'action': 'disabled',
            'reason': reason,
            'disabled_by': disabled_by,
            'severity': severity,
            'timestamp': datetime.utcnow().isoformat(),
            'fallback_activated': True
        }
        
        # Update model status
        self.model_status[model_name] = KillSwitchStatus.DISABLED.value
        
        # Log event
        self.kill_switch_events.append(event)
        
        # Activate fallback
        from .fallback_handler import fallback_handler
        fallback_handler.register_fallback(
            use_case=model_name,
            strategy=fallback_handler.FallbackStrategy.MANUAL_REVIEW
        )
        
        # Log to audit
        from .ai_audit_logs import audit_logger
        audit_logger.log_event(
            event_type='kill_switch_activated',
            model_id=model_name,
            details=event
        )
        
        return {'success': True, 'model_disabled': model_name}
    
    def enable_model(self, model_name: str, enabled_by: str,
                    verification: Dict) -> Dict:
        """Re-enable model after fix"""
        
        if not verification.get('fix_verified'):
            return {'error': 'Fix must be verified before re-enabling'}
        
        event = {
            'model_name': model_name,
            'action': 'enabled',
            'enabled_by': enabled_by,
            'verification': verification,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.model_status[model_name] = KillSwitchStatus.ACTIVE.value
        self.kill_switch_events.append(event)
        
        from .ai_audit_logs import audit_logger
        audit_logger.log_event(
            event_type='model_reactivated',
            model_id=model_name,
            details=event
        )
        
        return {'success': True, 'model_enabled': model_name}
    
    def is_model_enabled(self, model_name: str) -> bool:
        """Check if model is enabled"""
        status = self.model_status.get(model_name, KillSwitchStatus.ACTIVE.value)
        return status == KillSwitchStatus.ACTIVE.value

kill_switch = AIKillSwitch()
