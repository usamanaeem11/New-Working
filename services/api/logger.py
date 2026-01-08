"""
Centralized Audit Logger
Enterprise-grade activity tracking
"""
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from .models import AuditLog
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AuditLogger:
    """Production-ready audit logging system"""
    
    def __init__(self, db: Session):
        self.db = db
        self.sensitive_fields = {
            'password', 'token', 'secret', 'ssn', 'tax_id', 
            'bank_account', 'credit_card', 'api_key'
        }
    
    def log(self, tenant_id: str, action: str, **kwargs) -> Optional[AuditLog]:
        """Log auditable action with automatic sanitization"""
        try:
            # Sanitize request body
            if 'request_body' in kwargs:
                kwargs['request_body'] = self._sanitize(kwargs['request_body'])
            
            entry = AuditLog(
                tenant_id=tenant_id,
                action=action,
                **kwargs
            )
            
            self.db.add(entry)
            self.db.commit()
            
            logger.info(f"AUDIT: {action}", extra={
                'tenant_id': tenant_id,
                'user_id': kwargs.get('user_id'),
                'action': action
            })
            
            return entry
        except Exception as e:
            logger.error(f"Audit log failed: {e}")
            self.db.rollback()
            return None
    
    def _sanitize(self, data: Dict) -> Dict:
        """Remove sensitive fields"""
        if not isinstance(data, dict):
            return data
        
        sanitized = {}
        for key, value in data.items():
            if key.lower() in self.sensitive_fields:
                sanitized[key] = '[REDACTED]'
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize(value)
            else:
                sanitized[key] = value
        return sanitized
