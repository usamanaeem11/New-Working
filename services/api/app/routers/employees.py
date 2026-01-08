"""
Employees Router - COMPLETE REAL IMPLEMENTATION
Full CRUD with actual database operations
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import date

from app.database.session import get_db
from app.auth.jwt_manager import get_current_user
from app.auth.rbac import require_permission, Permission
from app.logging.logging_config import log_audit_event
from app.crud import employee as employee_crud

router = APIRouter()

# Pydantic Models
class EmployeeBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    employee_number: str
    department: str
    position: str
    hire_date: date
    phone: Optional[str] = None
    salary: Optional[float] = None
    hourly_rate: Optional[float] = None
    employment_type: str = "full_time"
    pay_frequency: str = "monthly"
    status: str = "active"
    manager_id: Optional[int] = None
    notes: Optional[str] = None

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    phone: Optional[str] = None
    salary: Optional[float] = None
    hourly_rate: Optional[float] = None
    status: Optional[str] = None
    manager_id: Optional[int] = None
    notes: Optional[str] = None

class EmployeeResponse(EmployeeBase):
    id: int
    tenant_id: int
    created_at: date
    updated_at: date
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[EmployeeResponse])
@require_permission(Permission.EMPLOYEE_READ)
async def get_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    department: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all employees with filters
    REAL DATABASE QUERY
    """
    tenant_id = current_user['tenant_id']
    
    employees = employee_crud.get_employees(
        db=db,
        tenant_id=tenant_id,
        skip=skip,
        limit=limit,
        department=department,
        status=status,
        search=search
    )
    
    log_audit_event(
        event_type='employee_list',
        user_id=current_user['id'],
        tenant_id=tenant_id,
        resource='employees',
        action='read',
        details={'count': len(employees), 'filters': {'department': department, 'status': status}}
    )
    
    return employees

@router.get("/{employee_id}", response_model=EmployeeResponse)
@require_permission(Permission.EMPLOYEE_READ)
async def get_employee(
    employee_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get single employee - REAL DATABASE QUERY"""
    tenant_id = current_user['tenant_id']
    
    employee = employee_crud.get_employee(db, employee_id, tenant_id)
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    log_audit_event(
        event_type='employee_view',
        user_id=current_user['id'],
        tenant_id=tenant_id,
        resource='employees',
        action='read',
        details={'employee_id': employee_id}
    )
    
    return employee

@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
@require_permission(Permission.EMPLOYEE_CREATE)
async def create_employee(
    employee: EmployeeCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new employee - REAL DATABASE INSERT"""
    tenant_id = current_user['tenant_id']
    
    # Check if employee number already exists
    existing = employee_crud.get_employee_by_number(db, employee.employee_number, tenant_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee number already exists"
        )
    
    new_employee = employee_crud.create_employee(
        db=db,
        employee_data=employee.dict(),
        tenant_id=tenant_id
    )
    
    log_audit_event(
        event_type='employee_create',
        user_id=current_user['id'],
        tenant_id=tenant_id,
        resource='employees',
        action='create',
        details={'employee_id': new_employee.id, 'employee_number': employee.employee_number}
    )
    
    return new_employee

@router.put("/{employee_id}", response_model=EmployeeResponse)
@require_permission(Permission.EMPLOYEE_UPDATE)
async def update_employee(
    employee_id: int,
    employee_update: EmployeeUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update employee - REAL DATABASE UPDATE"""
    tenant_id = current_user['tenant_id']
    
    updated_employee = employee_crud.update_employee(
        db=db,
        employee_id=employee_id,
        tenant_id=tenant_id,
        employee_data=employee_update.dict(exclude_unset=True)
    )
    
    if not updated_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    log_audit_event(
        event_type='employee_update',
        user_id=current_user['id'],
        tenant_id=tenant_id,
        resource='employees',
        action='update',
        details={'employee_id': employee_id, 'changes': employee_update.dict(exclude_unset=True)}
    )
    
    return updated_employee

@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permission(Permission.EMPLOYEE_DELETE)
async def delete_employee(
    employee_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete employee (soft delete) - REAL DATABASE UPDATE"""
    tenant_id = current_user['tenant_id']
    
    success = employee_crud.delete_employee(db, employee_id, tenant_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    log_audit_event(
        event_type='employee_delete',
        user_id=current_user['id'],
        tenant_id=tenant_id,
        resource='employees',
        action='delete',
        details={'employee_id': employee_id}
    )
    
    return None

@router.get("/stats/count")
@require_permission(Permission.EMPLOYEE_READ)
async def get_employee_count(
    status_filter: str = Query('active'),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get employee count - REAL DATABASE COUNT"""
    tenant_id = current_user['tenant_id']
    
    count = employee_crud.get_employee_count(db, tenant_id, status_filter)
    
    return {'count': count, 'status': status_filter}
