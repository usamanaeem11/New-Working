"""
Zero-Trust Security Architecture
Never trust, always verify - Enterprise security model
"""
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import secrets

class TrustLevel(Enum):
    UNTRUSTED = 0
    BASIC = 1
    VERIFIED = 2
    ELEVATED = 3
    PRIVILEGED = 4

class DevicePosture(Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    UNKNOWN = "unknown"

class ZeroTrustEngine:
    """
    Zero-Trust Security Implementation
    - Verify every access request
    - Assume breach
    - Least privilege access
    - Continuous validation
    """
    
    def __init__(self):
        self.trust_scores = {}
        self.device_registry = {}
        self.access_policies = {}
        self.continuous_validation_interval = timedelta(minutes=15)
    
    def evaluate_access_request(self, user_id: str, resource: str,
                                action: str, context: Dict) -> Dict:
        """
        Zero-Trust Access Evaluation
        Every request must be validated regardless of previous authentication
        """
        
        # Step 1: Identity Verification
        identity_score = self._verify_identity(user_id, context)
        
        # Step 2: Device Posture Check
        device_score = self._check_device_posture(context.get('device_id'))
        
        # Step 3: Context Analysis
        context_score = self._analyze_context(user_id, context)
        
        # Step 4: Resource Sensitivity
        resource_sensitivity = self._get_resource_sensitivity(resource)
        
        # Step 5: Calculate Trust Score
        trust_score = self._calculate_trust_score(
            identity_score, device_score, context_score
        )
        
        # Step 6: Policy Evaluation
        required_trust = self._get_required_trust_level(resource, action)
        
        # Step 7: Make Decision
        decision = self._make_access_decision(
            trust_score, required_trust, resource_sensitivity
        )
        
        # Step 8: Log Decision
        self._log_access_decision(user_id, resource, action, decision, trust_score)
        
        return decision
    
    def _verify_identity(self, user_id: str, context: Dict) -> float:
        """Verify user identity strength"""
        score = 0.0
        
        # MFA present?
        if context.get('mfa_verified'):
            score += 0.4
        
        # Biometric verification?
        if context.get('biometric_verified'):
            score += 0.3
        
        # Certificate-based auth?
        if context.get('cert_verified'):
            score += 0.3
        
        # Recent password change?
        password_age = context.get('password_age_days', 999)
        if password_age < 90:
            score += 0.0
        else:
            score -= 0.1  # Penalty for old passwords
        
        return max(0.0, min(1.0, score))
    
    def _check_device_posture(self, device_id: Optional[str]) -> float:
        """Check device security posture"""
        if not device_id:
            return 0.0
        
        if device_id not in self.device_registry:
            # Unknown device - very low trust
            return 0.2
        
        device = self.device_registry[device_id]
        score = 0.0
        
        # Managed device?
        if device.get('managed'):
            score += 0.3
        
        # OS up to date?
        if device.get('os_patched'):
            score += 0.2
        
        # Antivirus active?
        if device.get('av_active'):
            score += 0.2
        
        # Encryption enabled?
        if device.get('disk_encrypted'):
            score += 0.2
        
        # Screen lock enabled?
        if device.get('screen_lock'):
            score += 0.1
        
        return min(1.0, score)
    
    def _analyze_context(self, user_id: str, context: Dict) -> float:
        """Analyze request context for anomalies"""
        score = 1.0
        
        # Check location
        location = context.get('location')
        if location:
            if self._is_anomalous_location(user_id, location):
                score -= 0.3
        
        # Check time
        request_time = context.get('timestamp', datetime.utcnow())
        if self._is_anomalous_time(user_id, request_time):
            score -= 0.2
        
        # Check IP reputation
        ip_address = context.get('ip_address')
        if ip_address:
            if self._is_suspicious_ip(ip_address):
                score -= 0.4
        
        # Check velocity (rapid requests)
        if self._detect_impossible_travel(user_id, context):
            score -= 0.5
        
        return max(0.0, score)
    
    def _get_resource_sensitivity(self, resource: str) -> str:
        """Determine resource sensitivity level"""
        # High sensitivity: payroll, PII, financial
        high_sensitivity = ['payroll', 'salary', 'ssn', 'bank', 'financial']
        if any(s in resource.lower() for s in high_sensitivity):
            return 'high'
        
        # Medium: employee data, performance
        medium_sensitivity = ['employee', 'performance', 'review']
        if any(s in resource.lower() for s in medium_sensitivity):
            return 'medium'
        
        # Low: public data, reports
        return 'low'
    
    def _calculate_trust_score(self, identity: float, device: float, 
                               context: float) -> float:
        """Calculate overall trust score"""
        # Weighted average
        return (identity * 0.4 + device * 0.3 + context * 0.3)
    
    def _get_required_trust_level(self, resource: str, action: str) -> float:
        """Get required trust level for resource/action"""
        sensitivity = self._get_resource_sensitivity(resource)
        
        # Base requirements by sensitivity
        base_requirements = {
            'high': 0.85,
            'medium': 0.70,
            'low': 0.50
        }
        
        base = base_requirements.get(sensitivity, 0.70)
        
        # Modify based on action
        if action in ['delete', 'modify', 'export']:
            base += 0.10
        
        return min(1.0, base)
    
    def _make_access_decision(self, trust_score: float, 
                             required_trust: float,
                             sensitivity: str) -> Dict:
        """Make final access decision"""
        
        if trust_score >= required_trust:
            return {
                'allowed': True,
                'trust_score': trust_score,
                'required_trust': required_trust,
                'step_up_required': False
            }
        
        # Check if step-up auth can help
        if trust_score >= (required_trust - 0.15):
            return {
                'allowed': False,
                'trust_score': trust_score,
                'required_trust': required_trust,
                'step_up_required': True,
                'step_up_method': 'mfa'
            }
        
        # Deny
        return {
            'allowed': False,
            'trust_score': trust_score,
            'required_trust': required_trust,
            'step_up_required': False,
            'reason': 'insufficient_trust'
        }
    
    def _log_access_decision(self, user_id: str, resource: str,
                            action: str, decision: Dict, 
                            trust_score: float):
        """Log all access decisions for audit"""
        from ..ai_governance.ai_audit_logs import audit_logger
        
        audit_logger.log_event(
            event_type='zero_trust_access',
            model_id=f"user:{user_id}",
            details={
                'resource': resource,
                'action': action,
                'decision': decision,
                'trust_score': trust_score,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    
    def register_device(self, device_id: str, device_info: Dict):
        """Register device in zero-trust system"""
        self.device_registry[device_id] = {
            'device_id': device_id,
            'registered_at': datetime.utcnow(),
            'managed': device_info.get('managed', False),
            'os_patched': device_info.get('os_patched', False),
            'av_active': device_info.get('av_active', False),
            'disk_encrypted': device_info.get('disk_encrypted', False),
            'screen_lock': device_info.get('screen_lock', False),
            'last_check': datetime.utcnow()
        }
    
    def continuous_validation(self, user_id: str, session_id: str) -> bool:
        """Continuously validate active sessions"""
        # In production: check device posture, location, behavior
        # Re-evaluate trust score periodically
        return True
    
    def _is_anomalous_location(self, user_id: str, location: str) -> bool:
        """Check if location is anomalous for user"""
        # Implementation: check historical locations
        return False
    
    def _is_anomalous_time(self, user_id: str, time: datetime) -> bool:
        """Check if access time is anomalous"""
        # Implementation: check historical access patterns
        return False
    
    def _is_suspicious_ip(self, ip_address: str) -> bool:
        """Check IP reputation"""
        # Implementation: check against threat intel feeds
        return False
    
    def _detect_impossible_travel(self, user_id: str, context: Dict) -> bool:
        """Detect impossible travel (locations too far apart in time)"""
        # Implementation: check if user could physically travel between locations
        return False

# Global zero-trust engine
zero_trust = ZeroTrustEngine()
