"""
Time Tracking with Real-time WebSocket Integration
Sends live updates when employees clock in/out
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database.session import get_db
from app.auth.jwt_manager import get_current_user
from app.auth.rbac import require_permission, Permission
from app.logging.logging_config import log_audit_event
from app.crud import time_entry as time_crud
from app.websocket.connection_manager import manager

router = APIRouter()

@router.post("/clock-in-realtime", status_code=status.HTTP_201_CREATED)
@require_permission(Permission.TIME_CREATE)
async def clock_in_realtime(
    location: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Clock in with REAL-TIME WebSocket notification
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
    
    # REAL-TIME NOTIFICATION via WebSocket
    await manager.notify_time_entry(
        tenant_id=tenant_id,
        employee_id=employee_id,
        action='clock_in',
        data={
            'id': entry.id,
            'employee_id': entry.employee_id,
            'start_time': entry.start_time.isoformat(),
            'status': entry.status
        }
    )
    
    log_audit_event(
        event_type='time_clock_in',
        user_id=employee_id,
        tenant_id=tenant_id,
        resource='time_entries',
        action='create',
        details={'entry_id': entry.id}
    )
    
    return {
        'id': entry.id,
        'employee_id': entry.employee_id,
        'start_time': entry.start_time,
        'status': entry.status,
        'message': 'Clocked in successfully',
        'realtime_notification_sent': True
    }

@router.post("/clock-out-realtime")
@require_permission(Permission.TIME_CREATE)
async def clock_out_realtime(
    location: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Clock out with REAL-TIME WebSocket notification
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
    
    # REAL-TIME NOTIFICATION via WebSocket
    await manager.notify_time_entry(
        tenant_id=tenant_id,
        employee_id=employee_id,
        action='clock_out',
        data={
            'id': entry.id,
            'employee_id': entry.employee_id,
            'start_time': entry.start_time.isoformat(),
            'end_time': entry.end_time.isoformat(),
            'hours': entry.hours,
            'overtime_hours': entry.overtime_hours,
            'status': entry.status
        }
    )
    
    log_audit_event(
        event_type='time_clock_out',
        user_id=employee_id,
        tenant_id=tenant_id,
        resource='time_entries',
        action='update',
        details={'entry_id': entry.id, 'hours': entry.hours}
    )
    
    return {
        'id': entry.id,
        'employee_id': entry.employee_id,
        'hours': entry.hours,
        'overtime_hours': entry.overtime_hours,
        'status': entry.status,
        'message': 'Clocked out successfully',
        'realtime_notification_sent': True
    }
