"""
Settings Router - REAL IMPLEMENTATION
Complete settings and feature flags management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from pydantic import BaseModel

from app.database.session import get_db
from app.auth.jwt_manager import get_current_user
from app.auth.rbac import require_permission, Permission
from app.logging.logging_config import log_audit_event
from app.crud import setting as setting_crud

router = APIRouter()

class SettingUpdate(BaseModel):
    category: str
    key: str
    value: Any

class SettingsBatchUpdate(BaseModel):
    settings: Dict[str, Dict[str, Any]]

class FeatureFlagUpdate(BaseModel):
    name: str
    enabled: bool

@router.get("/")
@require_permission(Permission.SETTINGS_READ)
async def get_settings(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all settings - REAL DATABASE QUERY"""
    tenant_id = current_user['tenant_id']
    
    settings = setting_crud.get_all_settings(db, tenant_id)
    
    return settings

@router.get("/{category}")
@require_permission(Permission.SETTINGS_READ)
async def get_settings_by_category(
    category: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get settings by category - REAL DATABASE QUERY"""
    tenant_id = current_user['tenant_id']
    
    settings = setting_crud.get_settings_by_category(db, tenant_id, category)
    
    result = {s.key: s.value for s in settings}
    return result

@router.put("/")
@require_permission(Permission.SETTINGS_UPDATE)
async def update_settings(
    batch: SettingsBatchUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update multiple settings - REAL DATABASE UPDATE"""
    tenant_id = current_user['tenant_id']
    user_id = current_user['id']
    
    count = setting_crud.batch_update_settings(
        db, tenant_id, batch.settings, user_id
    )
    
    log_audit_event(
        event_type='settings_update',
        user_id=user_id,
        tenant_id=tenant_id,
        resource='settings',
        action='update',
        details={'count': count}
    )
    
    return {'message': f'Updated {count} settings', 'count': count}

@router.put("/single")
@require_permission(Permission.SETTINGS_UPDATE)
async def update_single_setting(
    setting: SettingUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update single setting - REAL DATABASE UPDATE"""
    tenant_id = current_user['tenant_id']
    user_id = current_user['id']
    
    updated = setting_crud.update_setting(
        db, tenant_id, setting.category, setting.key, setting.value, user_id
    )
    
    log_audit_event(
        event_type='setting_update',
        user_id=user_id,
        tenant_id=tenant_id,
        resource='settings',
        action='update',
        details={'category': setting.category, 'key': setting.key}
    )
    
    return {'message': 'Setting updated', 'setting': {
        'category': updated.category,
        'key': updated.key,
        'value': updated.value
    }}

# Feature Flags

@router.get("/feature-flags/all")
@require_permission(Permission.SETTINGS_READ)
async def get_feature_flags(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all feature flags - REAL DATABASE QUERY"""
    tenant_id = current_user['tenant_id']
    
    flags = setting_crud.get_all_feature_flags(db, tenant_id)
    
    return flags

@router.put("/feature-flags")
@require_permission(Permission.SETTINGS_UPDATE)
async def update_feature_flag(
    flag: FeatureFlagUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update feature flag - REAL DATABASE UPDATE"""
    tenant_id = current_user['tenant_id']
    user_id = current_user['id']
    
    updated = setting_crud.update_feature_flag(
        db, flag.name, flag.enabled, tenant_id
    )
    
    log_audit_event(
        event_type='feature_flag_update',
        user_id=user_id,
        tenant_id=tenant_id,
        resource='feature_flags',
        action='update',
        details={'flag': flag.name, 'enabled': flag.enabled}
    )
    
    return {'message': 'Feature flag updated', 'flag': {
        'name': updated.name,
        'enabled': updated.enabled
    }}

@router.get("/feature-flags/{name}")
async def check_feature_flag(
    name: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if feature is enabled - REAL DATABASE QUERY"""
    tenant_id = current_user['tenant_id']
    
    enabled = setting_crud.is_feature_enabled(db, name, tenant_id)
    
    return {'name': name, 'enabled': enabled}
