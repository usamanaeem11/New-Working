"""
Employee CRUD Operations
Real database operations with SQLAlchemy
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import date

from app.models.employee import Employee
from app.models.user import User

def get_employee(db: Session, employee_id: int, tenant_id: int) -> Optional[Employee]:
    """Get single employee by ID with tenant isolation"""
    return db.query(Employee).filter(
        and_(
            Employee.id == employee_id,
            Employee.tenant_id == tenant_id
        )
    ).first()

def get_employees(
    db: Session,
    tenant_id: int,
    skip: int = 0,
    limit: int = 100,
    department: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None
) -> List[Employee]:
    """Get all employees with filters"""
    query = db.query(Employee).filter(Employee.tenant_id == tenant_id)
    
    # Apply filters
    if department:
        query = query.filter(Employee.department == department)
    
    if status:
        query = query.filter(Employee.status == status)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Employee.first_name.ilike(search_term),
                Employee.last_name.ilike(search_term),
                Employee.email.ilike(search_term),
                Employee.employee_number.ilike(search_term)
            )
        )
    
    return query.offset(skip).limit(limit).all()

def create_employee(db: Session, employee_data: dict, tenant_id: int) -> Employee:
    """Create new employee"""
    employee = Employee(
        tenant_id=tenant_id,
        **employee_data
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee

def update_employee(
    db: Session,
    employee_id: int,
    tenant_id: int,
    employee_data: dict
) -> Optional[Employee]:
    """Update existing employee"""
    employee = get_employee(db, employee_id, tenant_id)
    
    if not employee:
        return None
    
    # Update fields
    for key, value in employee_data.items():
        if hasattr(employee, key) and value is not None:
            setattr(employee, key, value)
    
    db.commit()
    db.refresh(employee)
    return employee

def delete_employee(db: Session, employee_id: int, tenant_id: int) -> bool:
    """Soft delete employee (set status to inactive)"""
    employee = get_employee(db, employee_id, tenant_id)
    
    if not employee:
        return False
    
    employee.status = 'inactive'
    employee.termination_date = date.today()
    db.commit()
    return True

def get_employee_by_number(
    db: Session,
    employee_number: str,
    tenant_id: int
) -> Optional[Employee]:
    """Get employee by employee number"""
    return db.query(Employee).filter(
        and_(
            Employee.employee_number == employee_number,
            Employee.tenant_id == tenant_id
        )
    ).first()

def get_employees_by_department(
    db: Session,
    department: str,
    tenant_id: int
) -> List[Employee]:
    """Get all employees in a department"""
    return db.query(Employee).filter(
        and_(
            Employee.department == department,
            Employee.tenant_id == tenant_id,
            Employee.status == 'active'
        )
    ).all()

def get_employee_count(db: Session, tenant_id: int, status: str = 'active') -> int:
    """Get count of employees"""
    return db.query(Employee).filter(
        and_(
            Employee.tenant_id == tenant_id,
            Employee.status == status
        )
    ).count()
