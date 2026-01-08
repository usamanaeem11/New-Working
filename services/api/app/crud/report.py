"""
Reports CRUD Operations
Real report generation with actual data
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Dict, Any
from datetime import date

from app.models.report import Report
from app.models.employee import Employee
from app.models.time_entry import TimeEntry
from app.crud import time_entry as time_crud
from app.crud import employee as employee_crud

def generate_attendance_report(
    db: Session,
    tenant_id: int,
    start_date: date,
    end_date: date
) -> Dict[str, Any]:
    """Generate attendance report - REAL DATA"""
    
    # Get all active employees
    total_employees = employee_crud.get_employee_count(db, tenant_id, 'active')
    
    # Get time entries in period
    time_entries = db.query(TimeEntry).filter(
        and_(
            TimeEntry.tenant_id == tenant_id,
            TimeEntry.date >= start_date,
            TimeEntry.date <= end_date
        )
    ).all()
    
    # Calculate metrics
    total_days = (end_date - start_date).days + 1
    expected_entries = total_employees * total_days
    actual_entries = len([e for e in time_entries if e.status in ['completed', 'approved']])
    
    attendance_rate = actual_entries / expected_entries if expected_entries > 0 else 0
    
    # Count absences (days without entries)
    employees_with_entries = set([e.employee_id for e in time_entries])
    absences = total_employees - len(employees_with_entries)
    
    # Count late arrivals (clock in after 9 AM)
    from datetime import time as dt_time
    late_arrivals = len([
        e for e in time_entries 
        if e.start_time.time() > dt_time(9, 0)
    ])
    
    return {
        'report_type': 'attendance',
        'period': {'start': start_date.isoformat(), 'end': end_date.isoformat()},
        'total_employees': total_employees,
        'total_days': total_days,
        'attendance_rate': round(attendance_rate, 3),
        'actual_entries': actual_entries,
        'expected_entries': expected_entries,
        'absences': absences,
        'late_arrivals': late_arrivals
    }

def generate_hours_report(
    db: Session,
    tenant_id: int,
    start_date: date,
    end_date: date
) -> Dict[str, Any]:
    """Generate hours worked report - REAL DATA"""
    
    # Get all time entries in period
    result = db.query(
        func.sum(TimeEntry.hours).label('total_hours'),
        func.sum(TimeEntry.overtime_hours).label('overtime_hours'),
        func.count(TimeEntry.id).label('entry_count')
    ).filter(
        and_(
            TimeEntry.tenant_id == tenant_id,
            TimeEntry.date >= start_date,
            TimeEntry.date <= end_date,
            TimeEntry.status.in_(['completed', 'approved'])
        )
    ).first()
    
    total_hours = float(result.total_hours or 0)
    overtime_hours = float(result.overtime_hours or 0)
    regular_hours = total_hours - overtime_hours
    
    # Average per employee
    employee_count = employee_crud.get_employee_count(db, tenant_id, 'active')
    avg_per_employee = total_hours / employee_count if employee_count > 0 else 0
    
    return {
        'report_type': 'hours',
        'period': {'start': start_date.isoformat(), 'end': end_date.isoformat()},
        'total_hours': round(total_hours, 2),
        'regular_hours': round(regular_hours, 2),
        'overtime_hours': round(overtime_hours, 2),
        'entry_count': result.entry_count or 0,
        'average_per_employee': round(avg_per_employee, 2),
        'employee_count': employee_count
    }

def generate_payroll_report(
    db: Session,
    tenant_id: int,
    start_date: date,
    end_date: date
) -> Dict[str, Any]:
    """Generate payroll summary report - REAL DATA"""
    
    from app.models.payroll import PayrollRun, PayStub
    
    # Get payroll runs in period
    runs = db.query(PayrollRun).filter(
        and_(
            PayrollRun.tenant_id == tenant_id,
            PayrollRun.pay_date >= start_date,
            PayrollRun.pay_date <= end_date
        )
    ).all()
    
    total_paid = sum([r.total_amount for r in runs])
    total_employees = sum([r.employee_count for r in runs]) / len(runs) if runs else 0
    
    # Get pay stub details
    pay_stubs = db.query(PayStub).join(PayrollRun).filter(
        and_(
            PayrollRun.tenant_id == tenant_id,
            PayrollRun.pay_date >= start_date,
            PayrollRun.pay_date <= end_date
        )
    ).all()
    
    if pay_stubs:
        avg_pay = sum([ps.net_pay for ps in pay_stubs]) / len(pay_stubs)
        highest_pay = max([ps.net_pay for ps in pay_stubs])
        lowest_pay = min([ps.net_pay for ps in pay_stubs])
    else:
        avg_pay = highest_pay = lowest_pay = 0
    
    return {
        'report_type': 'payroll',
        'period': {'start': start_date.isoformat(), 'end': end_date.isoformat()},
        'total_paid': round(total_paid, 2),
        'average_salary': round(avg_pay, 2),
        'highest_paid': round(highest_pay, 2),
        'lowest_paid': round(lowest_pay, 2),
        'payroll_runs': len(runs),
        'total_employees': int(total_employees)
    }

def generate_performance_report(
    db: Session,
    tenant_id: int,
    start_date: date,
    end_date: date
) -> Dict[str, Any]:
    """Generate performance report - REAL DATA"""
    
    # Get employees and their metrics
    employees = employee_crud.get_employees(db, tenant_id, status='active')
    
    performance_data = []
    for emp in employees:
        # Get hours worked
        total_hours = time_crud.get_total_hours(
            db, emp.id, tenant_id, start_date, end_date
        )
        
        # Get attendance rate
        entries = time_crud.get_time_entries(
            db, emp.id, tenant_id, start_date, end_date, status='approved'
        )
        
        performance_data.append({
            'employee_id': emp.id,
            'name': f"{emp.first_name} {emp.last_name}",
            'department': emp.department,
            'hours_worked': total_hours,
            'days_present': len(entries),
            'performance_score': min(100, int((total_hours / 160) * 100))  # Based on expected 160 hours/month
        })
    
    # Sort by performance
    performance_data.sort(key=lambda x: x['performance_score'], reverse=True)
    
    return {
        'report_type': 'performance',
        'period': {'start': start_date.isoformat(), 'end': end_date.isoformat()},
        'employees': performance_data[:50],  # Top 50
        'average_score': sum([e['performance_score'] for e in performance_data]) / len(performance_data) if performance_data else 0,
        'top_performer': performance_data[0] if performance_data else None,
        'total_evaluated': len(performance_data)
    }

def create_report(
    db: Session,
    tenant_id: int,
    report_type: str,
    start_date: date,
    end_date: date,
    generated_by: int,
    format: str = 'json'
) -> Report:
    """Create report - REAL GENERATION"""
    
    # Generate data based on type
    if report_type == 'attendance':
        data = generate_attendance_report(db, tenant_id, start_date, end_date)
    elif report_type == 'hours':
        data = generate_hours_report(db, tenant_id, start_date, end_date)
    elif report_type == 'payroll':
        data = generate_payroll_report(db, tenant_id, start_date, end_date)
    elif report_type == 'performance':
        data = generate_performance_report(db, tenant_id, start_date, end_date)
    else:
        raise ValueError(f"Unknown report type: {report_type}")
    
    # Create report record
    report = Report(
        tenant_id=tenant_id,
        report_type=report_type,
        title=f"{report_type.title()} Report - {start_date} to {end_date}",
        start_date=start_date,
        end_date=end_date,
        data=data,
        generated_by=generated_by,
        status='completed',
        format=format
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return report

def get_report(db: Session, report_id: int, tenant_id: int) -> Report:
    """Get report by ID"""
    return db.query(Report).filter(
        and_(
            Report.id == report_id,
            Report.tenant_id == tenant_id
        )
    ).first()

def get_reports(db: Session, tenant_id: int, limit: int = 50):
    """Get all reports"""
    return db.query(Report).filter(
        Report.tenant_id == tenant_id
    ).order_by(Report.created_at.desc()).limit(limit).all()
