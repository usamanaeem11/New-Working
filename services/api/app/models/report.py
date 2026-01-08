"""
Report Model
Generated reports with metadata
"""

from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.session import Base

class Report(Base):
    """Generated report model"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Report info
    report_type = Column(String(100), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    
    # Date range
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Data
    data = Column(JSON, nullable=False)
    
    # Metadata
    generated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(50), default="completed")
    format = Column(String(20), default="json")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<Report(id={self.id}, type='{self.report_type}', period={self.start_date} to {self.end_date})>"
