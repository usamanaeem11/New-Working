"""
Time Entry Model
Time tracking records
"""

from sqlalchemy import Column, Integer, Float, DateTime, Date, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.session import Base

class TimeEntry(Base):
    """
    Time entry model for tracking work hours
    """
    __tablename__ = "time_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    
    # Time Information
    date = Column(Date, nullable=False, index=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    
    # Hours
    hours = Column(Float, nullable=True)
    overtime_hours = Column(Float, default=0.0)
    
    # Break time (in minutes)
    break_minutes = Column(Integer, default=0)
    
    # Status
    status = Column(String(50), default="active", index=True)  # active, completed, approved, rejected
    
    # Approval
    approved_by = Column(Integer, ForeignKey("employees.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Location (if using geofencing)
    clock_in_location = Column(String(255), nullable=True)
    clock_out_location = Column(String(255), nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="time_entries")
    approver = relationship("Employee", foreign_keys=[approved_by])
    
    def __repr__(self):
        return f"<TimeEntry(id={self.id}, employee_id={self.employee_id}, date='{self.date}', hours={self.hours})>"
    
    def calculate_hours(self):
        """Calculate hours from start and end time"""
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            hours = duration.total_seconds() / 3600
            # Subtract break time
            hours -= (self.break_minutes / 60)
            return round(hours, 2)
        return 0.0
