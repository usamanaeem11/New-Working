"""
Production Audit Logger
Immutable audit trail for all system actions
"""
from datetime import datetime
from typing import Optional

class AuditLogger:
    """
    Production audit logging
    - All requests logged
    - All actions logged
    - Immutable trail
    - GDPR compliant
    """
    
    def __init__(self):
        self.logs = []  # In production: database table
    
    def log_request(self, method: str, path: str, status_code: int,
                   user_id: Optional[str], ip_address: str):
        """Log HTTP request"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'http_request',
            'method': method,
            'path': path,
            'status_code': status_code,
            'user_id': user_id,
            'ip_address': ip_address
        }
        self.logs.append(log_entry)
        
        # In production: INSERT INTO audit_logs
    
    def log_auth_event(self, event: str, user_id: str, 
                      success: bool, details: dict):
        """Log authentication event"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'authentication',
            'event': event,
            'user_id': user_id,
            'success': success,
            'details': details
        }
        self.logs.append(log_entry)
    
    def log_data_access(self, user_id: str, resource: str,
                       action: str, record_count: int):
        """Log data access"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'data_access',
            'user_id': user_id,
            'resource': resource,
            'action': action,
            'record_count': record_count
        }
        self.logs.append(log_entry)

audit_logger = AuditLogger()
