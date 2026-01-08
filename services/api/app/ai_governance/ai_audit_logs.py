"""
AI Audit Logger - Immutable audit trail for all AI decisions
Enterprise requirement: Full traceability of AI decisions
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib
import json
import logging

logger = logging.getLogger(__name__)

class AIAuditLogger:
    """Immutable audit logging for AI decisions and operations"""
    
    def __init__(self):
        self.log_storage = []  # In production, this would be a database
        self.log_hash_chain = []  # Blockchain-like integrity verification
    
    def log_prediction(self, model_name: str, model_version: str,
                      input_data: Dict, prediction: Any, confidence: float,
                      user_id: str, organization_id: str,
                      decision_context: Dict = None) -> str:
        """Log every AI prediction with full context"""
        
        log_entry = {
            'log_id': self._generate_log_id(),
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'prediction',
            'model_name': model_name,
            'model_version': model_version,
            'input_data': self._sanitize_sensitive_data(input_data),
            'prediction': prediction,
            'confidence': confidence,
            'user_id': user_id,
            'organization_id': organization_id,
            'decision_context': decision_context or {},
            'environment': self._get_environment_info()
        }
        
        # Calculate hash for integrity
        log_entry['hash'] = self._calculate_hash(log_entry)
        log_entry['previous_hash'] = self._get_previous_hash()
        
        # Store log
        self._store_log(log_entry)
        
        return log_entry['log_id']
    
    def log_human_override(self, prediction_log_id: str, overridden_by: str,
                          original_prediction: Any, new_decision: Any,
                          reason: str, approval_required: bool = False) -> str:
        """Log when human overrides AI decision"""
        
        log_entry = {
            'log_id': self._generate_log_id(),
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'human_override',
            'original_prediction_id': prediction_log_id,
            'overridden_by': overridden_by,
            'original_prediction': original_prediction,
            'new_decision': new_decision,
            'reason': reason,
            'approval_required': approval_required,
            'approval_status': 'pending' if approval_required else 'approved'
        }
        
        log_entry['hash'] = self._calculate_hash(log_entry)
        log_entry['previous_hash'] = self._get_previous_hash()
        
        self._store_log(log_entry)
        
        logger.info(f"Human override logged: {prediction_log_id} by {overridden_by}")
        
        return log_entry['log_id']
    
    def log_model_update(self, model_name: str, old_version: str,
                        new_version: str, updated_by: str,
                        changes: List[str], reason: str) -> str:
        """Log model version changes"""
        
        log_entry = {
            'log_id': self._generate_log_id(),
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'model_update',
            'model_name': model_name,
            'old_version': old_version,
            'new_version': new_version,
            'updated_by': updated_by,
            'changes': changes,
            'reason': reason
        }
        
        log_entry['hash'] = self._calculate_hash(log_entry)
        log_entry['previous_hash'] = self._get_previous_hash()
        
        self._store_log(log_entry)
        
        return log_entry['log_id']
    
    def log_event(self, event_type: str, model_id: str = None, 
                 use_case: str = None, details: Dict = None) -> str:
        """Log generic AI governance event"""
        
        log_entry = {
            'log_id': self._generate_log_id(),
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'model_id': model_id,
            'use_case': use_case,
            'details': details or {}
        }
        
        log_entry['hash'] = self._calculate_hash(log_entry)
        log_entry['previous_hash'] = self._get_previous_hash()
        
        self._store_log(log_entry)
        
        return log_entry['log_id']
    
    def log_bias_alert(self, model_name: str, bias_report: Dict,
                      severity: str) -> str:
        """Log bias detection alert"""
        
        log_entry = {
            'log_id': self._generate_log_id(),
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'bias_alert',
            'model_name': model_name,
            'bias_report': bias_report,
            'severity': severity,
            'requires_action': True
        }
        
        log_entry['hash'] = self._calculate_hash(log_entry)
        log_entry['previous_hash'] = self._get_previous_hash()
        
        self._store_log(log_entry)
        
        return log_entry['log_id']
    
    def query_audit_trail(self, filters: Dict, limit: int = 100) -> List[Dict]:
        """Query audit logs for compliance"""
        
        results = []
        
        for log in reversed(self.log_storage):  # Most recent first
            if self._matches_filters(log, filters):
                results.append(log)
                
                if len(results) >= limit:
                    break
        
        return results
    
    def verify_log_integrity(self, log_id: str = None) -> Dict:
        """Verify integrity of audit logs"""
        
        if log_id:
            # Verify specific log
            log = self._find_log(log_id)
            if not log:
                return {'valid': False, 'error': 'Log not found'}
            
            recalculated_hash = self._calculate_hash({
                k: v for k, v in log.items() 
                if k not in ['hash', 'previous_hash']
            })
            
            return {
                'valid': recalculated_hash == log['hash'],
                'log_id': log_id,
                'stored_hash': log['hash'],
                'calculated_hash': recalculated_hash
            }
        
        else:
            # Verify entire chain
            for i, log in enumerate(self.log_storage):
                if i > 0:
                    # Check if previous_hash matches
                    if log['previous_hash'] != self.log_storage[i-1]['hash']:
                        return {
                            'valid': False,
                            'error': f'Chain broken at log {log["log_id"]}',
                            'position': i
                        }
            
            return {'valid': True, 'logs_verified': len(self.log_storage)}
    
    def generate_compliance_report(self, organization_id: str,
                                   start_date: datetime, 
                                   end_date: datetime) -> Dict:
        """Generate compliance report for audit"""
        
        filters = {
            'organization_id': organization_id,
            'start_date': start_date,
            'end_date': end_date
        }
        
        logs = self.query_audit_trail(filters, limit=100000)
        
        # Aggregate statistics
        report = {
            'organization_id': organization_id,
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'total_predictions': sum(1 for l in logs if l['event_type'] == 'prediction'),
            'human_overrides': sum(1 for l in logs if l['event_type'] == 'human_override'),
            'bias_alerts': sum(1 for l in logs if l['event_type'] == 'bias_alert'),
            'model_updates': sum(1 for l in logs if l['event_type'] == 'model_update'),
            'models_used': list(set(l.get('model_name') for l in logs if 'model_name' in l)),
            'override_rate': 0.0
        }
        
        # Calculate override rate
        if report['total_predictions'] > 0:
            report['override_rate'] = report['human_overrides'] / report['total_predictions']
        
        return report
    
    def _generate_log_id(self) -> str:
        """Generate unique log ID"""
        import uuid
        return f"ai_log_{uuid.uuid4().hex}"
    
    def _calculate_hash(self, data: Dict) -> str:
        """Calculate hash for integrity verification"""
        # Remove hash fields if present
        data_to_hash = {k: v for k, v in data.items() if k not in ['hash', 'previous_hash']}
        
        # Serialize to JSON (sorted for consistency)
        json_str = json.dumps(data_to_hash, sort_keys=True)
        
        # Calculate SHA-256 hash
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def _get_previous_hash(self) -> Optional[str]:
        """Get hash of previous log entry"""
        if self.log_storage:
            return self.log_storage[-1]['hash']
        return None
    
    def _store_log(self, log_entry: Dict):
        """Store log entry (immutable)"""
        # In production, this would write to:
        # 1. Primary database (PostgreSQL with append-only table)
        # 2. Long-term storage (S3 with Object Lock)
        # 3. Optionally: Blockchain for additional verification
        
        self.log_storage.append(log_entry)
        self.log_hash_chain.append(log_entry['hash'])
        
        logger.debug(f"AI audit log stored: {log_entry['log_id']}")
    
    def _sanitize_sensitive_data(self, data: Dict) -> Dict:
        """Remove or mask sensitive data from logs"""
        sanitized = {}
        
        sensitive_fields = [
            'password', 'ssn', 'tax_id', 'bank_account', 
            'credit_card', 'api_key', 'secret', 'token'
        ]
        
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_fields):
                sanitized[key] = '[REDACTED]'
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _get_environment_info(self) -> Dict:
        """Get environment information for context"""
        import socket
        import platform
        
        return {
            'hostname': socket.gethostname(),
            'platform': platform.system(),
            'python_version': platform.python_version()
        }
    
    def _matches_filters(self, log: Dict, filters: Dict) -> bool:
        """Check if log matches filter criteria"""
        for key, value in filters.items():
            if key == 'start_date':
                log_time = datetime.fromisoformat(log['timestamp'])
                if log_time < value:
                    return False
            
            elif key == 'end_date':
                log_time = datetime.fromisoformat(log['timestamp'])
                if log_time > value:
                    return False
            
            elif key in log:
                if log[key] != value:
                    return False
        
        return True
    
    def _find_log(self, log_id: str) -> Optional[Dict]:
        """Find log by ID"""
        for log in self.log_storage:
            if log['log_id'] == log_id:
                return log
        return None

# Global audit logger instance
audit_logger = AIAuditLogger()
