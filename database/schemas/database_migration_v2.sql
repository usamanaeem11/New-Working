-- ============================================================
-- DATABASE MIGRATION V2.0
-- Adding 6 New Features: Client Portal, Resource Planning,
-- Workflows, BI, Wellness, Performance Reviews
-- Date: 2026-01-05
-- Author: WorkingTracker Development Team
-- ============================================================

BEGIN;

-- ============================================================
-- FEATURE 1: CLIENT PORTAL
-- ============================================================

CREATE TABLE IF NOT EXISTS client_access (
    access_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_email VARCHAR(255) UNIQUE NOT NULL,
    organization_id UUID NOT NULL,
    client_name VARCHAR(255),
    permissions JSONB DEFAULT '["view_projects", "approve_timesheets"]',
    is_active BOOLEAN DEFAULT true,
    invited_by UUID,
    invited_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    password_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS client_invitations (
    invitation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL,
    organization_id UUID NOT NULL,
    invitation_token VARCHAR(255) UNIQUE,
    permissions JSONB,
    expires_at TIMESTAMP,
    accepted_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending', -- pending, accepted, expired
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS client_feedback (
    feedback_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES client_access(access_id) ON DELETE CASCADE,
    project_id UUID,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    category VARCHAR(50), -- 'service', 'communication', 'quality', 'timeliness'
    comments TEXT,
    submitted_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- FEATURE 2: RESOURCE PLANNING
-- ============================================================

CREATE TABLE IF NOT EXISTS skills (
    skill_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) UNIQUE NOT NULL,
    category VARCHAR(100), -- 'programming', 'design', 'management', etc.
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS employee_skills (
    employee_id UUID NOT NULL,
    skill_id UUID REFERENCES skills(skill_id) ON DELETE CASCADE,
    proficiency_level INTEGER CHECK (proficiency_level BETWEEN 1 AND 5),
    years_experience DECIMAL(4,1),
    certified BOOLEAN DEFAULT false,
    last_used DATE,
    added_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (employee_id, skill_id)
);

CREATE TABLE IF NOT EXISTS resource_allocations (
    allocation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID NOT NULL,
    project_id UUID NOT NULL,
    role VARCHAR(100), -- 'developer', 'designer', 'qa', etc.
    hours_allocated DECIMAL(10,2),
    start_date DATE,
    end_date DATE,
    priority INTEGER DEFAULT 1, -- 1=low, 2=medium, 3=high
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS employee_availability (
    availability_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID NOT NULL,
    date DATE NOT NULL,
    hours_available DECIMAL(4,2), -- Max working hours for the day
    hours_allocated DECIMAL(4,2) DEFAULT 0,
    utilization_percentage DECIMAL(5,2),
    notes TEXT,
    UNIQUE(employee_id, date)
);

-- ============================================================
-- FEATURE 3: APPROVAL WORKFLOWS
-- ============================================================

CREATE TABLE IF NOT EXISTS workflow_definitions (
    workflow_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    trigger_type VARCHAR(50), -- 'expense', 'leave', 'timesheet', 'invoice', 'purchase_order'
    is_active BOOLEAN DEFAULT true,
    created_by UUID,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS approval_chains (
    chain_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID REFERENCES workflow_definitions(workflow_id) ON DELETE CASCADE,
    step_order INTEGER NOT NULL,
    approver_role VARCHAR(100), -- 'Manager', 'Finance', etc.
    approver_user_id UUID, -- Specific user (optional, overrides role)
    approval_conditions JSONB, -- e.g., {"amount": {">": 1000}}
    sla_hours INTEGER DEFAULT 24, -- Time limit for approval
    escalation_user_id UUID, -- Who to escalate to if SLA breached
    is_required BOOLEAN DEFAULT true,
    is_parallel BOOLEAN DEFAULT false, -- Multiple approvers at same level
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS workflow_instances (
    instance_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID REFERENCES workflow_definitions(workflow_id),
    entity_type VARCHAR(50), -- What is being approved
    entity_id UUID, -- ID of the entity
    current_step INTEGER DEFAULT 1,
    status VARCHAR(50) DEFAULT 'pending', -- pending, approved, rejected, escalated
    initiated_by UUID,
    initiated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    metadata JSONB -- Additional context data
);

CREATE TABLE IF NOT EXISTS approval_history (
    history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instance_id UUID REFERENCES workflow_instances(instance_id) ON DELETE CASCADE,
    step_number INTEGER,
    approver_id UUID,
    action VARCHAR(50), -- 'approved', 'rejected', 'delegated', 'escalated'
    comments TEXT,
    delegated_to UUID, -- If delegated
    action_timestamp TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- FEATURE 4: BUSINESS INTELLIGENCE
-- ============================================================

CREATE TABLE IF NOT EXISTS kpi_definitions (
    kpi_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    formula TEXT, -- SQL query or calculation formula
    unit VARCHAR(50), -- 'percentage', 'currency', 'number', 'hours'
    target_value DECIMAL(15,2),
    warning_threshold DECIMAL(15,2),
    critical_threshold DECIMAL(15,2),
    calculation_frequency VARCHAR(50), -- 'daily', 'weekly', 'monthly'
    is_active BOOLEAN DEFAULT true,
    created_by UUID,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS kpi_values (
    value_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kpi_id UUID REFERENCES kpi_definitions(kpi_id) ON DELETE CASCADE,
    period_start DATE,
    period_end DATE,
    calculated_value DECIMAL(15,2),
    status VARCHAR(50), -- 'normal', 'warning', 'critical'
    calculated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS trend_analysis (
    trend_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name VARCHAR(255),
    period VARCHAR(50), -- 'week', 'month', 'quarter', 'year'
    historical_values JSONB, -- Array of {period, value}
    trend_direction VARCHAR(20), -- 'up', 'down', 'stable'
    predicted_value DECIMAL(15,2),
    confidence_level DECIMAL(5,2), -- 0-100
    analysis_date TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS roi_calculations (
    calc_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID,
    total_revenue DECIMAL(15,2),
    total_cost DECIMAL(15,2),
    gross_profit DECIMAL(15,2),
    roi_percentage DECIMAL(5,2),
    payback_period_months INTEGER,
    npv DECIMAL(15,2), -- Net Present Value
    irr DECIMAL(5,2), -- Internal Rate of Return
    calculated_at TIMESTAMP DEFAULT NOW(),
    notes TEXT
);

CREATE TABLE IF NOT EXISTS custom_dashboards (
    dashboard_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255),
    user_id UUID,
    layout JSONB, -- Grid layout configuration
    widgets JSONB, -- Array of widget definitions
    is_shared BOOLEAN DEFAULT false,
    shared_with JSONB, -- Array of user IDs if partially shared
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- FEATURE 5: EMPLOYEE WELLNESS
-- ============================================================

CREATE TABLE IF NOT EXISTS wellness_checkins (
    checkin_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID NOT NULL,
    mood INTEGER CHECK (mood BETWEEN 1 AND 5),
    stress_level INTEGER CHECK (stress_level BETWEEN 1 AND 5),
    energy_level INTEGER CHECK (energy_level BETWEEN 1 AND 5),
    sleep_hours DECIMAL(3,1),
    notes TEXT,
    checkin_timestamp TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stress_indicators (
    indicator_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID NOT NULL,
    indicator_type VARCHAR(50), -- 'overtime', 'missed_breaks', 'rapid_activity', 'after_hours', 'long_sessions'
    metric_value DECIMAL(10,2),
    threshold_exceeded BOOLEAN,
    detected_at TIMESTAMP DEFAULT NOW(),
    acknowledged BOOLEAN DEFAULT false,
    acknowledged_by UUID,
    acknowledged_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS wellness_goals (
    goal_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID NOT NULL,
    goal_type VARCHAR(50), -- 'exercise', 'meditation', 'breaks', 'sleep', 'hydration'
    target_value DECIMAL(10,2),
    current_progress DECIMAL(10,2) DEFAULT 0,
    frequency VARCHAR(20), -- 'daily', 'weekly', 'monthly'
    start_date DATE,
    end_date DATE,
    status VARCHAR(20) DEFAULT 'active', -- active, completed, abandoned
    streak_days INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS wellness_resources (
    resource_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255),
    category VARCHAR(50), -- 'mental_health', 'exercise', 'nutrition', 'sleep', 'stress_management'
    resource_type VARCHAR(50), -- 'article', 'video', 'tool', 'service'
    url TEXT,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS wellness_challenges (
    challenge_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255),
    challenge_type VARCHAR(50), -- 'steps', 'exercise', 'meditation', 'water'
    goal_value DECIMAL(10,2),
    start_date DATE,
    end_date DATE,
    is_team_challenge BOOLEAN DEFAULT false,
    created_by UUID,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS wellness_challenge_participants (
    participant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    challenge_id UUID REFERENCES wellness_challenges(challenge_id) ON DELETE CASCADE,
    employee_id UUID NOT NULL,
    current_value DECIMAL(10,2) DEFAULT 0,
    rank INTEGER,
    joined_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- FEATURE 6: PERFORMANCE REVIEWS & OKRs
-- ============================================================

CREATE TABLE IF NOT EXISTS okrs (
    okr_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID,
    team_id UUID,
    owner_id UUID,
    objective TEXT NOT NULL,
    key_results JSONB, -- Array of {description, target, current, unit, status}
    quarter VARCHAR(10), -- e.g., '2024-Q1'
    year INTEGER,
    parent_okr_id UUID REFERENCES okrs(okr_id), -- For cascading OKRs
    progress_percentage DECIMAL(5,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'on_track', -- on_track, at_risk, off_track, completed
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS goals (
    goal_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID NOT NULL,
    manager_id UUID,
    goal_type VARCHAR(50), -- 'performance', 'development', 'behavioral'
    description TEXT,
    success_criteria TEXT,
    target_date DATE,
    progress_percentage DECIMAL(5,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active', -- active, completed, abandoned, on_hold
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS review_cycles (
    cycle_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255), -- e.g., 'Q4 2024 Performance Review'
    cycle_type VARCHAR(50), -- 'annual', 'quarterly', 'probation', 'mid_year'
    start_date DATE,
    end_date DATE,
    review_template_id UUID,
    status VARCHAR(20) DEFAULT 'planned', -- planned, active, completed
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS performance_reviews (
    review_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cycle_id UUID REFERENCES review_cycles(cycle_id),
    employee_id UUID NOT NULL,
    reviewer_id UUID NOT NULL,
    review_type VARCHAR(50), -- 'self', 'manager', 'peer', '360'
    overall_rating INTEGER CHECK (overall_rating BETWEEN 1 AND 5),
    competency_ratings JSONB, -- {competency_name: rating}
    strengths TEXT,
    areas_for_improvement TEXT,
    goals_for_next_period TEXT,
    status VARCHAR(20) DEFAULT 'draft', -- draft, submitted, completed
    review_date DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS review_feedback (
    feedback_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id UUID REFERENCES performance_reviews(review_id) ON DELETE CASCADE,
    feedback_type VARCHAR(50), -- 'peer', 'direct_report', 'manager', 'self'
    reviewer_id UUID,
    feedback_text TEXT,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    is_anonymous BOOLEAN DEFAULT false,
    submitted_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- INDEXES FOR PERFORMANCE OPTIMIZATION
-- ============================================================

-- Client Portal Indexes
CREATE INDEX IF NOT EXISTS idx_client_access_org ON client_access(organization_id);
CREATE INDEX IF NOT EXISTS idx_client_access_email ON client_access(client_email);
CREATE INDEX IF NOT EXISTS idx_client_invitations_email ON client_invitations(email);
CREATE INDEX IF NOT EXISTS idx_client_invitations_token ON client_invitations(invitation_token);
CREATE INDEX IF NOT EXISTS idx_client_feedback_client ON client_feedback(client_id);
CREATE INDEX IF NOT EXISTS idx_client_feedback_project ON client_feedback(project_id);

-- Resource Planning Indexes
CREATE INDEX IF NOT EXISTS idx_skills_category ON skills(category);
CREATE INDEX IF NOT EXISTS idx_skills_name ON skills(name);
CREATE INDEX IF NOT EXISTS idx_employee_skills_employee ON employee_skills(employee_id);
CREATE INDEX IF NOT EXISTS idx_employee_skills_skill ON employee_skills(skill_id);
CREATE INDEX IF NOT EXISTS idx_resource_allocations_employee ON resource_allocations(employee_id);
CREATE INDEX IF NOT EXISTS idx_resource_allocations_project ON resource_allocations(project_id);
CREATE INDEX IF NOT EXISTS idx_resource_allocations_dates ON resource_allocations(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_employee_availability_employee ON employee_availability(employee_id);
CREATE INDEX IF NOT EXISTS idx_employee_availability_date ON employee_availability(date);

-- Workflow Indexes
CREATE INDEX IF NOT EXISTS idx_workflow_definitions_trigger ON workflow_definitions(trigger_type);
CREATE INDEX IF NOT EXISTS idx_workflow_definitions_active ON workflow_definitions(is_active);
CREATE INDEX IF NOT EXISTS idx_approval_chains_workflow ON approval_chains(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_instances_workflow ON workflow_instances(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_instances_status ON workflow_instances(status);
CREATE INDEX IF NOT EXISTS idx_workflow_instances_entity ON workflow_instances(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_approval_history_instance ON approval_history(instance_id);
CREATE INDEX IF NOT EXISTS idx_approval_history_approver ON approval_history(approver_id);

-- Business Intelligence Indexes
CREATE INDEX IF NOT EXISTS idx_kpi_definitions_active ON kpi_definitions(is_active);
CREATE INDEX IF NOT EXISTS idx_kpi_values_kpi ON kpi_values(kpi_id);
CREATE INDEX IF NOT EXISTS idx_kpi_values_period ON kpi_values(period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_trend_analysis_metric ON trend_analysis(metric_name);
CREATE INDEX IF NOT EXISTS idx_roi_calculations_project ON roi_calculations(project_id);
CREATE INDEX IF NOT EXISTS idx_custom_dashboards_user ON custom_dashboards(user_id);

-- Wellness Indexes
CREATE INDEX IF NOT EXISTS idx_wellness_checkins_employee ON wellness_checkins(employee_id);
CREATE INDEX IF NOT EXISTS idx_wellness_checkins_timestamp ON wellness_checkins(checkin_timestamp);
CREATE INDEX IF NOT EXISTS idx_stress_indicators_employee ON stress_indicators(employee_id);
CREATE INDEX IF NOT EXISTS idx_stress_indicators_type ON stress_indicators(indicator_type);
CREATE INDEX IF NOT EXISTS idx_wellness_goals_employee ON wellness_goals(employee_id);
CREATE INDEX IF NOT EXISTS idx_wellness_goals_status ON wellness_goals(status);
CREATE INDEX IF NOT EXISTS idx_wellness_challenge_participants_challenge ON wellness_challenge_participants(challenge_id);

-- Performance Reviews Indexes
CREATE INDEX IF NOT EXISTS idx_okrs_owner ON okrs(owner_id);
CREATE INDEX IF NOT EXISTS idx_okrs_team ON okrs(team_id);
CREATE INDEX IF NOT EXISTS idx_okrs_quarter ON okrs(quarter, year);
CREATE INDEX IF NOT EXISTS idx_okrs_parent ON okrs(parent_okr_id);
CREATE INDEX IF NOT EXISTS idx_goals_employee ON goals(employee_id);
CREATE INDEX IF NOT EXISTS idx_goals_manager ON goals(manager_id);
CREATE INDEX IF NOT EXISTS idx_goals_status ON goals(status);
CREATE INDEX IF NOT EXISTS idx_review_cycles_status ON review_cycles(status);
CREATE INDEX IF NOT EXISTS idx_performance_reviews_cycle ON performance_reviews(cycle_id);
CREATE INDEX IF NOT EXISTS idx_performance_reviews_employee ON performance_reviews(employee_id);
CREATE INDEX IF NOT EXISTS idx_performance_reviews_reviewer ON performance_reviews(reviewer_id);
CREATE INDEX IF NOT EXISTS idx_review_feedback_review ON review_feedback(review_id);

COMMIT;

-- ============================================================
-- POST-MIGRATION NOTES
-- ============================================================
-- 
-- 1. All tables created with UUID primary keys for scalability
-- 2. Proper foreign key relationships with CASCADE deletes where appropriate
-- 3. Indexes created for all frequently queried columns
-- 4. JSONB fields used for flexible data structures
-- 5. Check constraints for data validation
-- 6. Timestamps for audit trails
--
-- Next Steps:
-- 1. Update server.py to register new route modules
-- 2. Create frontend pages for each feature
-- 3. Update RBAC permissions to include new features
-- 4. Test all endpoints
-- 5. Deploy to production
--
-- ============================================================
