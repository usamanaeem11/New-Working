"""
Time Entry CRUD Operations
Real database operations for time tracking
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional
from datetime import datetime, date, timedelta

from app.models.time_entry import TimeEntry

def get_time_entry(db: Session, entry_id: int, tenant_id: int) -> Optional[TimeEntry]:
    """Get single time entry"""
    return db.query(TimeEntry).filter(
        and_(
            TimeEntry.id == entry_id,
            TimeEntry.tenant_id == tenant_id
        )
    ).first()

def get_active_entry(db: Session, employee_id: int, tenant_id: int) -> Optional[TimeEntry]:
    """Get active (currently clocked in) entry for employee"""
    return db.query(TimeEntry).filter(
        and_(
            TimeEntry.employee_id == employee_id,
            TimeEntry.tenant_id == tenant_id,
            TimeEntry.end_time == None,
            TimeEntry.status == 'active'
        )
    ).first()

def clock_in(db: Session, employee_id: int, tenant_id: int, location: Optional[str] = None) -> TimeEntry:
    """Clock in employee"""
    # Check if already clocked in
    existing = get_active_entry(db, employee_id, tenant_id)
    if existing:
        raise ValueError("Already clocked in")
    
    now = datetime.utcnow()
    entry = TimeEntry(
        tenant_id=tenant_id,
        employee_id=employee_id,
        date=now.date(),
        start_time=now,
        status='active',
        clock_in_location=location
    )
    
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

def clock_out(
    db: Session,
    employee_id: int,
    tenant_id: int,
    location: Optional[str] = None
) -> Optional[TimeEntry]:
    """Clock out employee"""
    entry = get_active_entry(db, employee_id, tenant_id)
    
    if not entry:
        raise ValueError("Not currently clocked in")
    
    now = datetime.utcnow()
    entry.end_time = now
    entry.clock_out_location = location
    
    # Calculate hours
    duration = now - entry.start_time
    hours = duration.total_seconds() / 3600
    hours -= (entry.break_minutes / 60)
    entry.hours = round(hours, 2)
    
    # Calculate overtime (if over 8 hours)
    if hours > 8:
        entry.overtime_hours = round(hours - 8, 2)
    
    entry.status = 'completed'
    
    db.commit()
    db.refresh(entry)
    return entry

def get_time_entries(
    db: Session,
    employee_id: int,
    tenant_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[TimeEntry]:
    """Get time entries with filters"""
    query = db.query(TimeEntry).filter(
        and_(
            TimeEntry.employee_id == employee_id,
            TimeEntry.tenant_id == tenant_id
        )
    )
    
    if start_date:
        query = query.filter(TimeEntry.date >= start_date)
    
    if end_date:
        query = query.filter(TimeEntry.date <= end_date)
    
    if status:
        query = query.filter(TimeEntry.status == status)
    
    return query.order_by(TimeEntry.date.desc()).offset(skip).limit(limit).all()

def get_total_hours(
    db: Session,
    employee_id: int,
    tenant_id: int,
    start_date: date,
    end_date: date
) -> float:
    """Get total hours worked in date range"""
    result = db.query(func.sum(TimeEntry.hours)).filter(
        and_(
            TimeEntry.employee_id == employee_id,
            TimeEntry.tenant_id == tenant_id,
            TimeEntry.date >= start_date,
            TimeEntry.date <= end_date,
            TimeEntry.status.in_(['completed', 'approved'])
        )
    ).scalar()
    
    return result or 0.0

def approve_time_entry(
    db: Session,
    entry_id: int,
    tenant_id: int,
    approver_id: int
) -> Optional[TimeEntry]:
    """Approve time entry"""
    entry = get_time_entry(db, entry_id, tenant_id)
    
    if not entry:
        return None
    
    entry.status = 'approved'
    entry.approved_by = approver_id
    entry.approved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(entry)
    return entry

def update_time_entry(
    db: Session,
    entry_id: int,
    tenant_id: int,
    entry_data: dict
) -> Optional[TimeEntry]:
    """Update time entry"""
    entry = get_time_entry(db, entry_id, tenant_id)
    
    if not entry:
        return None
    
    # Update allowed fields
    allowed_fields = ['start_time', 'end_time', 'hours', 'break_minutes', 'notes']
    for key, value in entry_data.items():
        if key in allowed_fields and value is not None:
            setattr(entry, key, value)
    
    db.commit()
    db.refresh(entry)
    return entry
