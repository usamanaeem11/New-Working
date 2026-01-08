"""
Time Tracking Router - COMPLETE REAL IMPLEMENTATION
Real clock in/out with database persistence
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel

from app.database.session import get_db
from app.auth.jwt_manager import get_current_user
from app.auth.rbac import require_permission, Permission
from app.logging.logging_config import log_audit_event
from app.crud import time_entry as time_crud

router = APIRouter()

# Pydantic Models
class TimeEntryResponse(BaseModel):
    id: int
    employee_id: int
    date: date
    start_time: datetime
    end_time: Optional[datetime]
    hours: Optional[float]
    overtime_hours: float
    status: str
    
    class Config:
        from_attributes = True

class TimeEntryUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    hours: Optional[float] = None
    break_minutes: Optional[int] = None
    notes: Optional[str] = None

@router.post("/clock-in", status_code=status.HTTP_201_CREATED)
@require_permission(Permission.TIME_CREATE)
async def clock_in(
    location: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Clock in - REAL DATABASE INSERT
    Creates actual time entry in database
    """
    employee_id = current_user['id']
    tenant_id = current_user['tenant_id']
    
    try:
        entry = time_crud.clock_in(db, employee_id, tenant_id, location)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    log_audit_event(
        event_type='time_clock_in',
        user_id=employee_id,
        tenant_id=tenant_id,
        resource='time_entries',
        action='create',
        details={'entry_id': entry.id, 'start_time': entry.start_time.isoformat()}
    )
    
    return {
        'id': entry.id,
        'employee_id': entry.employee_id,
        'start_time': entry.start_time,
        'status': entry.status,
        'message': 'Clocked in successfully'
    }

@router.post("/clock-out")
@require_permission(Permission.TIME_CREATE)
async def clock_out(
    location: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Clock out - REAL DATABASE UPDATE
    Updates existing time entry with end time and calculates hours
    """
    employee_id = current_user['id']
    tenant_id = current_user['tenant_id']
    
    try:
        entry = time_crud.clock_out(db, employee_id, tenant_id, location)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    log_audit_event(
        event_type='time_clock_out',
        user_id=employee_id,
        tenant_id=tenant_id,
        resource='time_entries',
        action='update',
        details={
            'entry_id': entry.id,
            'end_time': entry.end_time.isoformat(),
            'hours': entry.hours,
            'overtime_hours': entry.overtime_hours
        }
    )
    
    return {
        'id': entry.id,
        'employee_id': entry.employee_id,
        'start_time': entry.start_time,
        'end_time': entry.end_time,
        'hours': entry.hours,
        'overtime_hours': entry.overtime_hours,
        'status': entry.status,
        'message': 'Clocked out successfully'
    }

@router.get("/entries", response_model=List[TimeEntryResponse])
@require_permission(Permission.TIME_READ)
async def get_time_entries(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status_filter: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get time entries - REAL DATABASE QUERY"""
    employee_id = current_user['id']
    tenant_id = current_user['tenant_id']
    
    entries = time_crud.get_time_entries(
        db=db,
        employee_id=employee_id,
        tenant_id=tenant_id,
        start_date=start_date,
        end_date=end_date,
        status=status_filter,
        skip=skip,
        limit=limit
    )
    
    return entries

@router.get("/entries/{entry_id}", response_model=TimeEntryResponse)
@require_permission(Permission.TIME_READ)
async def get_time_entry(
    entry_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get single time entry - REAL DATABASE QUERY"""
    tenant_id = current_user['tenant_id']
    
    entry = time_crud.get_time_entry(db, entry_id, tenant_id)
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time entry not found"
        )
    
    return entry

@router.put("/entries/{entry_id}", response_model=TimeEntryResponse)
@require_permission(Permission.TIME_UPDATE)
async def update_time_entry(
    entry_id: int,
    entry_update: TimeEntryUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update time entry - REAL DATABASE UPDATE"""
    tenant_id = current_user['tenant_id']
    
    updated_entry = time_crud.update_time_entry(
        db=db,
        entry_id=entry_id,
        tenant_id=tenant_id,
        entry_data=entry_update.dict(exclude_unset=True)
    )
    
    if not updated_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time entry not found"
        )
    
    log_audit_event(
        event_type='time_entry_update',
        user_id=current_user['id'],
        tenant_id=tenant_id,
        resource='time_entries',
        action='update',
        details={'entry_id': entry_id, 'changes': entry_update.dict(exclude_unset=True)}
    )
    
    return updated_entry

@router.post("/entries/{entry_id}/approve")
@require_permission(Permission.TIME_APPROVE)
async def approve_time_entry(
    entry_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve time entry - REAL DATABASE UPDATE"""
    tenant_id = current_user['tenant_id']
    approver_id = current_user['id']
    
    approved_entry = time_crud.approve_time_entry(db, entry_id, tenant_id, approver_id)
    
    if not approved_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time entry not found"
        )
    
    log_audit_event(
        event_type='time_entry_approve',
        user_id=approver_id,
        tenant_id=tenant_id,
        resource='time_entries',
        action='approve',
        details={'entry_id': entry_id, 'employee_id': approved_entry.employee_id}
    )
    
    return {'message': 'Time entry approved', 'entry_id': entry_id}

@router.get("/stats/total-hours")
@require_permission(Permission.TIME_READ)
async def get_total_hours(
    start_date: date,
    end_date: date,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get total hours in date range - REAL DATABASE AGGREGATE"""
    employee_id = current_user['id']
    tenant_id = current_user['tenant_id']
    
    total_hours = time_crud.get_total_hours(db, employee_id, tenant_id, start_date, end_date)
    
    return {
        'employee_id': employee_id,
        'start_date': start_date,
        'end_date': end_date,
        'total_hours': total_hours
    }
