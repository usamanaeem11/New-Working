"""
Advanced Screenshot & Screen Recording Management
Features: Admin control, Random intervals, Separate systems
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime
import random
import uuid

router = APIRouter(prefix="/api/monitoring", tags=["Monitoring"])

# ============================================
# PYDANTIC MODELS
# ============================================

class ScreenshotConfig(BaseModel):
    interval_type: Literal["fixed", "random"]
    fixed_interval_seconds: Optional[int] = 600  # 10 minutes default
    random_min_seconds: Optional[int] = 60  # 1 minute
    random_max_seconds: Optional[int] = 900  # 15 minutes
    enabled: bool = True
    quality: int = 80  # 1-100
    capture_multi_monitor: bool = True
    privacy_blur_enabled: bool = True
    blur_regions: Optional[list] = []

class ScreenRecordingConfig(BaseModel):
    interval_type: Literal["fixed", "random"]
    fixed_interval_seconds: Optional[int] = 1800  # 30 minutes default
    random_min_seconds: Optional[int] = 600  # 10 minutes
    random_max_seconds: Optional[int] = 3600  # 60 minutes
    recording_duration_seconds: int = 300  # 5 minutes per recording
    enabled: bool = True
    quality: Literal["low", "medium", "high"] = "medium"
    fps: int = 2  # Frames per second
    capture_audio: bool = False

class UserMonitoringSettings(BaseModel):
    user_id: str
    screenshot_config: Optional[ScreenshotConfig] = None
    recording_config: Optional[ScreenRecordingConfig] = None

class OrganizationMonitoringSettings(BaseModel):
    organization_id: str
    default_screenshot_config: ScreenshotConfig
    default_recording_config: ScreenRecordingConfig
    allow_users_disable_screenshots: bool = False
    allow_users_delete_screenshots: bool = True
    screenshot_retention_days: int = 90
    recording_retention_days: int = 30

# ============================================
# ADMIN CONFIGURATION ENDPOINTS
# ============================================

@router.post("/config/organization")
async def set_organization_monitoring_config(
    config: OrganizationMonitoringSettings,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Set organization-wide monitoring configuration (Admin only)
    """
    # Check permissions
    if not has_permission(current_user, "monitoring.configure"):
        raise HTTPException(
            status_code=403,
            detail="Only admins can configure monitoring"
        )
    
    try:
        # Validate intervals
        _validate_screenshot_config(config.default_screenshot_config)
        _validate_recording_config(config.default_recording_config)
        
        # Check for conflicts
        _check_monitoring_conflicts(
            config.default_screenshot_config,
            config.default_recording_config
        )
        
        # Store configuration
        await db.table('monitoring_configs').upsert({
            "organization_id": current_user['organization_id'],
            "screenshot_config": config.default_screenshot_config.dict(),
            "recording_config": config.default_recording_config.dict(),
            "allow_users_disable_screenshots": config.allow_users_disable_screenshots,
            "allow_users_delete_screenshots": config.allow_users_delete_screenshots,
            "screenshot_retention_days": config.screenshot_retention_days,
            "recording_retention_days": config.recording_retention_days,
            "updated_at": datetime.utcnow().isoformat(),
            "updated_by_id": current_user['id']
        }).execute()
        
        return {
            "success": True,
            "message": "Organization monitoring configuration updated",
            "config": config.dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/config/user")
async def set_user_monitoring_config(
    config: UserMonitoringSettings,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Set user-specific monitoring configuration (Admin only)
    """
    if not has_permission(current_user, "monitoring.configure"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        # Validate configurations
        if config.screenshot_config:
            _validate_screenshot_config(config.screenshot_config)
        if config.recording_config:
            _validate_recording_config(config.recording_config)
        
        # Check conflicts
        if config.screenshot_config and config.recording_config:
            _check_monitoring_conflicts(
                config.screenshot_config,
                config.recording_config
            )
        
        # Store configuration
        await db.table('user_monitoring_configs').upsert({
            "user_id": config.user_id,
            "organization_id": current_user['organization_id'],
            "screenshot_config": config.screenshot_config.dict() if config.screenshot_config else None,
            "recording_config": config.recording_config.dict() if config.recording_config else None,
            "updated_at": datetime.utcnow().isoformat(),
            "updated_by_id": current_user['id']
        }).execute()
        
        return {
            "success": True,
            "message": "User monitoring configuration updated",
            "user_id": config.user_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config")
async def get_monitoring_config(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get effective monitoring configuration for current user
    """
    try:
        # Get organization default config
        org_config = await db.table('monitoring_configs').select('*')\
            .eq('organization_id', current_user['organization_id'])\
            .single().execute()
        
        # Get user-specific config
        user_config = await db.table('user_monitoring_configs').select('*')\
            .eq('user_id', current_user['id'])\
            .execute()
        
        # Merge configurations (user-specific overrides organization)
        if user_config.data:
            screenshot_config = user_config.data[0].get('screenshot_config') or \
                                org_config.data.get('screenshot_config')
            recording_config = user_config.data[0].get('recording_config') or \
                               org_config.data.get('recording_config')
        else:
            screenshot_config = org_config.data.get('screenshot_config')
            recording_config = org_config.data.get('recording_config')
        
        # Calculate next intervals
        next_screenshot_interval = _calculate_next_interval(screenshot_config)
        next_recording_interval = _calculate_next_interval(recording_config)
        
        return {
            "success": True,
            "screenshot_config": screenshot_config,
            "recording_config": recording_config,
            "next_screenshot_in_seconds": next_screenshot_interval,
            "next_recording_in_seconds": next_recording_interval,
            "permissions": {
                "can_disable_screenshots": org_config.data.get('allow_users_disable_screenshots', False),
                "can_delete_screenshots": org_config.data.get('allow_users_delete_screenshots', True)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/interval/next")
async def get_next_interval(
    monitoring_type: Literal["screenshot", "recording"],
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get next random interval for screenshot or recording
    Used by desktop app to schedule next capture
    """
    try:
        # Get user's config
        config_response = await get_monitoring_config(current_user, db)
        
        if monitoring_type == "screenshot":
            config = config_response['screenshot_config']
        else:
            config = config_response['recording_config']
        
        # Calculate next interval
        next_interval = _calculate_next_interval(config)
        
        # Log the scheduled interval
        await db.table('monitoring_schedule').insert({
            "id": str(uuid.uuid4()),
            "user_id": current_user['id'],
            "monitoring_type": monitoring_type,
            "interval_seconds": next_interval,
            "scheduled_at": datetime.utcnow().isoformat(),
            "status": "scheduled"
        }).execute()
        
        return {
            "success": True,
            "monitoring_type": monitoring_type,
            "next_interval_seconds": next_interval,
            "next_interval_minutes": round(next_interval / 60, 2),
            "scheduled_time": (datetime.utcnow().timestamp() + next_interval)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# INTERVAL PRESETS
# ============================================

@router.get("/presets")
async def get_interval_presets():
    """Get predefined interval presets"""
    return {
        "success": True,
        "screenshot_presets": {
            "very_frequent": {
                "name": "Very Frequent (1-3 min)",
                "interval_type": "random",
                "random_min_seconds": 60,
                "random_max_seconds": 180
            },
            "frequent": {
                "name": "Frequent (3-5 min)",
                "interval_type": "random",
                "random_min_seconds": 180,
                "random_max_seconds": 300
            },
            "normal": {
                "name": "Normal (5-10 min)",
                "interval_type": "random",
                "random_min_seconds": 300,
                "random_max_seconds": 600
            },
            "relaxed": {
                "name": "Relaxed (10-15 min)",
                "interval_type": "random",
                "random_min_seconds": 600,
                "random_max_seconds": 900
            },
            "fixed_5min": {
                "name": "Fixed 5 minutes",
                "interval_type": "fixed",
                "fixed_interval_seconds": 300
            },
            "fixed_10min": {
                "name": "Fixed 10 minutes",
                "interval_type": "fixed",
                "fixed_interval_seconds": 600
            }
        },
        "recording_presets": {
            "frequent": {
                "name": "Frequent (10-20 min)",
                "interval_type": "random",
                "random_min_seconds": 600,
                "random_max_seconds": 1200,
                "recording_duration_seconds": 300
            },
            "normal": {
                "name": "Normal (20-40 min)",
                "interval_type": "random",
                "random_min_seconds": 1200,
                "random_max_seconds": 2400,
                "recording_duration_seconds": 300
            },
            "relaxed": {
                "name": "Relaxed (40-60 min)",
                "interval_type": "random",
                "random_min_seconds": 2400,
                "random_max_seconds": 3600,
                "recording_duration_seconds": 600
            },
            "hourly": {
                "name": "Hourly",
                "interval_type": "fixed",
                "fixed_interval_seconds": 3600,
                "recording_duration_seconds": 300
            }
        }
    }

# ============================================
# MONITORING STATISTICS
# ============================================

@router.get("/stats")
async def get_monitoring_statistics(
    user_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get monitoring statistics (Admin can view all, users only own)"""
    try:
        # Permission check
        if user_id and user_id != current_user['id']:
            if not has_permission(current_user, "monitoring.view_all"):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
        else:
            user_id = current_user['id']
        
        # Get screenshot count
        screenshot_query = db.table('screenshots').select('*', count='exact')\
            .eq('user_id', user_id)
        
        if start_date:
            screenshot_query = screenshot_query.gte('captured_at', start_date.isoformat())
        if end_date:
            screenshot_query = screenshot_query.lte('captured_at', end_date.isoformat())
        
        screenshots = await screenshot_query.execute()
        
        # Get recording count
        recording_query = db.table('screen_recordings').select('*', count='exact')\
            .eq('user_id', user_id)
        
        if start_date:
            recording_query = recording_query.gte('started_at', start_date.isoformat())
        if end_date:
            recording_query = recording_query.lte('started_at', end_date.isoformat())
        
        recordings = await recording_query.execute()
        
        return {
            "success": True,
            "user_id": user_id,
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            },
            "statistics": {
                "total_screenshots": screenshots.count,
                "total_recordings": recordings.count,
                "screenshots_deleted_by_user": len([s for s in screenshots.data if s.get('is_deleted_by_user')]),
                "average_screenshot_size_kb": sum([s.get('file_size', 0) for s in screenshots.data]) / len(screenshots.data) / 1024 if screenshots.data else 0,
                "total_recording_duration_minutes": sum([r.get('duration_seconds', 0) for r in recordings.data]) / 60 if recordings.data else 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# HELPER FUNCTIONS
# ============================================

def _validate_screenshot_config(config: ScreenshotConfig):
    """Validate screenshot configuration"""
    if config.interval_type == "fixed":
        if not config.fixed_interval_seconds:
            raise ValueError("fixed_interval_seconds required for fixed interval type")
        if config.fixed_interval_seconds < 60 or config.fixed_interval_seconds > 900:
            raise ValueError("Fixed interval must be between 60 and 900 seconds (1-15 minutes)")
    
    elif config.interval_type == "random":
        if not config.random_min_seconds or not config.random_max_seconds:
            raise ValueError("random_min_seconds and random_max_seconds required for random interval type")
        if config.random_min_seconds < 60:
            raise ValueError("Minimum interval must be at least 60 seconds (1 minute)")
        if config.random_max_seconds > 900:
            raise ValueError("Maximum interval must not exceed 900 seconds (15 minutes)")
        if config.random_min_seconds >= config.random_max_seconds:
            raise ValueError("Minimum interval must be less than maximum interval")
    
    if config.quality < 1 or config.quality > 100:
        raise ValueError("Quality must be between 1 and 100")

def _validate_recording_config(config: ScreenRecordingConfig):
    """Validate screen recording configuration"""
    if config.interval_type == "fixed":
        if not config.fixed_interval_seconds:
            raise ValueError("fixed_interval_seconds required for fixed interval type")
        if config.fixed_interval_seconds < 60:
            raise ValueError("Fixed interval must be at least 60 seconds")
    
    elif config.interval_type == "random":
        if not config.random_min_seconds or not config.random_max_seconds:
            raise ValueError("random_min_seconds and random_max_seconds required for random interval type")
        if config.random_min_seconds < 60:
            raise ValueError("Minimum interval must be at least 60 seconds")
        if config.random_min_seconds >= config.random_max_seconds:
            raise ValueError("Minimum interval must be less than maximum interval")
    
    if config.recording_duration_seconds < 60:
        raise ValueError("Recording duration must be at least 60 seconds")
    if config.recording_duration_seconds > 1800:
        raise ValueError("Recording duration must not exceed 1800 seconds (30 minutes)")
    
    if config.fps < 1 or config.fps > 30:
        raise ValueError("FPS must be between 1 and 30")

def _check_monitoring_conflicts(screenshot_config: ScreenshotConfig, recording_config: ScreenRecordingConfig):
    """Check for conflicts between screenshot and recording configurations"""
    # Ensure they don't overlap too frequently
    # This is a basic check - could be more sophisticated
    
    screenshot_min_interval = screenshot_config.random_min_seconds if screenshot_config.interval_type == "random" else screenshot_config.fixed_interval_seconds
    recording_min_interval = recording_config.random_min_seconds if recording_config.interval_type == "random" else recording_config.fixed_interval_seconds
    
    # Ensure recording interval is at least 2x screenshot interval to avoid conflicts
    if recording_min_interval < screenshot_min_interval * 2:
        raise ValueError(
            "Recording interval should be at least 2x the screenshot interval to avoid system conflicts"
        )

def _calculate_next_interval(config: dict) -> int:
    """Calculate next interval in seconds based on configuration"""
    if config['interval_type'] == "fixed":
        return config['fixed_interval_seconds']
    else:
        # Random interval
        return random.randint(
            config['random_min_seconds'],
            config['random_max_seconds']
        )

def has_permission(user: dict, permission: str) -> bool:
    """Check if user has specific permission"""
    # Implementation from RBAC module
    pass

async def get_current_user():
    """Get current user"""
    pass

async def get_db():
    """Get database connection"""
    pass
