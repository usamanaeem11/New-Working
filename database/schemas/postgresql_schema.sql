-- ============================================
-- COMPLETE POSTGRESQL MIGRATION SCRIPT
-- Migrating from Supabase to Pure PostgreSQL
-- For: workingtracker.com on Contabo VPS
-- ============================================

-- Create database and user (run as postgres user)
-- CREATE DATABASE workingtracker;
-- CREATE USER workingtracker_user WITH ENCRYPTED PASSWORD 'ChangeMeToStrongPassword123!';
-- GRANT ALL PRIVILEGES ON DATABASE workingtracker TO workingtracker_user;

\c workingtracker;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================
-- CORE TABLES
-- ============================================

-- Organizations (companies)
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    
    -- White-label support
    is_white_label BOOLEAN DEFAULT FALSE,
    parent_org_id UUID REFERENCES organizations(id),
    custom_domain VARCHAR(255),
    custom_branding JSONB,
    
    -- Subscription
    subscription_tier VARCHAR(50) DEFAULT 'free',
    subscription_status VARCHAR(50) DEFAULT 'trial',
    trial_ends_at TIMESTAMP,
    subscription_started_at TIMESTAMP,
    
    -- Billing
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    billing_email VARCHAR(255),
    
    -- Settings
    settings JSONB DEFAULT '{}',
    timezone VARCHAR(50) DEFAULT 'UTC',
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Compliance
    industry VARCHAR(100),
    compliance_requirements TEXT[],
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_org_slug ON organizations(slug);
CREATE INDEX idx_org_subscription ON organizations(subscription_tier, subscription_status);

-- Users/Employees
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Basic Info
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    full_name VARCHAR(255) NOT NULL,
    avatar_url VARCHAR(500),
    
    -- Role & Permissions
    role VARCHAR(50) DEFAULT 'employee',
    permissions JSONB DEFAULT '{}',
    
    -- OAuth
    google_id VARCHAR(255) UNIQUE,
    microsoft_id VARCHAR(255) UNIQUE,
    
    -- Employment Details
    employee_id VARCHAR(50) UNIQUE,
    department VARCHAR(100),
    job_title VARCHAR(100),
    hire_date DATE,
    termination_date DATE,
    
    -- Compensation
    hourly_rate DECIMAL(10, 2),
    salary DECIMAL(12, 2),
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Work Schedule
    work_hours_per_week INTEGER DEFAULT 40,
    work_days TEXT[] DEFAULT ARRAY['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
    shift_start TIME,
    shift_end TIME,
    
    -- Time Tracking Settings
    auto_track BOOLEAN DEFAULT FALSE,
    screenshot_enabled BOOLEAN DEFAULT TRUE,
    screenshot_interval INTEGER DEFAULT 600,
    activity_tracking BOOLEAN DEFAULT TRUE,
    
    -- AI Settings
    ai_coaching_enabled BOOLEAN DEFAULT TRUE,
    ai_autopilot_enabled BOOLEAN DEFAULT FALSE,
    productivity_insights BOOLEAN DEFAULT TRUE,
    
    -- Wellness
    burnout_prevention BOOLEAN DEFAULT TRUE,
    break_reminders BOOLEAN DEFAULT TRUE,
    focus_mode_enabled BOOLEAN DEFAULT FALSE,
    
    -- Geolocation
    location_tracking_enabled BOOLEAN DEFAULT FALSE,
    last_known_location JSONB,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    last_active_at TIMESTAMP,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_org ON users(organization_id);
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_user_role ON users(role);

-- Teams
CREATE TABLE IF NOT EXISTS teams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    manager_id UUID REFERENCES users(id),
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Projects
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    client_name VARCHAR(255),
    project_code VARCHAR(50) UNIQUE,
    
    -- Status & Dates
    status VARCHAR(50) DEFAULT 'active',
    start_date DATE,
    end_date DATE,
    deadline DATE,
    
    -- Budget & Billing
    budget_hours FLOAT,
    budget_amount DECIMAL(12, 2),
    hourly_rate DECIMAL(10, 2),
    is_billable BOOLEAN DEFAULT TRUE,
    
    -- Settings
    color VARCHAR(7) DEFAULT '#3B82F6',
    settings JSONB DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_project_org ON projects(organization_id);
CREATE INDEX idx_project_status ON projects(status);

-- Tasks
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    assigned_to_id UUID REFERENCES users(id),
    
    -- Task Details
    estimated_hours FLOAT,
    actual_hours FLOAT DEFAULT 0,
    priority VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(50) DEFAULT 'todo',
    
    -- AI Predictions
    ai_estimated_hours FLOAT,
    ai_completion_probability FLOAT,
    
    -- Dates
    due_date DATE,
    completed_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Time Entries
CREATE TABLE IF NOT EXISTS time_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id),
    task_id UUID REFERENCES tasks(id),
    
    -- Time Data
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_seconds INTEGER DEFAULT 0,
    
    -- Description
    description TEXT,
    ai_generated_description TEXT,
    tags TEXT[],
    
    -- Billing
    is_billable BOOLEAN DEFAULT TRUE,
    hourly_rate DECIMAL(10, 2),
    
    -- Tracking Source
    source VARCHAR(50) DEFAULT 'manual',
    device_id VARCHAR(255),
    
    -- Geolocation
    location JSONB,
    geofence_verified BOOLEAN DEFAULT FALSE,
    
    -- Blockchain
    blockchain_hash VARCHAR(255),
    is_blockchain_verified BOOLEAN DEFAULT FALSE,
    
    -- Approval
    is_approved BOOLEAN,
    approved_by_id UUID REFERENCES users(id),
    approved_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_time_entry_user ON time_entries(user_id);
