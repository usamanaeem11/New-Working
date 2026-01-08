"""
Tenant Model
Multi-tenant architecture
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.session import Base

class Tenant(Base):
    """
    Tenant model for multi-tenant architecture
    Each company/organization is a tenant
    """
    __tablename__ = "tenants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), unique=True, nullable=False, index=True)
    status = Column(String(50), default="active")  # active, suspended, trial
    
    # Subscription
    plan = Column(String(50), default="basic")  # basic, professional, enterprise
    max_employees = Column(Integer, default=50)
    
    # Settings
    timezone = Column(String(50), default="UTC")
    work_week_start = Column(String(20), default="Monday")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    trial_ends_at = Column(DateTime, nullable=True)
    
    # Relationships
    users = relationship("User", back_populates="tenant")
    employees = relationship("Employee", back_populates="tenant")
    
    def __repr__(self):
        return f"<Tenant(id={self.id}, name='{self.name}', domain='{self.domain}')>"
