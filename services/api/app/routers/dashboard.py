"""
Dashboard API Router
Complete dashboard data endpoint with metrics, employees, time entries
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Any

from app.database.session import get_db
from app.auth.jwt_manager import get_current_user
from app.auth.rbac import require_permission, Permission
from app.logging.logging_config import log_audit_event

router = APIRouter()

@router.get("/metrics")
@require_permission(Permission.EMPLOYEE_READ)
async def get_dashboard_metrics(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get dashboard metrics
    Returns: active employees, clocked in, today's hours, week's hours
    """
    
    tenant_id = current_user['tenant_id']
    
    # Mock data - in production, query from database
    # employees = db.query(Employee).filter(
    #     Employee.tenant_id == tenant_id,
    #     Employee.status == 'active'
    # ).all()
    
    # time_entries_today = db.query(TimeEntry).filter(
    #     TimeEntry.tenant_id == tenant_id,
    #     TimeEntry.date >= datetime.now().date()
    # ).all()
    
    metrics = {
        'active_employees': 25,
        'clocked_in': 12,
        'today_hours': 96.5,
        'week_hours': 520.0,
        'on_leave': 3,
        'overtime': 8.5,
    }
    
    log_audit_event(
        event_type='data_access',
        user_id=current_user['id'],
        tenant_id=tenant_id,
        resource='dashboard',
        action='view_metrics'
    )
    
    return {'metrics': metrics, 'status': 'success'}

@router.get("/activity")
@require_permission(Permission.TIME_READ)
async def get_dashboard_activity(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get recent activity feed
    Returns: Recent clock ins, clock outs, and other events
    """
    
    tenant_id = current_user['tenant_id']
    
    # Mock activity data
    activity = [
        {
            'id': 1,
            'type': 'clock_in',
            'employee_name': 'John Doe',
            'timestamp': datetime.now().isoformat(),
            'department': 'Engineering'
        },
        {
            'id': 2,
            'type': 'clock_out',
            'employee_name': 'Jane Smith',
            'timestamp': (datetime.now() - timedelta(minutes=30)).isoformat(),
            'department': 'Sales'
        },
        {
            'id': 3,
            'type': 'leave_request',
            'employee_name': 'Bob Wilson',
            'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
            'department': 'Marketing'
        }
    ]
    
    return {'activity': activity, 'status': 'success'}

@router.get("/status")
async def get_user_status(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's clock status
    Returns: Whether user is clocked in and active entry details
    """
    
    user_id = current_user['id']
    
    # Mock status - in production, query active time entry
    # active_entry = db.query(TimeEntry).filter(
    #     TimeEntry.user_id == user_id,
    #     TimeEntry.end_time == None
    # ).first()
    
    is_clocked_in = False
    active_entry = None
    
    return {
        'is_clocked_in': is_clocked_in,
        'active_entry': active_entry,
        'status': 'success'
    }

@router.get("/complete")
@require_permission(Permission.EMPLOYEE_READ)
async def get_complete_dashboard(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get complete dashboard data in one call
    Includes: metrics, recent employees, user status, activity
    """
    
    tenant_id = current_user['tenant_id']
    
    # Get all data
    metrics = {
        'active_employees': 25,
        'clocked_in': 12,
        'today_hours': 96.5,
        'week_hours': 520.0,
    }
    
    # Recent employees
    employees = [
        {
            'id': 1,
            'first_name': 'John',
            'last_name': 'Doe',
            'position': 'Senior Developer',
            'department': 'Engineering',
            'status': 'active',
            'email': 'john.doe@company.com'
        },
        {
            'id': 2,
            'first_name': 'Jane',
            'last_name': 'Smith',
            'position': 'Sales Manager',
            'department': 'Sales',
            'status': 'active',
            'email': 'jane.smith@company.com'
        },
        {
            'id': 3,
            'first_name': 'Bob',
            'last_name': 'Wilson',
            'position': 'Marketing Lead',
            'department': 'Marketing',
            'status': 'active',
            'email': 'bob.wilson@company.com'
        }
    ]
    
    # User status
    is_clocked_in = False
    
    # Recent activity
    activity = [
        {
            'type': 'clock_in',
            'employee_name': 'John Doe',
            'timestamp': datetime.now().isoformat(),
        }
    ]
    
    log_audit_event(
        event_type='data_access',
        user_id=current_user['id'],
        tenant_id=tenant_id,
        resource='dashboard',
        action='view_complete'
    )
    
    return {
        'metrics': metrics,
        'employees': employees,
        'is_clocked_in': is_clocked_in,
        'activity': activity,
        'status': 'success'
    }
