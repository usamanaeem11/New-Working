"""
Add settings and feature_flags tables

Revision ID: 003
Revises: 002
Create Date: 2026-01-08
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Add settings and feature_flags tables"""
    
    # Settings table
    op.create_table(
        'settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', postgresql.JSON(), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('is_public', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_settings_tenant_id', 'settings', ['tenant_id'])
    op.create_index('ix_settings_category', 'settings', ['category'])
    op.create_index('ix_settings_key', 'settings', ['key'])
    op.create_index('ix_settings_tenant_category_key', 'settings', ['tenant_id', 'category', 'key'], unique=True)
    
    # Feature flags table
    op.create_table(
        'feature_flags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('enabled', sa.Boolean(), server_default='false'),
        sa.Column('rollout_percentage', sa.Integer(), server_default='100'),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_feature_flags_tenant_id', 'feature_flags', ['tenant_id'])
    op.create_index('ix_feature_flags_name', 'feature_flags', ['name'])
    op.create_index('ix_feature_flags_name_tenant', 'feature_flags', ['name', 'tenant_id'], unique=True)

def downgrade() -> None:
    """Drop settings and feature_flags tables"""
    op.drop_table('feature_flags')
    op.drop_table('settings')