CREATE INDEX idx_time_entry_project ON time_entries(project_id);
CREATE INDEX idx_time_entry_date ON time_entries(start_time);
CREATE INDEX idx_time_entry_billable ON time_entries(is_billable);

-- Screenshots
CREATE TABLE IF NOT EXISTS screenshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    time_entry_id UUID REFERENCES time_entries(id),
    
    -- File Storage
    file_path VARCHAR(500) NOT NULL,
    file_url VARCHAR(500),
    thumbnail_url VARCHAR(500),
    file_size INTEGER,
    
    -- Screenshot Analysis
    ocr_text TEXT,
    detected_apps JSONB,
    detected_urls TEXT[],
    activity_type VARCHAR(50),
    
    -- AI Analysis
    ai_description TEXT,
    ai_tags TEXT[],
    productivity_score FLOAT,
    
    -- Privacy
    is_blurred BOOLEAN DEFAULT FALSE,
    blur_regions JSONB,
    is_deleted_by_user BOOLEAN DEFAULT FALSE,
    
    captured_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_screenshot_user ON screenshots(user_id);
CREATE INDEX idx_screenshot_time_entry ON screenshots(time_entry_id);
CREATE INDEX idx_screenshot_captured_at ON screenshots(captured_at);

-- Activities
CREATE TABLE IF NOT EXISTS activities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    time_entry_id UUID REFERENCES time_entries(id),
    
    -- Activity Details
    app_name VARCHAR(255),
    window_title VARCHAR(500),
    url VARCHAR(1000),
    category VARCHAR(100),
    
    -- Activity Metrics
    activity_type VARCHAR(50) DEFAULT 'neutral',
    productivity_score FLOAT,
    
    -- Time
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP,
    duration_seconds INTEGER DEFAULT 0,
    
    -- Input Activity
    keyboard_strokes INTEGER DEFAULT 0,
    mouse_clicks INTEGER DEFAULT 0,
    mouse_distance FLOAT DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_activity_user ON activities(user_id);
CREATE INDEX idx_activity_started_at ON activities(started_at);
CREATE INDEX idx_activity_type ON activities(activity_type);

-- ============================================
-- AI FEATURES TABLES
-- ============================================

-- AI Insights
CREATE TABLE IF NOT EXISTS ai_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Insight Details
    insight_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium',
    
    -- Data
    data JSONB,
    metrics JSONB,
    
    -- Actions
    actionable BOOLEAN DEFAULT FALSE,
    action_taken BOOLEAN DEFAULT FALSE,
    action_data JSONB,
    
    -- Dates
    insight_date DATE NOT NULL,
    expires_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_insight_user ON ai_insights(user_id);
CREATE INDEX idx_ai_insight_type ON ai_insights(insight_type);
CREATE INDEX idx_ai_insight_date ON ai_insights(insight_date);

-- AI Coaching Sessions
CREATE TABLE IF NOT EXISTS ai_coaching_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Session Data
    messages JSONB DEFAULT '[]',
    session_type VARCHAR(50) DEFAULT 'general',
    
    -- Metrics
    message_count INTEGER DEFAULT 0,
    satisfaction_rating INTEGER,
    
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP
);

CREATE INDEX idx_coaching_user ON ai_coaching_sessions(user_id);

-- ============================================
-- HRMS TABLES
-- ============================================

