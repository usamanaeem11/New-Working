"""
Complete Role-Based Access Control (RBAC) System
Roles: CEO/Founder, Admin, Manager/HR, Employee, Freelancer
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/rbac", tags=["RBAC"])

# ============================================
# ROLE DEFINITIONS & PERMISSIONS
# ============================================

ROLE_HIERARCHY = {
    "ceo": 1000,      # Highest authority
    "founder": 1000,   # Same as CEO
    "admin": 900,      # Full system access
    "manager": 700,    # Team management
    "hr": 700,         # HR operations
    "employee": 500,   # Basic features
    "freelancer": 400  # Limited features
}

# Complete permission matrix
PERMISSIONS_MATRIX = {
    "ceo": {
        # System Administration
        "system.settings": True,
        "system.billing": True,
        "system.integrations": True,
        "system.white_label": True,
        "system.security": True,
        "system.audit_logs": True,
        
        # User Management
        "users.create": True,
        "users.read": True,
        "users.update": True,
        "users.delete": True,
        "users.assign_roles": True,
        "users.manage_permissions": True,
        
        # Organization
        "organization.settings": True,
        "organization.branding": True,
        "organization.departments": True,
        
        # Projects & Tasks
        "projects.create": True,
        "projects.read": True,
        "projects.update": True,
        "projects.delete": True,
        "projects.budgets": True,
        "tasks.create": True,
        "tasks.read": True,
        "tasks.update": True,
        "tasks.delete": True,
        "tasks.assign": True,
        
        # Time Tracking
        "time.track": True,
        "time.edit_own": True,
        "time.edit_others": True,
        "time.approve": True,
        "time.delete": True,
        
        # Screenshots & Monitoring
        "screenshots.view_own": True,
        "screenshots.view_team": True,
        "screenshots.view_all": True,
        "screenshots.delete_own": True,
        "screenshots.delete_others": True,
        "screenshots.configure": True,
        "monitoring.configure": True,
        "monitoring.view_all": True,
        
        # HRMS
        "hrms.leave.approve": True,
        "hrms.leave.manage": True,
        "hrms.expense.approve": True,
        "hrms.expense.manage": True,
        "hrms.payroll.view": True,
        "hrms.payroll.process": True,
        "hrms.attendance.view": True,
        "hrms.attendance.manage": True,
        "hrms.shifts.manage": True,
        "hrms.benefits.manage": True,
        
        # Reports & Analytics
        "reports.view_own": True,
        "reports.view_team": True,
        "reports.view_all": True,
        "reports.export": True,
        "reports.schedule": True,
        "analytics.view": True,
        
        # Invoicing & Billing
        "invoices.create": True,
        "invoices.view": True,
        "invoices.edit": True,
        "invoices.delete": True,
        "invoices.send": True,
        "billing.manage": True,
        
        # AI Features
        "ai.autopilot": True,
        "ai.coach": True,
        "ai.insights": True,
        "ai.assistant": True,
        
        # Integrations
        "integrations.manage": True,
        "integrations.configure": True,
    },
    
    "admin": {
        # Similar to CEO but without billing
        "system.settings": True,
        "system.integrations": True,
        "system.security": True,
        "system.audit_logs": True,
        "system.billing": False,  # Only CEO
        "system.white_label": False,  # Only CEO
        
        "users.create": True,
        "users.read": True,
        "users.update": True,
        "users.delete": True,
        "users.assign_roles": True,
        "users.manage_permissions": True,
        
        "organization.settings": True,
        "organization.branding": False,  # Only CEO
        "organization.departments": True,
        
        "projects.create": True,
        "projects.read": True,
        "projects.update": True,
        "projects.delete": True,
        "projects.budgets": True,
        
        "tasks.create": True,
        "tasks.read": True,
        "tasks.update": True,
        "tasks.delete": True,
        "tasks.assign": True,
        
        "time.track": True,
        "time.edit_own": True,
        "time.edit_others": True,
        "time.approve": True,
        "time.delete": True,
        
        "screenshots.view_own": True,
        "screenshots.view_team": True,
        "screenshots.view_all": True,
        "screenshots.delete_own": True,
        "screenshots.delete_others": True,
        "screenshots.configure": True,
        "monitoring.configure": True,
        "monitoring.view_all": True,
        
        "hrms.leave.approve": True,
        "hrms.leave.manage": True,
        "hrms.expense.approve": True,
        "hrms.expense.manage": True,
        "hrms.payroll.view": True,
        "hrms.payroll.process": True,
        "hrms.attendance.view": True,
        "hrms.attendance.manage": True,
        "hrms.shifts.manage": True,
        "hrms.benefits.manage": True,
        
        "reports.view_own": True,
        "reports.view_team": True,
        "reports.view_all": True,
        "reports.export": True,
        "reports.schedule": True,
        "analytics.view": True,
        
        "invoices.create": True,
        "invoices.view": True,
        "invoices.edit": True,
        "invoices.delete": True,
        "invoices.send": True,
        "billing.manage": False,  # Only CEO
        
        "ai.autopilot": True,
        "ai.coach": True,
        "ai.insights": True,
        "ai.assistant": True,
        
        "integrations.manage": True,
        "integrations.configure": True,
    },
    
    "manager": {
        # Team management focused
        "system.settings": False,
        "system.billing": False,
        "system.integrations": False,
        "system.security": False,
        "system.audit_logs": False,
        
        "users.create": False,
        "users.read": True,
        "users.update": False,
        "users.delete": False,
        "users.assign_roles": False,
        "users.manage_permissions": False,
        
        "organization.settings": False,
        "organization.branding": False,
        "organization.departments": False,
        
        "projects.create": True,
        "projects.read": True,
        "projects.update": True,
        "projects.delete": False,
        "projects.budgets": True,
        
        "tasks.create": True,
        "tasks.read": True,
        "tasks.update": True,
        "tasks.delete": True,
        "tasks.assign": True,
        
        "time.track": True,
        "time.edit_own": True,
        "time.edit_others": False,
        "time.approve": True,
        "time.delete": False,
        
        "screenshots.view_own": True,
        "screenshots.view_team": True,
        "screenshots.view_all": False,
        "screenshots.delete_own": True,
        "screenshots.delete_others": False,
        "screenshots.configure": False,
        "monitoring.configure": False,
        "monitoring.view_all": False,
        
        "hrms.leave.approve": True,
        "hrms.leave.manage": False,
        "hrms.expense.approve": True,
        "hrms.expense.manage": False,
        "hrms.payroll.view": False,
        "hrms.payroll.process": False,
        "hrms.attendance.view": True,
        "hrms.attendance.manage": False,
        "hrms.shifts.manage": False,
        "hrms.benefits.manage": False,
        
        "reports.view_own": True,
        "reports.view_team": True,
        "reports.view_all": False,
        "reports.export": True,
        "reports.schedule": False,
        "analytics.view": True,
        
        "invoices.create": False,
        "invoices.view": True,
        "invoices.edit": False,
        "invoices.delete": False,
        "invoices.send": False,
        "billing.manage": False,
        
        "ai.autopilot": True,
        "ai.coach": True,
        "ai.insights": True,
        "ai.assistant": True,
        
        "integrations.manage": False,
        "integrations.configure": False,
    },
    
    "hr": {
        # HR operations focused
        "system.settings": False,
        "system.billing": False,
        "system.integrations": False,
        "system.security": False,
        "system.audit_logs": False,
        
        "users.create": True,
        "users.read": True,
        "users.update": True,
        "users.delete": False,
        "users.assign_roles": False,
        "users.manage_permissions": False,
        
        "organization.settings": False,
        "organization.branding": False,
        "organization.departments": True,
        
        "projects.create": False,
        "projects.read": True,
        "projects.update": False,
        "projects.delete": False,
        "projects.budgets": False,
        
        "tasks.create": False,
        "tasks.read": True,
        "tasks.update": False,
        "tasks.delete": False,
        "tasks.assign": False,
        
        "time.track": True,
        "time.edit_own": True,
        "time.edit_others": False,
        "time.approve": False,
        "time.delete": False,
        
        "screenshots.view_own": True,
        "screenshots.view_team": False,
        "screenshots.view_all": False,
        "screenshots.delete_own": True,
        "screenshots.delete_others": False,
        "screenshots.configure": False,
        "monitoring.configure": False,
        "monitoring.view_all": False,
        
        "hrms.leave.approve": True,
        "hrms.leave.manage": True,
        "hrms.expense.approve": True,
        "hrms.expense.manage": True,
        "hrms.payroll.view": True,
        "hrms.payroll.process": True,
        "hrms.attendance.view": True,
        "hrms.attendance.manage": True,
        "hrms.shifts.manage": True,
        "hrms.benefits.manage": True,
        
        "reports.view_own": True,
        "reports.view_team": False,
        "reports.view_all": True,
        "reports.export": True,
        "reports.schedule": False,
        "analytics.view": True,
        
        "invoices.create": False,
        "invoices.view": False,
        "invoices.edit": False,
        "invoices.delete": False,
        "invoices.send": False,
        "billing.manage": False,
        
        "ai.autopilot": True,
        "ai.coach": True,
        "ai.insights": True,
        "ai.assistant": True,
        
        "integrations.manage": False,
        "integrations.configure": False,
    },
    
    "employee": {
        # Basic employee permissions
        "system.settings": False,
        "system.billing": False,
        "system.integrations": False,
        "system.security": False,
        "system.audit_logs": False,
        
        "users.create": False,
        "users.read": False,
        "users.update": False,
        "users.delete": False,
        "users.assign_roles": False,
        "users.manage_permissions": False,
        
        "organization.settings": False,
        "organization.branding": False,
        "organization.departments": False,
        
        "projects.create": False,
        "projects.read": True,
        "projects.update": False,
        "projects.delete": False,
        "projects.budgets": False,
        
        "tasks.create": False,
        "tasks.read": True,
        "tasks.update": True,
        "tasks.delete": False,
        "tasks.assign": False,
        
        "time.track": True,
        "time.edit_own": True,
        "time.edit_others": False,
        "time.approve": False,
        "time.delete": False,
        
        "screenshots.view_own": True,
        "screenshots.view_team": False,
        "screenshots.view_all": False,
        "screenshots.delete_own": True,
        "screenshots.delete_others": False,
        "screenshots.configure": False,
        "monitoring.configure": False,
        "monitoring.view_all": False,
        
        "hrms.leave.approve": False,
        "hrms.leave.manage": False,
        "hrms.expense.approve": False,
        "hrms.expense.manage": False,
        "hrms.payroll.view": False,
        "hrms.payroll.process": False,
        "hrms.attendance.view": True,
        "hrms.attendance.manage": False,
        "hrms.shifts.manage": False,
        "hrms.benefits.manage": False,
        
        "reports.view_own": True,
        "reports.view_team": False,
        "reports.view_all": False,
        "reports.export": True,
        "reports.schedule": False,
        "analytics.view": False,
        
        "invoices.create": False,
        "invoices.view": False,
        "invoices.edit": False,
        "invoices.delete": False,
        "invoices.send": False,
        "billing.manage": False,
        
        "ai.autopilot": True,
        "ai.coach": True,
        "ai.insights": True,
        "ai.assistant": True,
        
        "integrations.manage": False,
        "integrations.configure": False,
    },
    
    "freelancer": {
        # Freelancer specific permissions
        "system.settings": False,
        "system.billing": False,
        "system.integrations": False,
        "system.security": False,
        "system.audit_logs": False,
        
        "users.create": False,
        "users.read": False,
        "users.update": False,
        "users.delete": False,
        "users.assign_roles": False,
        "users.manage_permissions": False,
        
        "organization.settings": False,
        "organization.branding": False,
        "organization.departments": False,
        
        "projects.create": True,
        "projects.read": True,
        "projects.update": True,
        "projects.delete": True,
        "projects.budgets": True,
        
        "tasks.create": True,
        "tasks.read": True,
        "tasks.update": True,
        "tasks.delete": True,
        "tasks.assign": False,
        
        "time.track": True,
        "time.edit_own": True,
        "time.edit_others": False,
        "time.approve": False,
        "time.delete": False,
        
        "screenshots.view_own": True,
        "screenshots.view_team": False,
        "screenshots.view_all": False,
        "screenshots.delete_own": True,
        "screenshots.delete_others": False,
        "screenshots.configure": True,
        "monitoring.configure": True,
        "monitoring.view_all": False,
        
        "hrms.leave.approve": False,
        "hrms.leave.manage": False,
        "hrms.expense.approve": False,
        "hrms.expense.manage": False,
        "hrms.payroll.view": False,
        "hrms.payroll.process": False,
        "hrms.attendance.view": True,
        "hrms.attendance.manage": False,
        "hrms.shifts.manage": False,
        "hrms.benefits.manage": False,
        
        "reports.view_own": True,
        "reports.view_team": False,
        "reports.view_all": False,
        "reports.export": True,
        "reports.schedule": False,
        "analytics.view": True,
        
        "invoices.create": True,
        "invoices.view": True,
        "invoices.edit": True,
        "invoices.delete": True,
        "invoices.send": True,
        "billing.manage": False,
        
        "ai.autopilot": True,
        "ai.coach": True,
        "ai.insights": True,
        "ai.assistant": True,
        
        "integrations.manage": False,
        "integrations.configure": False,
    }
}

# ============================================
# PYDANTIC MODELS
# ============================================

class RoleUpdate(BaseModel):
    user_id: str
    new_role: str

class CustomPermissions(BaseModel):
    user_id: str
    permissions: Dict[str, bool]

class ManagerPermissions(BaseModel):
    manager_id: str
    allowed_features: List[str]

# ============================================
# RBAC ENDPOINTS
# ============================================

@router.get("/roles")
async def get_all_roles(
    current_user: dict = Depends(get_current_user)
):
    """Get all available roles"""
    return {
        "success": True,
        "roles": list(ROLE_HIERARCHY.keys()),
        "hierarchy": ROLE_HIERARCHY
    }

@router.get("/permissions/{role}")
async def get_role_permissions(
    role: str,
    current_user: dict = Depends(get_current_user)
):
    """Get permissions for a specific role"""
    if role not in PERMISSIONS_MATRIX:
        raise HTTPException(status_code=404, detail="Role not found")
    
    return {
        "success": True,
        "role": role,
        "permissions": PERMISSIONS_MATRIX[role]
    }

@router.post("/assign-role")
async def assign_role(
    role_update: RoleUpdate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Assign role to user (CEO/Admin only)"""
    # Check if current user has permission
    if not has_permission(current_user, "users.assign_roles"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Validate new role
    if role_update.new_role not in ROLE_HIERARCHY:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    # Check hierarchy (can't assign higher role than yours)
    if ROLE_HIERARCHY[role_update.new_role] >= ROLE_HIERARCHY[current_user['role']]:
        raise HTTPException(status_code=403, detail="Cannot assign role equal or higher than yours")
    
    # Update user role
    await db.table('users').update({
        "role": role_update.new_role,
        "updated_at": datetime.utcnow().isoformat()
    }).eq('id', role_update.user_id).execute()
    
    return {
        "success": True,
        "message": f"Role updated to {role_update.new_role}"
    }

@router.post("/custom-permissions")
async def set_custom_permissions(
    custom_perms: CustomPermissions,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Set custom permissions for a user (CEO/Admin only)"""
    if not has_permission(current_user, "users.manage_permissions"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Store custom permissions
    await db.table('user_permissions').upsert({
        "user_id": custom_perms.user_id,
        "custom_permissions": custom_perms.permissions,
        "updated_at": datetime.utcnow().isoformat()
    }).execute()
    
    return {
        "success": True,
        "message": "Custom permissions set"
    }

@router.post("/manager/set-permissions")
async def set_manager_permissions(
    manager_perms: ManagerPermissions,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Admin assigns specific features to managers"""
    if not has_permission(current_user, "users.manage_permissions"):
        raise HTTPException(status_code=403, detail="Only admin can set manager permissions")
    
    # Get manager
    manager = await db.table('users').select('*')\
        .eq('id', manager_perms.manager_id).single().execute()
    
    if not manager.data or manager.data['role'] != 'manager':
        raise HTTPException(status_code=400, detail="User is not a manager")
    
    # Set allowed features
    await db.table('user_permissions').upsert({
        "user_id": manager_perms.manager_id,
        "allowed_features": manager_perms.allowed_features,
        "updated_at": datetime.utcnow().isoformat()
    }).execute()
    
    return {
        "success": True,
        "message": "Manager permissions updated",
        "allowed_features": manager_perms.allowed_features
    }

@router.get("/user/{user_id}/permissions")
async def get_user_permissions(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get effective permissions for a user"""
    # Get user
    user = await db.table('users').select('*').eq('id', user_id).single().execute()
    if not user.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get base permissions from role
    base_permissions = PERMISSIONS_MATRIX.get(user.data['role'], {})
    
    # Get custom permissions
    custom = await db.table('user_permissions').select('*')\
        .eq('user_id', user_id).execute()
    
    if custom.data:
        # Merge custom permissions
        custom_perms = custom.data[0].get('custom_permissions', {})
        effective_permissions = {**base_permissions, **custom_perms}
    else:
        effective_permissions = base_permissions
    
    return {
        "success": True,
        "user_id": user_id,
        "role": user.data['role'],
        "permissions": effective_permissions
    }

# ============================================
# HELPER FUNCTIONS
# ============================================

def has_permission(user: dict, permission: str) -> bool:
    """Check if user has specific permission"""
    role = user.get('role', 'employee')
    base_permissions = PERMISSIONS_MATRIX.get(role, {})
    
    # Check custom permissions
    custom_perms = user.get('custom_permissions', {})
    
    # Custom permissions override base
    if permission in custom_perms:
        return custom_perms[permission]
    
    return base_permissions.get(permission, False)

def require_permission(permission: str):
    """Decorator to require specific permission"""
    def decorator(func):
        async def wrapper(*args, current_user: dict = None, **kwargs):
            if not has_permission(current_user, permission):
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission '{permission}' required"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

async def get_current_user():
    """Get current user"""
    pass

async def get_db():
    """Get database connection"""
    pass
