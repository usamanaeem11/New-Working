"""
Payroll Router - REAL IMPLEMENTATION
Actual payroll processing with real calculations
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import date

from app.database.session import get_db
from app.auth.jwt_manager import get_current_user
from app.auth.rbac import require_permission, Permission
from app.logging.logging_config import log_audit_event
from app.crud import payroll as payroll_crud

router = APIRouter()

# Pydantic Models
class PayrollRunCreate(BaseModel):
    pay_period_start: date
    pay_period_end: date
    pay_date: date

class PayrollRunResponse(BaseModel):
    id: int
    pay_period_start: date
    pay_period_end: date
    pay_date: date
    status: str
    total_amount: float
    total_hours: float
    employee_count: int
    
    class Config:
        from_attributes = True

class PayStubResponse(BaseModel):
    id: int
    employee_id: int
    regular_hours: float
    overtime_hours: float
    total_hours: float
    gross_pay: float
    total_deductions: float
    net_pay: float
    
    class Config:
        from_attributes = True

@router.post("/run", response_model=PayrollRunResponse, status_code=status.HTTP_201_CREATED)
@require_permission(Permission.PAYROLL_RUN)
async def run_payroll(
    payroll_data: PayrollRunCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Run payroll - REAL PROCESSING
    Calculates hours, pay, deductions from actual time entries
    """
    tenant_id = current_user['tenant_id']
    user_id = current_user['id']
    
    payroll_run = payroll_crud.create_payroll_run(
        db=db,
        tenant_id=tenant_id,
        pay_period_start=payroll_data.pay_period_start,
        pay_period_end=payroll_data.pay_period_end,
        pay_date=payroll_data.pay_date,
        processed_by=user_id
    )
    
    log_audit_event(
        event_type='payroll_run',
        user_id=user_id,
        tenant_id=tenant_id,
        resource='payroll',
        action='run',
        details={
            'payroll_run_id': payroll_run.id,
            'period': f"{payroll_data.pay_period_start} to {payroll_data.pay_period_end}",
            'total_amount': payroll_run.total_amount,
            'employee_count': payroll_run.employee_count
        }
    )
    
    return payroll_run

@router.get("/runs", response_model=List[PayrollRunResponse])
@require_permission(Permission.PAYROLL_READ)
async def get_payroll_runs(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payroll history - REAL DATABASE QUERY"""
    tenant_id = current_user['tenant_id']
    
    runs = payroll_crud.get_payroll_runs(db, tenant_id, skip, limit)
    return runs

@router.get("/runs/{run_id}", response_model=PayrollRunResponse)
@require_permission(Permission.PAYROLL_READ)
async def get_payroll_run(
    run_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific payroll run - REAL DATABASE QUERY"""
    tenant_id = current_user['tenant_id']
    
    run = payroll_crud.get_payroll_run(db, run_id, tenant_id)
    
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payroll run not found"
        )
    
    return run

@router.get("/runs/{run_id}/pay-stubs", response_model=List[PayStubResponse])
@require_permission(Permission.PAYROLL_READ)
async def get_pay_stubs(
    run_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all pay stubs for a run - REAL DATABASE QUERY"""
    tenant_id = current_user['tenant_id']
    
    pay_stubs = payroll_crud.get_pay_stubs(db, run_id, tenant_id)
    return pay_stubs