-- Leave Requests
CREATE TABLE IF NOT EXISTS leave_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Leave Details
    leave_type VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    days_count FLOAT NOT NULL,
    reason TEXT,
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending',
    reviewed_by_id UUID REFERENCES users(id),
    reviewed_at TIMESTAMP,
    review_notes TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_leave_user ON leave_requests(user_id);
CREATE INDEX idx_leave_status ON leave_requests(status);
CREATE INDEX idx_leave_dates ON leave_requests(start_date, end_date);

-- Expenses
CREATE TABLE IF NOT EXISTS expenses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id),
    
    -- Expense Details
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Receipt
    receipt_url VARCHAR(500),
    receipt_ocr_data JSONB,
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending',
    approved_by_id UUID REFERENCES users(id),
    approved_at TIMESTAMP,
    
    -- Dates
    expense_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_expense_user ON expenses(user_id);
CREATE INDEX idx_expense_status ON expenses(status);
CREATE INDEX idx_expense_date ON expenses(expense_date);

-- Payroll
CREATE TABLE IF NOT EXISTS payroll (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Pay Period
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    pay_date DATE NOT NULL,
    
    -- Amounts
    gross_pay DECIMAL(12, 2) NOT NULL,
    net_pay DECIMAL(12, 2) NOT NULL,
    
    -- Breakdown
    regular_hours FLOAT DEFAULT 0,
    overtime_hours FLOAT DEFAULT 0,
    bonus DECIMAL(10, 2) DEFAULT 0,
    
    -- Deductions
    tax_deductions JSONB DEFAULT '{}',
    other_deductions JSONB DEFAULT '{}',
    
    -- Payment
    payment_method VARCHAR(50) DEFAULT 'direct_deposit',
    payment_reference VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);

CREATE INDEX idx_payroll_user ON payroll(user_id);
CREATE INDEX idx_payroll_period ON payroll(period_start, period_end);
CREATE INDEX idx_payroll_status ON payroll(status);

-- ============================================
-- BILLING & PAYMENTS TABLES
-- ============================================

-- Invoices
CREATE TABLE IF NOT EXISTS invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id),
    
    -- Invoice Details
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    client_name VARCHAR(255) NOT NULL,
    client_email VARCHAR(255) NOT NULL,
    
    -- Amounts
    subtotal DECIMAL(12, 2) NOT NULL,
    tax_amount DECIMAL(10, 2) DEFAULT 0,
    total_amount DECIMAL(12, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Status
    status VARCHAR(50) DEFAULT 'draft',
    
    -- Dates
    issue_date DATE NOT NULL,
    due_date DATE NOT NULL,
    paid_date DATE,
    
    -- Payment
    payment_method VARCHAR(50),
    payment_reference VARCHAR(255),
    stripe_invoice_id VARCHAR(255),
    
    -- Line Items
    line_items JSONB DEFAULT '[]',
    
    -- Notes
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_invoice_org ON invoices(organization_id);
CREATE INDEX idx_invoice_status ON invoices(status);
CREATE INDEX idx_invoice_due_date ON invoices(due_date);

-- ============================================
-- INTEGRATION & SYSTEM TABLES
-- ============================================

-- Integrations
CREATE TABLE IF NOT EXISTS integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Integration Details
    integration_type VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_configured BOOLEAN DEFAULT FALSE,
    
    -- Credentials (encrypted)
    credentials JSONB,
    config JSONB DEFAULT '{}',
    
    -- OAuth
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_synced_at TIMESTAMP
);

CREATE INDEX idx_integration_org ON integrations(organization_id);
CREATE INDEX idx_integration_type ON integrations(integration_type);

-- Audit Logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    
    -- Action Details
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(255),
    
    -- Changes
    old_values JSONB,
    new_values JSONB,
    
    -- Context
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    metadata JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_org ON audit_logs(organization_id);
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_created ON audit_logs(created_at);

-- Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Notification Details
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    
    -- Status
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    
    -- Action
    action_url VARCHAR(500),
    action_data JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notification_user ON notifications(user_id);
CREATE INDEX idx_notification_read ON notifications(is_read);

-- ============================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_teams_updated_at BEFORE UPDATE ON teams FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_time_entries_updated_at BEFORE UPDATE ON time_entries FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_leave_requests_updated_at BEFORE UPDATE ON leave_requests FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_expenses_updated_at BEFORE UPDATE ON expenses FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_invoices_updated_at BEFORE UPDATE ON invoices FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_integrations_updated_at BEFORE UPDATE ON integrations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- GRANT PERMISSIONS
-- ============================================

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO workingtracker_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO workingtracker_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO workingtracker_user;
