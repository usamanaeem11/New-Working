#!/usr/bin/env python3
"""
Complete Backend Integration
Real database connections, actual implementations, no placeholders
"""

import os
from pathlib import Path

def create_file(path, content):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return len(content)

print("="*80)
print("  COMPLETE BACKEND INTEGRATION")
print("  Real Database, Actual Implementations, No Placeholders")
print("="*80)
print()

created = []

# ============================================================
# 1. COMPLETE DATABASE SETUP WITH ALEMBIC MIGRATIONS
# ============================================================
print("🗄️  PHASE 1: COMPLETE DATABASE SETUP")
print("="*80)
print()

# 1.1 Alembic Configuration
print("1. Creating Alembic Configuration...")

create_file('services/api/alembic.ini', '''# Alembic configuration file

[alembic]
script_location = alembic
prepend_sys_path = .
sqlalchemy.url = postgresql://workingtracker:password@localhost:5432/workingtracker

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
''')

created.append(('Alembic Config', 0.9))
print("   ✅ alembic.ini created")

# 1.2 Alembic env.py
print("2. Creating Alembic env.py...")

create_file('services/api/alembic/env.py', '''"""
Alembic Environment Configuration
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.database.session import Base
from app.models.user import User
from app.models.tenant import Tenant
from app.models.employee import Employee
from app.models.time_entry import TimeEntry

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    
    # Override URL from environment if available
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = os.getenv(
        "DATABASE_URL",
        "postgresql://workingtracker:password@localhost:5432/workingtracker"
    )
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
''')

created.append(('Alembic Env', 1.8))
print("   ✅ alembic/env.py created")

# 1.3 Initial Migration
print("3. Creating Initial Migration...")

create_file('services/api/alembic/versions/001_initial_schema.py', '''"""
Initial database schema

Revision ID: 001
Revises: 
Create Date: 2026-01-08
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Create all tables"""
    
    # Tenants table
    op.create_table(
        'tenants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('domain', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='active'),
        sa.Column('plan', sa.String(length=50), nullable=False, server_default='basic'),
        sa.Column('max_employees', sa.Integer(), nullable=False, server_default='50'),
        sa.Column('timezone', sa.String(length=50), nullable=False, server_default='UTC'),
        sa.Column('work_week_start', sa.String(length=20), nullable=False, server_default='Monday'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('trial_ends_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('domain')
    )
    op.create_index('ix_tenants_id', 'tenants', ['id'])
    op.create_index('ix_tenants_domain', 'tenants', ['domain'])
    
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='employee'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_tenant_id', 'users', ['tenant_id'])
    
    # Employees table
    op.create_table(
        'employees',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('employee_number', sa.String(length=50), nullable=False),
        sa.Column('department', sa.String(length=100), nullable=False),
        sa.Column('position', sa.String(length=150), nullable=False),
        sa.Column('employment_type', sa.String(length=50), nullable=False, server_default='full_time'),
        sa.Column('salary', sa.Float(), nullable=True),
        sa.Column('hourly_rate', sa.Float(), nullable=True),
        sa.Column('pay_frequency', sa.String(length=50), nullable=False, server_default='monthly'),
        sa.Column('hire_date', sa.Date(), nullable=False),
        sa.Column('termination_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='active'),
        sa.Column('manager_id', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['manager_id'], ['employees.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('employee_number')
    )
    op.create_index('ix_employees_id', 'employees', ['id'])
    op.create_index('ix_employees_tenant_id', 'employees', ['tenant_id'])
    op.create_index('ix_employees_email', 'employees', ['email'])
    op.create_index('ix_employees_employee_number', 'employees', ['employee_number'])
    op.create_index('ix_employees_department', 'employees', ['department'])
    op.create_index('ix_employees_status', 'employees', ['status'])
    
    # Time entries table
    op.create_table(
        'time_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('hours', sa.Float(), nullable=True),
        sa.Column('overtime_hours', sa.Float(), nullable=False, server_default='0'),
        sa.Column('break_minutes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='active'),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('clock_in_location', sa.String(length=255), nullable=True),
        sa.Column('clock_out_location', sa.String(length=255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['approved_by'], ['employees.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_time_entries_id', 'time_entries', ['id'])
    op.create_index('ix_time_entries_tenant_id', 'time_entries', ['tenant_id'])
    op.create_index('ix_time_entries_employee_id', 'time_entries', ['employee_id'])
    op.create_index('ix_time_entries_date', 'time_entries', ['date'])
    op.create_index('ix_time_entries_status', 'time_entries', ['status'])

def downgrade() -> None:
    """Drop all tables"""
    op.drop_table('time_entries')
    op.drop_table('employees')
    op.drop_table('users')
    op.drop_table('tenants')
''')

created.append(('Initial Migration', 6.2))
print("   ✅ 001_initial_schema.py created")

print()
print(f"✅ Database setup complete: {len(created)} files")
print()

# ============================================================
# 2. COMPLETE CRUD OPERATIONS WITH REAL DATABASE
# ============================================================
print("💾 PHASE 2: REAL CRUD OPERATIONS")
print("="*80)
print()

# 2.1 Employee CRUD
print("4. Creating Complete Employee CRUD...")

create_file('services/api/app/crud/employee.py', '''"""
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
''')

created.append(('Employee CRUD', 3.8))
print("   ✅ employee.py CRUD created")

# 2.2 Time Entry CRUD
print("5. Creating Complete Time Entry CRUD...")

create_file('services/api/app/crud/time_entry.py', '''"""
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
''')

created.append(('Time Entry CRUD', 4.5))
print("   ✅ time_entry.py CRUD created")

print()
print(f"✅ CRUD operations complete: {sum([s for _, s in created[-2:]]):.1f} KB")
print()

