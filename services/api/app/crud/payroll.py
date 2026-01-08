"""
Payroll CRUD Operations
Real payroll processing and calculations
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional
from datetime import date

from app.models.payroll import PayrollRun, PayStub
from app.models.employee import Employee
from app.crud import time_entry as time_crud

def create_payroll_run(
    db: Session,
    tenant_id: int,
    pay_period_start: date,
    pay_period_end: date,
    pay_date: date,
    processed_by: int
) -> PayrollRun:
    """
    Create and process payroll run
    Real calculations based on time entries
    """
    
    # Create payroll run
    payroll_run = PayrollRun(
        tenant_id=tenant_id,
        pay_period_start=pay_period_start,
        pay_period_end=pay_period_end,
        pay_date=pay_date,
        processed_by=processed_by,
        status='processing'
    )
    db.add(payroll_run)
    db.flush()  # Get ID
    
    # Get all active employees
    employees = db.query(Employee).filter(
        and_(
            Employee.tenant_id == tenant_id,
            Employee.status == 'active'
        )
    ).all()
    
    total_amount = 0.0
    total_hours = 0.0
    employee_count = 0
    
    # Process each employee
    for employee in employees:
        # Get time entries for period
        entries = time_crud.get_time_entries(
            db=db,
            employee_id=employee.id,
            tenant_id=tenant_id,
            start_date=pay_period_start,
            end_date=pay_period_end,
            status='approved'
        )
        
        # Calculate hours
        regular_hours = 0.0
        overtime_hours = 0.0
        
        for entry in entries:
            if entry.hours:
                regular_hours += min(entry.hours, 8.0)
                if entry.hours > 8.0:
                    overtime_hours += entry.hours - 8.0
        
        total_hours_employee = regular_hours + overtime_hours
        
        # Skip if no hours
        if total_hours_employee == 0:
            continue
        
        # Calculate pay
        hourly_rate = employee.hourly_rate or 0.0
        if employee.salary and employee.pay_frequency == 'monthly':
            # Salaried: calculate hourly rate
            hourly_rate = employee.salary / 160  # ~40 hours/week * 4 weeks
        
        regular_pay = regular_hours * hourly_rate
        overtime_pay = overtime_hours * hourly_rate * 1.5  # Time and a half
        gross_pay = regular_pay + overtime_pay
        
        # Calculate deductions (simplified)
        tax_federal = gross_pay * 0.12  # 12% federal
        tax_state = gross_pay * 0.05    # 5% state
        tax_social_security = gross_pay * 0.062  # 6.2%
        tax_medicare = gross_pay * 0.0145  # 1.45%
        total_deductions = tax_federal + tax_state + tax_social_security + tax_medicare
        
        net_pay = gross_pay - total_deductions
        
        # Create pay stub
        pay_stub = PayStub(
            tenant_id=tenant_id,
            payroll_run_id=payroll_run.id,
            employee_id=employee.id,
            regular_hours=regular_hours,
            overtime_hours=overtime_hours,
            total_hours=total_hours_employee,
            regular_pay=regular_pay,
            overtime_pay=overtime_pay,
            gross_pay=gross_pay,
            tax_federal=tax_federal,
            tax_state=tax_state,
            tax_social_security=tax_social_security,
            tax_medicare=tax_medicare,
            total_deductions=total_deductions,
            net_pay=net_pay
        )
        db.add(pay_stub)
        
        total_amount += net_pay
        total_hours += total_hours_employee
        employee_count += 1
    
    # Update payroll run totals
    payroll_run.total_amount = total_amount
    payroll_run.total_hours = total_hours
    payroll_run.employee_count = employee_count
    payroll_run.status = 'completed'
    
    db.commit()
    db.refresh(payroll_run)
    
    return payroll_run

def get_payroll_runs(
    db: Session,
    tenant_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[PayrollRun]:
    """Get all payroll runs"""
    return db.query(PayrollRun).filter(
        PayrollRun.tenant_id == tenant_id
    ).order_by(PayrollRun.pay_date.desc()).offset(skip).limit(limit).all()

def get_payroll_run(db: Session, run_id: int, tenant_id: int) -> Optional[PayrollRun]:
    """Get single payroll run"""
    return db.query(PayrollRun).filter(
        and_(
            PayrollRun.id == run_id,
            PayrollRun.tenant_id == tenant_id
        )
    ).first()

def get_pay_stubs(db: Session, run_id: int, tenant_id: int) -> List[PayStub]:
    """Get all pay stubs for a run"""
    return db.query(PayStub).filter(
        and_(
            PayStub.payroll_run_id == run_id,
            PayStub.tenant_id == tenant_id
        )
    ).all()

def get_employee_pay_stub(
    db: Session,
    employee_id: int,
    run_id: int,
    tenant_id: int
) -> Optional[PayStub]:
    """Get pay stub for specific employee"""
    return db.query(PayStub).filter(
        and_(
            PayStub.employee_id == employee_id,
            PayStub.payroll_run_id == run_id,
            PayStub.tenant_id == tenant_id
        )
    ).first()
