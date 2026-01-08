"""
Settings CRUD Operations
Real settings management with database
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Dict, Any, List, Optional

from app.models.setting import Setting, FeatureFlag

def get_setting(db: Session, tenant_id: int, category: str, key: str) -> Optional[Setting]:
    """Get specific setting"""
    return db.query(Setting).filter(
        and_(
            Setting.tenant_id == tenant_id,
            Setting.category == category,
            Setting.key == key
        )
    ).first()

def get_settings_by_category(db: Session, tenant_id: int, category: str) -> List[Setting]:
    """Get all settings in category"""
    return db.query(Setting).filter(
        and_(
            Setting.tenant_id == tenant_id,
            Setting.category == category
        )
    ).all()

def get_all_settings(db: Session, tenant_id: int) -> Dict[str, Dict[str, Any]]:
    """Get all settings organized by category"""
    settings = db.query(Setting).filter(Setting.tenant_id == tenant_id).all()
    
    result = {}
    for setting in settings:
        if setting.category not in result:
            result[setting.category] = {}
        result[setting.category][setting.key] = setting.value
    
    return result

def update_setting(
    db: Session,
    tenant_id: int,
    category: str,
    key: str,
    value: Any,
    updated_by: int
) -> Setting:
    """Update or create setting"""
    setting = get_setting(db, tenant_id, category, key)
    
    if setting:
        # Update existing
        setting.value = value
        setting.updated_by = updated_by
    else:
        # Create new
        setting = Setting(
            tenant_id=tenant_id,
            category=category,
            key=key,
            value=value,
            updated_by=updated_by
        )
        db.add(setting)
    
    db.commit()
    db.refresh(setting)
    return setting

def batch_update_settings(
    db: Session,
    tenant_id: int,
    settings_dict: Dict[str, Dict[str, Any]],
    updated_by: int
) -> int:
    """Update multiple settings at once"""
    count = 0
    
    for category, settings in settings_dict.items():
        for key, value in settings.items():
            update_setting(db, tenant_id, category, key, value, updated_by)
            count += 1
    
    return count

# Feature Flags

def get_feature_flag(db: Session, name: str, tenant_id: Optional[int] = None) -> Optional[FeatureFlag]:
    """Get feature flag"""
    query = db.query(FeatureFlag).filter(FeatureFlag.name == name)
    
    if tenant_id:
        # Check tenant-specific first
        flag = query.filter(FeatureFlag.tenant_id == tenant_id).first()
        if flag:
            return flag
    
    # Check global
    return query.filter(FeatureFlag.tenant_id == None).first()

def get_all_feature_flags(db: Session, tenant_id: Optional[int] = None) -> Dict[str, bool]:
    """Get all feature flags"""
    query = db.query(FeatureFlag)
    
    if tenant_id:
        query = query.filter(
            (FeatureFlag.tenant_id == tenant_id) | (FeatureFlag.tenant_id == None)
        )
    else:
        query = query.filter(FeatureFlag.tenant_id == None)
    
    flags = query.all()
    
    return {flag.name: flag.enabled for flag in flags}

def update_feature_flag(
    db: Session,
    name: str,
    enabled: bool,
    tenant_id: Optional[int] = None
) -> FeatureFlag:
    """Update or create feature flag"""
    flag = get_feature_flag(db, name, tenant_id)
    
    if flag:
        flag.enabled = enabled
    else:
        flag = FeatureFlag(
            name=name,
            enabled=enabled,
            tenant_id=tenant_id
        )
        db.add(flag)
    
    db.commit()
    db.refresh(flag)
    return flag

def is_feature_enabled(db: Session, name: str, tenant_id: Optional[int] = None) -> bool:
    """Check if feature is enabled"""
    flag = get_feature_flag(db, name, tenant_id)
    return flag.enabled if flag else False
