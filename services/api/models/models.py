"""
Audit Log Database Models
Supports partitioned tables for high-volume logging
"""
from sqlalchemy import Column, String, Integer, DateTime, UUID, Index, Text
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class AuditLog(Base):
    """
    Comprehensive audit log model
    
    Features:
    - Partitioned by month for performance
    - Captures full request/response details
    - Tracks data changes (before/after)
    - Sanitizes sensitive information
    - Supports forensic investigations
    """
    
    __tablename__ = "audit_logs"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), index=True)
    session_id = Column(UUID(as_uuid=True))
    
    # Action details
    action = Column(String(100), nullable=False, index=True)  # e.g., USER_LOGIN, PROJECT_CREATE
    resource_type = Column(String(50))  # e.g., user, project, task
    resource_id = Column(UUID(as_uuid=True))
    
    # Request context
    ip_address = Column(INET)
    user_agent = Column(Text)
    request_method = Column(String(10))  # GET, POST, PUT, DELETE
    request_path = Column(Text)
    request_body = Column(JSONB)  # Sanitized request payload
    
    # Response details
    status_code = Column(Integer)
    response_time_ms = Column(Integer)
    
    # Change tracking
    changes = Column(JSONB)  # {before: {...}, after: {...}}
    
    # Additional metadata
    metadata = Column(JSONB)
    
    # Timestamp (used for partitioning)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('idx_audit_tenant_date', 'tenant_id', 'created_at'),
        Index('idx_audit_user_date', 'user_id', 'created_at'),
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
        Index('idx_audit_action_date', 'action', 'created_at'),
    )
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': str(self.id),
            'tenant_id': str(self.tenant_id),
            'user_id': str(self.user_id) if self.user_id else None,
            'session_id': str(self.session_id) if self.session_id else None,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': str(self.resource_id) if self.resource_id else None,
            'ip_address': str(self.ip_address) if self.ip_address else None,
            'user_agent': self.user_agent,
            'request_method': self.request_method,
            'request_path': self.request_path,
            'status_code': self.status_code,
            'response_time_ms': self.response_time_ms,
            'changes': self.changes,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<AuditLog(action={self.action}, user_id={self.user_id}, created_at={self.created_at})>"
