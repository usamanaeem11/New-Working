"""
Employee Model
Employee records with full details
"""

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.session import Base

class Employee(Base):
    """
    Employee model with complete details
    """
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Personal Information
    email = Column(String(255), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(50), nullable=True)
    
    # Employment Information
    employee_number = Column(String(50), unique=True, nullable=False, index=True)
    department = Column(String(100), nullable=False, index=True)
    position = Column(String(150), nullable=False)
    employment_type = Column(String(50), default="full_time")  # full_time, part_time, contract
    
    # Compensation
    salary = Column(Float, nullable=True)
    hourly_rate = Column(Float, nullable=True)
    pay_frequency = Column(String(50), default="monthly")  # weekly, biweekly, monthly
    
    # Dates
    hire_date = Column(Date, nullable=False)
    termination_date = Column(Date, nullable=True)
    
    # Status
    status = Column(String(50), default="active", index=True)  # active, inactive, terminated
    
    # Manager
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="employees")
    time_entries = relationship("TimeEntry", back_populates="employee")
    manager = relationship("Employee", remote_side=[id], back_populates="direct_reports")
    direct_reports = relationship("Employee", back_populates="manager")
    
    def __repr__(self):
        return f"<Employee(id={self.id}, name='{self.first_name} {self.last_name}', number='{self.employee_number}')>"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
