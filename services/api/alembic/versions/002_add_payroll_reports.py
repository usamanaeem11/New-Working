"""
Add payroll and reports tables

Revision ID: 002
Revises: 001
Create Date: 2026-01-08
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Add payroll_runs, pay_stubs, and reports tables"""
    
    # Payroll runs table
    op.create_table(
        'payroll_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('pay_period_start', sa.Date(), nullable=False),
        sa.Column('pay_period_end', sa.Date(), nullable=False),
        sa.Column('pay_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='draft'),
        sa.Column('total_amount', sa.Float(), server_default='0'),
        sa.Column('total_hours', sa.Float(), server_default='0'),
        sa.Column('employee_count', sa.Integer(), server_default='0'),
        sa.Column('processed_by', sa.Integer(), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['processed_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_payroll_runs_tenant_id', 'payroll_runs', ['tenant_id'])
    op.create_index('ix_payroll_runs_status', 'payroll_runs', ['status'])
    
    # Pay stubs table
    op.create_table(
        'pay_stubs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('payroll_run_id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('regular_hours', sa.Float(), server_default='0'),
        sa.Column('overtime_hours', sa.Float(), server_default='0'),
        sa.Column('total_hours', sa.Float(), server_default='0'),
        sa.Column('regular_pay', sa.Float(), server_default='0'),
        sa.Column('overtime_pay', sa.Float(), server_default='0'),
        sa.Column('gross_pay', sa.Float(), server_default='0'),
        sa.Column('tax_federal', sa.Float(), server_default='0'),
        sa.Column('tax_state', sa.Float(), server_default='0'),
        sa.Column('tax_social_security', sa.Float(), server_default='0'),
        sa.Column('tax_medicare', sa.Float(), server_default='0'),
        sa.Column('deductions_other', sa.Float(), server_default='0'),
        sa.Column('total_deductions', sa.Float(), server_default='0'),
        sa.Column('net_pay', sa.Float(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['payroll_run_id'], ['payroll_runs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_pay_stubs_tenant_id', 'pay_stubs', ['tenant_id'])
    op.create_index('ix_pay_stubs_payroll_run_id', 'pay_stubs', ['payroll_run_id'])
    op.create_index('ix_pay_stubs_employee_id', 'pay_stubs', ['employee_id'])
    
    # Reports table
    op.create_table(
        'reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('report_type', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('data', postgresql.JSON(), nullable=False),
        sa.Column('generated_by', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='completed'),
        sa.Column('format', sa.String(length=20), server_default='json'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['generated_by'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_reports_tenant_id', 'reports', ['tenant_id'])
    op.create_index('ix_reports_report_type', 'reports', ['report_type'])
    op.create_index('ix_reports_created_at', 'reports', ['created_at'])

def downgrade() -> None:
    """Drop payroll and reports tables"""
    op.drop_table('reports')
    op.drop_table('pay_stubs')
    op.drop_table('payroll_runs')
