"""
Settings Model
System and tenant settings
"""

from sqlalchemy import Column, Integer, String, Boolean, JSON, DateTime, ForeignKey
from datetime import datetime

from app.database.session import Base

class Setting(Base):
    """System and tenant settings"""
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Setting identification
    category = Column(String(100), nullable=False, index=True)  # system, company, email, etc
    key = Column(String(100), nullable=False, index=True)
    
    # Value (stored as JSON for flexibility)
    value = Column(JSON, nullable=False)
    
    # Metadata
    description = Column(String(255), nullable=True)
    is_public = Column(Boolean, default=False)  # Can users see this?
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    def __repr__(self):
        return f"<Setting(category='{self.category}', key='{self.key}')>"

class FeatureFlag(Base):
    """Feature flags for A/B testing and gradual rollouts"""
    __tablename__ = "feature_flags"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True, index=True)  # NULL = global
    
    # Flag identification
    name = Column(String(100), nullable=False, unique=True, index=True)
    
    # Status
    enabled = Column(Boolean, default=False)
    
    # Rollout percentage (0-100)
    rollout_percentage = Column(Integer, default=100)
    
    # Metadata
    description = Column(String(255), nullable=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<FeatureFlag(name='{self.name}', enabled={self.enabled})>"
