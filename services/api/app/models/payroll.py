"""
Payroll Model
Payroll run records
"""

from sqlalchemy import Column, Integer, Float, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.session import Base

class PayrollRun(Base):
    """Payroll run model"""
    __tablename__ = "payroll_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Pay period
    pay_period_start = Column(Date, nullable=False)
    pay_period_end = Column(Date, nullable=False)
    pay_date = Column(Date, nullable=False)
    
    # Status
    status = Column(String(50), default="draft", index=True)  # draft, processing, completed, failed
    
    # Totals
    total_amount = Column(Float, default=0.0)
    total_hours = Column(Float, default=0.0)
    employee_count = Column(Integer, default=0)
    
    # Processing
    processed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    processed_at = Column(DateTime, nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    pay_stubs = relationship("PayStub", back_populates="payroll_run")
    
    def __repr__(self):
        return f"<PayrollRun(id={self.id}, period={self.pay_period_start} to {self.pay_period_end}, status='{self.status}')>"

class PayStub(Base):
    """Individual employee pay stub"""
    __tablename__ = "pay_stubs"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    payroll_run_id = Column(Integer, ForeignKey("payroll_runs.id"), nullable=False, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    
    # Hours
    regular_hours = Column(Float, default=0.0)
    overtime_hours = Column(Float, default=0.0)
    total_hours = Column(Float, default=0.0)
    
    # Pay
    regular_pay = Column(Float, default=0.0)
    overtime_pay = Column(Float, default=0.0)
    gross_pay = Column(Float, default=0.0)
    
    # Deductions
    tax_federal = Column(Float, default=0.0)
    tax_state = Column(Float, default=0.0)
    tax_social_security = Column(Float, default=0.0)
    tax_medicare = Column(Float, default=0.0)
    deductions_other = Column(Float, default=0.0)
    total_deductions = Column(Float, default=0.0)
    
    # Net
    net_pay = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    payroll_run = relationship("PayrollRun", back_populates="pay_stubs")
    employee = relationship("Employee")
    
    def __repr__(self):
        return f"<PayStub(id={self.id}, employee_id={self.employee_id}, net_pay={self.net_pay})>"
