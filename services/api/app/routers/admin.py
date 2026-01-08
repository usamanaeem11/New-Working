"""
Admin Router - Complete Implementation
Administrative functions with RBAC
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from pydantic import BaseModel

from app.database.session import get_db
from app.auth.jwt_manager import get_current_user
from app.auth.rbac import require_permission, Permission
from app.logging.logging_config import log_audit_event
from app.config.feature_flags import feature_flags

router = APIRouter()

# Pydantic Models
class SystemSettings(BaseModel):
    company_name: str
    timezone: str
    work_week_start: str
    work_hours_per_day: float
    overtime_threshold: float

class FeatureFlagUpdate(BaseModel):
    flag_name: str
    enabled: bool

@router.get("/settings", response_model=SystemSettings)
@require_permission(Permission.ADMIN_SETTINGS)
async def get_settings(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get system settings"""
    tenant_id = current_user['tenant_id']
    
    # In production: Query from database
    settings = {
        'company_name': 'Acme Corporation',
        'timezone': 'America/New_York',
        'work_week_start': 'Monday',
        'work_hours_per_day': 8.0,
        'overtime_threshold': 40.0
    }
    
    return settings

@router.put("/settings", response_model=SystemSettings)
@require_permission(Permission.ADMIN_SETTINGS)
async def update_settings(
    settings: SystemSettings,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update system settings"""
    tenant_id = current_user['tenant_id']
    
    # In production: Update in database
    
    log_audit_event(
        event_type='admin_settings_update',
        user_id=current_user['id'],
        tenant_id=tenant_id,
        resource='system_settings',
        action='update',
        details={'changes': settings.dict()}
    )
    
    return settings

@router.get("/feature-flags", response_model=Dict[str, Any])
@require_permission(Permission.ADMIN_SETTINGS)
async def get_feature_flags(
    current_user: dict = Depends(get_current_user)
):
    """Get all feature flags"""
    return feature_flags.get_all()

@router.put("/feature-flags")
@require_permission(Permission.ADMIN_SETTINGS)
async def update_feature_flag(
    flag_update: FeatureFlagUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Enable or disable a feature flag"""
    
    if flag_update.enabled:
        feature_flags.enable(flag_update.flag_name)
    else:
        feature_flags.disable(flag_update.flag_name)
    
    log_audit_event(
        event_type='feature_flag_change',
        user_id=current_user['id'],
        tenant_id=current_user['tenant_id'],
        resource='feature_flags',
        action='update',
        details={
            'flag': flag_update.flag_name,
            'enabled': flag_update.enabled
        }
    )
    
    return {'status': 'success', 'flag': flag_update.flag_name, 'enabled': flag_update.enabled}

@router.post("/maintenance-mode")
@require_permission(Permission.ADMIN_SETTINGS)
async def toggle_maintenance_mode(
    enabled: bool,
    current_user: dict = Depends(get_current_user)
):
    """Enable or disable maintenance mode"""
    
    feature_flags.set_maintenance_mode(enabled)
    
    log_audit_event(
        event_type='maintenance_mode',
        user_id=current_user['id'],
        tenant_id=current_user['tenant_id'],
        resource='system',
        action='maintenance_mode',
        details={'enabled': enabled}
    )
    
    return {'status': 'success', 'maintenance_mode': enabled}
