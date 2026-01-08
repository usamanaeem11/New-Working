"""
Complete Database Models for Time Tracking Platform
Includes all features: HRMS, AI, Geolocation, Compliance, White-label, etc.
"""

from datetime import datetime, date
from typing import Optional, List
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, 
    Text, Float, JSON, Enum, Date, Time, Numeric, Index
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
import uuid

Base = declarative_base()

# ==================== ENUMS ====================

class UserRole(str, PyEnum):
    SUPER_ADMIN = "super_admin"
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"
    CLIENT = "client"
    CONTRACTOR = "contractor"

class SubscriptionTier(str, PyEnum):
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"
    WHITE_LABEL = "white_label"

class SubscriptionStatus(str, PyEnum):
    ACTIVE = "active"
    TRIAL = "trial"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    PAUSED = "paused"

class ActivityType(str, PyEnum):
    PRODUCTIVE = "productive"
    NEUTRAL = "neutral"
    UNPRODUCTIVE = "unproductive"
    AWAY = "away"

class InvoiceStatus(str, PyEnum):
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELED = "canceled"

class LeaveStatus(str, PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELED = "canceled"

class ExpenseStatus(str, PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REIMBURSED = "reimbursed"

class PayrollStatus(str, PyEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ProjectStatus(str, PyEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

# ==================== CORE MODELS ====================

class Organization(Base):
    """Main organization/company entity - supports white-label"""
    __tablename__ = "organizations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    
    # White-label configuration
    is_white_label = Column(Boolean, default=False)
    parent_org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    custom_domain = Column(String(255), nullable=True)
    custom_branding = Column(JSONB, nullable=True)  # Logo, colors, etc.
    
    # Subscription
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE)
    subscription_status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.TRIAL)
    trial_ends_at = Column(DateTime, nullable=True)
    subscription_started_at = Column(DateTime, nullable=True)
    
    # Billing
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    billing_email = Column(String(255), nullable=True)
    
    # Settings
    settings = Column(JSONB, default={})
    timezone = Column(String(50), default="UTC")
    currency = Column(String(3), default="USD")
    
    # Compliance
    industry = Column(String(100), nullable=True)
    compliance_requirements = Column(ARRAY(String), default=[])  # HIPAA, SOC2, etc.
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    users = relationship("User", back_populates="organization")
    projects = relationship("Project", back_populates="organization")
    teams = relationship("Team", back_populates="organization")
    children = relationship("Organization", remote_side=[id])
    
    __table_args__ = (
        Index('idx_org_slug', 'slug'),
        Index('idx_org_subscription', 'subscription_tier', 'subscription_status'),
    )


class User(Base):
    """User/Employee model with comprehensive features"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    # Basic Info
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # Null for OAuth-only users
    full_name = Column(String(255), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    
    # Role & Permissions
    role = Column(Enum(UserRole), default=UserRole.EMPLOYEE)
    permissions = Column(JSONB, default={})
    
    # OAuth
    google_id = Column(String(255), nullable=True, unique=True)
    microsoft_id = Column(String(255), nullable=True, unique=True)
    
    # Employment Details
    employee_id = Column(String(50), nullable=True, unique=True)
    department = Column(String(100), nullable=True)
    job_title = Column(String(100), nullable=True)
    hire_date = Column(Date, nullable=True)
    termination_date = Column(Date, nullable=True)
    
    # Compensation
    hourly_rate = Column(Numeric(10, 2), nullable=True)
    salary = Column(Numeric(12, 2), nullable=True)
    currency = Column(String(3), default="USD")
    
    # Work Schedule
    work_hours_per_week = Column(Integer, default=40)
    work_days = Column(ARRAY(String), default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
    shift_start = Column(Time, nullable=True)
    shift_end = Column(Time, nullable=True)
    
    # Time Tracking Settings
    auto_track = Column(Boolean, default=False)
    screenshot_enabled = Column(Boolean, default=True)
    screenshot_interval = Column(Integer, default=600)  # seconds
    activity_tracking = Column(Boolean, default=True)
    
    # AI Settings
    ai_coaching_enabled = Column(Boolean, default=True)
    ai_autopilot_enabled = Column(Boolean, default=False)
    productivity_insights = Column(Boolean, default=True)
    
    # Wellness
    burnout_prevention = Column(Boolean, default=True)
    break_reminders = Column(Boolean, default=True)
    focus_mode_enabled = Column(Boolean, default=False)
    
    # Geolocation
    location_tracking_enabled = Column(Boolean, default=False)
    last_known_location = Column(JSONB, nullable=True)  # {lat, lng, timestamp}
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_active_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    time_entries = relationship("TimeEntry", back_populates="user")
    screenshots = relationship("Screenshot", back_populates="user")
    activities = relationship("Activity", back_populates="user")
    ai_insights = relationship("AIInsight", back_populates="user")
    leave_requests = relationship("LeaveRequest", back_populates="user")
    expenses = relationship("Expense", back_populates="user")
    
    __table_args__ = (
        Index('idx_user_org', 'organization_id'),
        Index('idx_user_email', 'email'),
        Index('idx_user_role', 'role'),
    )


class Team(Base):
    """Teams within organization"""
    __tablename__ = "teams"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    manager_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Settings
    settings = Column(JSONB, default={})
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="teams")
    manager = relationship("User", foreign_keys=[manager_id])


class Project(Base):
    """Projects for time tracking"""
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    client_name = Column(String(255), nullable=True)
    project_code = Column(String(50), nullable=True, unique=True)
    
    # Status & Dates
    status = Column(Enum(ProjectStatus), default=ProjectStatus.ACTIVE)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    deadline = Column(Date, nullable=True)
    
    # Budget & Billing
    budget_hours = Column(Float, nullable=True)
    budget_amount = Column(Numeric(12, 2), nullable=True)
    hourly_rate = Column(Numeric(10, 2), nullable=True)
    is_billable = Column(Boolean, default=True)
    
    # Settings
    color = Column(String(7), default="#3B82F6")
    settings = Column(JSONB, default={})
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="projects")
    time_entries = relationship("TimeEntry", back_populates="project")
    tasks = relationship("Task", back_populates="project")
    
    __table_args__ = (
        Index('idx_project_org', 'organization_id'),
        Index('idx_project_status', 'status'),
    )


class Task(Base):
    """Tasks within projects"""
    __tablename__ = "tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Task Details
    estimated_hours = Column(Float, nullable=True)
    actual_hours = Column(Float, default=0)
    priority = Column(String(20), default="medium")
    status = Column(String(50), default="todo")
    
    # AI Predictions
    ai_estimated_hours = Column(Float, nullable=True)
    ai_completion_probability = Column(Float, nullable=True)
    
    # Dates
    due_date = Column(Date, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="tasks")
    assigned_to = relationship("User")
    time_entries = relationship("TimeEntry", back_populates="task")


class TimeEntry(Base):
    """Time tracking entries"""
    __tablename__ = "time_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True)
    
    # Time Data
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, default=0)
    
    # Description
    description = Column(Text, nullable=True)
    ai_generated_description = Column(Text, nullable=True)
    tags = Column(ARRAY(String), default=[])
    
    # Billing
    is_billable = Column(Boolean, default=True)
    hourly_rate = Column(Numeric(10, 2), nullable=True)
    
    # Tracking Source
    source = Column(String(50), default="manual")  # manual, desktop, mobile, browser, auto
    device_id = Column(String(255), nullable=True)
    
    # Geolocation
    location = Column(JSONB, nullable=True)  # {lat, lng, address}
    geofence_verified = Column(Boolean, default=False)
    
    # Blockchain (optional)
    blockchain_hash = Column(String(255), nullable=True)
    is_blockchain_verified = Column(Boolean, default=False)
    
    # Approval
    is_approved = Column(Boolean, nullable=True)
    approved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="time_entries")
    project = relationship("Project", back_populates="time_entries")
    task = relationship("Task", back_populates="time_entries")
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    screenshots = relationship("Screenshot", back_populates="time_entry")
    activities = relationship("Activity", back_populates="time_entry")
    
    __table_args__ = (
        Index('idx_time_entry_user', 'user_id'),
        Index('idx_time_entry_project', 'project_id'),
        Index('idx_time_entry_date', 'start_time'),
        Index('idx_time_entry_billable', 'is_billable'),
    )


class Screenshot(Base):
    """Screenshots captured during time tracking"""
    __tablename__ = "screenshots"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    time_entry_id = Column(UUID(as_uuid=True), ForeignKey("time_entries.id"), nullable=True)
    
    # File Storage
    file_path = Column(String(500), nullable=False)
    file_url = Column(String(500), nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    
    # Screenshot Analysis
    ocr_text = Column(Text, nullable=True)
    detected_apps = Column(JSONB, nullable=True)
    detected_urls = Column(ARRAY(String), nullable=True)
    activity_type = Column(Enum(ActivityType), nullable=True)
    
    # AI Analysis
    ai_description = Column(Text, nullable=True)
    ai_tags = Column(ARRAY(String), nullable=True)
    productivity_score = Column(Float, nullable=True)
    
    # Privacy
    is_blurred = Column(Boolean, default=False)
    blur_regions = Column(JSONB, nullable=True)
    is_deleted_by_user = Column(Boolean, default=False)
    
    captured_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="screenshots")
    time_entry = relationship("TimeEntry", back_populates="screenshots")
    
    __table_args__ = (
        Index('idx_screenshot_user', 'user_id'),
        Index('idx_screenshot_time_entry', 'time_entry_id'),
        Index('idx_screenshot_captured_at', 'captured_at'),
    )


class Activity(Base):
    """Activity tracking (apps, websites, keyboard/mouse)"""
    __tablename__ = "activities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    time_entry_id = Column(UUID(as_uuid=True), ForeignKey("time_entries.id"), nullable=True)
    
    # Activity Details
    app_name = Column(String(255), nullable=True)
    window_title = Column(String(500), nullable=True)
    url = Column(String(1000), nullable=True)
    category = Column(String(100), nullable=True)
    
    # Activity Metrics
    activity_type = Column(Enum(ActivityType), default=ActivityType.NEUTRAL)
    productivity_score = Column(Float, nullable=True)
    
    # Time
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, default=0)
    
    # Input Activity
    keyboard_strokes = Column(Integer, default=0)
    mouse_clicks = Column(Integer, default=0)
    mouse_distance = Column(Float, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="activities")
    time_entry = relationship("TimeEntry", back_populates="activities")
    
    __table_args__ = (
        Index('idx_activity_user', 'user_id'),
        Index('idx_activity_started_at', 'started_at'),
        Index('idx_activity_type', 'activity_type'),
    )


# ==================== AI MODELS ====================

class AIInsight(Base):
    """AI-generated insights and recommendations"""
    __tablename__ = "ai_insights"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    # Insight Details
    insight_type = Column(String(50), nullable=False)  # productivity, burnout, recommendation, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(20), default="medium")
    
    # Data
    data = Column(JSONB, nullable=True)
    metrics = Column(JSONB, nullable=True)
    
    # Actions
    actionable = Column(Boolean, default=False)
    action_taken = Column(Boolean, default=False)
    action_data = Column(JSONB, nullable=True)
    
    # Dates
    insight_date = Column(Date, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="ai_insights")
    
    __table_args__ = (
        Index('idx_ai_insight_user', 'user_id'),
        Index('idx_ai_insight_type', 'insight_type'),
        Index('idx_ai_insight_date', 'insight_date'),
    )


class AICoachingSession(Base):
    """AI coaching conversations"""
    __tablename__ = "ai_coaching_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Session Data
    messages = Column(JSONB, default=[])  # [{role, content, timestamp}]
    session_type = Column(String(50), default="general")  # general, productivity, wellness
    
    # Metrics
    message_count = Column(Integer, default=0)
    satisfaction_rating = Column(Integer, nullable=True)
    
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index('idx_coaching_user', 'user_id'),
    )


# ==================== HRMS MODELS ====================

class LeaveRequest(Base):
    """Leave/PTO requests"""
    __tablename__ = "leave_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    # Leave Details
    leave_type = Column(String(50), nullable=False)  # vacation, sick, personal, etc.
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    days_count = Column(Float, nullable=False)
    reason = Column(Text, nullable=True)
    
    # Status
    status = Column(Enum(LeaveStatus), default=LeaveStatus.PENDING)
    reviewed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="leave_requests")
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_id])
    
    __table_args__ = (
        Index('idx_leave_user', 'user_id'),
        Index('idx_leave_status', 'status'),
        Index('idx_leave_dates', 'start_date', 'end_date'),
    )


class Expense(Base):
    """Expense tracking and reimbursement"""
    __tablename__ = "expenses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    
    # Expense Details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    
    # Receipt
    receipt_url = Column(String(500), nullable=True)
    receipt_ocr_data = Column(JSONB, nullable=True)
    
    # Status
    status = Column(Enum(ExpenseStatus), default=ExpenseStatus.PENDING)
    approved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Dates
    expense_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="expenses")
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    
    __table_args__ = (
        Index('idx_expense_user', 'user_id'),
        Index('idx_expense_status', 'status'),
        Index('idx_expense_date', 'expense_date'),
    )


class Payroll(Base):
    """Payroll records"""
    __tablename__ = "payroll"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    # Pay Period
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    pay_date = Column(Date, nullable=False)
    
    # Amounts
    gross_pay = Column(Numeric(12, 2), nullable=False)
    net_pay = Column(Numeric(12, 2), nullable=False)
    
    # Breakdown
    regular_hours = Column(Float, default=0)
    overtime_hours = Column(Float, default=0)
    bonus = Column(Numeric(10, 2), default=0)
    
    # Deductions
    tax_deductions = Column(JSONB, default={})
    other_deductions = Column(JSONB, default={})
    
    # Payment
    payment_method = Column(String(50), default="direct_deposit")
    payment_reference = Column(String(255), nullable=True)
    status = Column(Enum(PayrollStatus), default=PayrollStatus.PENDING)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index('idx_payroll_user', 'user_id'),
        Index('idx_payroll_period', 'period_start', 'period_end'),
        Index('idx_payroll_status', 'status'),
    )


# ==================== BILLING & PAYMENTS ====================

class Invoice(Base):
    """Client invoices"""
    __tablename__ = "invoices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    
    # Invoice Details
    invoice_number = Column(String(50), unique=True, nullable=False)
    client_name = Column(String(255), nullable=False)
    client_email = Column(String(255), nullable=False)
    
    # Amounts
    subtotal = Column(Numeric(12, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="USD")
    
    # Status
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    
    # Dates
    issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    paid_date = Column(Date, nullable=True)
    
    # Payment
    payment_method = Column(String(50), nullable=True)
    payment_reference = Column(String(255), nullable=True)
    stripe_invoice_id = Column(String(255), nullable=True)
    
    # Line Items
    line_items = Column(JSONB, default=[])
    
    # Notes
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_invoice_org', 'organization_id'),
        Index('idx_invoice_status', 'status'),
        Index('idx_invoice_due_date', 'due_date'),
    )


# ==================== INTEGRATIONS ====================

class Integration(Base):
    """Third-party integrations"""
    __tablename__ = "integrations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    # Integration Details
    integration_type = Column(String(50), nullable=False)  # slack, google, jira, etc.
    name = Column(String(255), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_configured = Column(Boolean, default=False)
    
    # Credentials (encrypted)
    credentials = Column(JSONB, nullable=True)
    config = Column(JSONB, default={})
    
    # OAuth
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_synced_at = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index('idx_integration_org', 'organization_id'),
        Index('idx_integration_type', 'integration_type'),
    )


# ==================== COMPLIANCE & AUDIT ====================

class AuditLog(Base):
    """Audit trail for compliance"""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Action Details
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(255), nullable=True)
    
    # Changes
    old_values = Column(JSONB, nullable=True)
    new_values = Column(JSONB, nullable=True)
    
    # Context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    metadata = Column(JSONB, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('idx_audit_org', 'organization_id'),
        Index('idx_audit_user', 'user_id'),
        Index('idx_audit_action', 'action'),
        Index('idx_audit_created', 'created_at'),
    )


# ==================== NOTIFICATIONS ====================

class Notification(Base):
    """User notifications"""
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Notification Details
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)
    
    # Status
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    
    # Action
    action_url = Column(String(500), nullable=True)
    action_data = Column(JSONB, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_notification_user', 'user_id'),
        Index('idx_notification_read', 'is_read'),
    )
