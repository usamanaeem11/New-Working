"""
Human Override System - Allow humans to override AI decisions
Enterprise requirement: Humans must be able to override AI
"""
from typing import Dict, Optional
from datetime import datetime
from enum import Enum

class OverrideStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"

class HumanOverride:
    """Human-in-the-loop override system"""
    
    def __init__(self):
        self.override_requests = {}
        self.override_history = []
    
    def request_override(self, prediction_id: str, user_id: str,
                        ai_prediction: any, proposed_decision: any,
                        reason: str, organization_id: str) -> str:
        """Request to override AI decision"""
        import uuid
        
        override_id = f"override_{uuid.uuid4().hex}"
        
        override_request = {
            'override_id': override_id,
            'prediction_id': prediction_id,
            'requested_by': user_id,
            'organization_id': organization_id,
            'timestamp': datetime.utcnow().isoformat(),
            'ai_prediction': ai_prediction,
            'proposed_decision': proposed_decision,
            'reason': reason,
            'status': OverrideStatus.PENDING.value,
            'approver_id': None,
            'approval_timestamp': None
        }
        
        self.override_requests[override_id] = override_request
        
        # Log to audit trail
        from .ai_audit_logs import audit_logger
        audit_logger.log_event(
            event_type='override_requested',
            model_id=prediction_id,
            details=override_request
        )
        
        return override_id
    
    def approve_override(self, override_id: str, approver_id: str,
                        comments: str = "") -> Dict:
        """Approve and apply override"""
        if override_id not in self.override_requests:
            return {'error': 'Override request not found'}
        
        request = self.override_requests[override_id]
        
        if request['status'] != OverrideStatus.PENDING.value:
            return {'error': f"Override already {request['status']}"}
        
        # Apply override
        request['status'] = OverrideStatus.APPROVED.value
        request['approver_id'] = approver_id
        request['approval_timestamp'] = datetime.utcnow().isoformat()
        request['comments'] = comments
        
        # Add to history
        self.override_history.append(request)
        
        # Log to audit trail
        from .ai_audit_logs import audit_logger
        audit_logger.log_human_override(
            prediction_log_id=request['prediction_id'],
            overridden_by=approver_id,
            original_prediction=request['ai_prediction'],
            new_decision=request['proposed_decision'],
            reason=request['reason']
        )
        
        return {
            'success': True,
            'override_id': override_id,
            'applied_decision': request['proposed_decision']
        }
    
    def analyze_override_patterns(self, model_name: str, 
                                  period_days: int = 30) -> Dict:
        """Analyze why humans override AI"""
        from datetime import timedelta
        
        cutoff = datetime.utcnow() - timedelta(days=period_days)
        
        relevant_overrides = [
            o for o in self.override_history
            if datetime.fromisoformat(o['timestamp']) > cutoff
        ]
        
        if not relevant_overrides:
            return {'message': 'No overrides in period'}
        
        # Analyze patterns
        total = len(relevant_overrides)
        reasons = {}
        
        for override in relevant_overrides:
            reason = override.get('reason', 'unspecified')
            reasons[reason] = reasons.get(reason, 0) + 1
        
        return {
            'model_name': model_name,
            'period_days': period_days,
            'total_overrides': total,
            'common_reasons': sorted(reasons.items(), key=lambda x: x[1], reverse=True),
            'override_rate': total / (total + 100)  # Simplified calculation
        }

human_override = HumanOverride()
