# 🔐 RBAC PERMISSIONS UPDATE - New Features

## NEW ROLE: Client

**Authority Level:** 300 (between Employee: 400 and Guest: 200)

```python
# Add to backend/routes/rbac_complete.py

ROLES = {
    "super_admin": {"authority": 1000, "description": "Full system access"},
    "admin": {"authority": 900, "description": "Organization administrator"},
    "manager": {"authority": 700, "description": "Team manager"},
    "hr": {"authority": 600, "description": "HR manager"},
    "employee": {"authority": 400, "description": "Regular employee"},
    "client": {"authority": 300, "description": "External client"},  # NEW ROLE
    "guest": {"authority": 200, "description": "Guest access"}
}
```

## NEW PERMISSIONS

### Client Portal Permissions:
```python
"client_portal.view_dashboard": {
    "roles": ["client", "admin", "super_admin"],
    "description": "View client portal dashboard"
},
"client_portal.view_projects": {
    "roles": ["client", "manager", "admin", "super_admin"],
    "description": "View assigned projects"
},
"client_portal.approve_timesheets": {
    "roles": ["client", "manager", "admin"],
    "description": "Approve employee timesheets"
},
"client_portal.view_invoices": {
    "roles": ["client", "admin", "super_admin"],
    "description": "View invoices"
},
"client_portal.submit_feedback": {
    "roles": ["client"],
    "description": "Submit project feedback"
},
```

### Resource Planning Permissions:
```python
"resource.view_capacity": {
    "roles": ["manager", "admin", "super_admin"],
    "description": "View capacity heatmap"
},
"resource.manage_allocations": {
    "roles": ["manager", "admin", "super_admin"],
    "description": "Create/modify resource allocations"
},
"resource.view_skills": {
    "roles": ["employee", "manager", "hr", "admin", "super_admin"],
    "description": "View skill matrix"
},
"resource.manage_skills": {
    "roles": ["hr", "admin", "super_admin"],
    "description": "Add/remove skills"
},
```

### Workflow Permissions:
```python
"workflow.create": {
    "roles": ["admin", "super_admin"],
    "description": "Create workflow definitions"
},
"workflow.approve": {
    "roles": ["manager", "admin", "super_admin"],
    "description": "Approve workflow steps"
},
"workflow.view_pending": {
    "roles": ["employee", "manager", "admin", "super_admin"],
    "description": "View pending approvals"
},
"workflow.delegate": {
    "roles": ["manager", "admin"],
    "description": "Delegate approvals"
},
```

### Business Intelligence Permissions:
```python
"bi.view_kpis": {
    "roles": ["manager", "admin", "super_admin"],
    "description": "View KPI dashboard"
},
"bi.create_kpis": {
    "roles": ["admin", "super_admin"],
    "description": "Define new KPIs"
},
"bi.view_profitability": {
    "roles": ["manager", "admin", "super_admin"],
    "description": "View profitability analysis"
},
"bi.view_predictions": {
    "roles": ["manager", "admin", "super_admin"],
    "description": "View predictive analytics"
},
"bi.create_dashboard": {
    "roles": ["manager", "admin", "super_admin"],
    "description": "Create custom dashboards"
},
```

### Wellness Permissions:
```python
"wellness.submit_checkin": {
    "roles": ["employee", "manager", "admin", "super_admin"],
    "description": "Submit daily wellness check-in"
},
"wellness.view_own_data": {
    "roles": ["employee", "manager", "admin", "super_admin"],
    "description": "View own wellness data"
},
"wellness.view_team_data": {
    "roles": ["manager", "hr", "admin", "super_admin"],
    "description": "View team wellness trends"
},
"wellness.create_goals": {
    "roles": ["employee", "manager", "admin", "super_admin"],
    "description": "Create wellness goals"
},
"wellness.view_alerts": {
    "roles": ["manager", "hr", "admin", "super_admin"],
    "description": "View stress alerts"
},
```

### Performance Review Permissions:
```python
"performance.create_okr": {
    "roles": ["employee", "manager", "admin", "super_admin"],
    "description": "Create OKRs"
},
"performance.view_own_okrs": {
    "roles": ["employee", "manager", "admin", "super_admin"],
    "description": "View own OKRs"
},
"performance.view_team_okrs": {
    "roles": ["manager", "admin", "super_admin"],
    "description": "View team OKRs"
},
"performance.create_review": {
    "roles": ["manager", "hr", "admin", "super_admin"],
    "description": "Create performance reviews"
},
"performance.submit_feedback": {
    "roles": ["employee", "manager", "admin", "super_admin"],
    "description": "Submit 360 feedback"
},
"performance.view_reviews": {
    "roles": ["employee", "manager", "hr", "admin", "super_admin"],
    "description": "View performance reviews"
},
"performance.manage_cycles": {
    "roles": ["hr", "admin", "super_admin"],
    "description": "Manage review cycles"
},
```

## COMPLETE PERMISSIONS FILE UPDATE

### File: backend/routes/rbac_permissions.py

```python
# Complete permissions matrix for all 6 new features

PERMISSIONS = {
    # ... existing permissions ...
    
    # CLIENT PORTAL
    "client_portal.view_dashboard": ["client", "admin", "super_admin"],
    "client_portal.view_projects": ["client", "manager", "admin", "super_admin"],
    "client_portal.approve_timesheets": ["client", "manager", "admin"],
    "client_portal.view_invoices": ["client", "admin", "super_admin"],
    "client_portal.view_files": ["client", "manager", "admin", "super_admin"],
    "client_portal.upload_files": ["client", "manager", "admin", "super_admin"],
    "client_portal.submit_feedback": ["client"],
    
    # RESOURCE PLANNING
    "resource.view_capacity": ["manager", "admin", "super_admin"],
    "resource.manage_allocations": ["manager", "admin", "super_admin"],
    "resource.view_skills": ["employee", "manager", "hr", "admin", "super_admin"],
    "resource.manage_skills": ["hr", "admin", "super_admin"],
    "resource.add_employee_skill": ["hr", "admin", "super_admin"],
    "resource.view_workload": ["manager", "admin", "super_admin"],
    "resource.forecast_demand": ["manager", "admin", "super_admin"],
    
    # WORKFLOWS
    "workflow.create": ["admin", "super_admin"],
    "workflow.edit": ["admin", "super_admin"],
    "workflow.delete": ["super_admin"],
    "workflow.view": ["employee", "manager", "admin", "super_admin"],
    "workflow.approve": ["manager", "admin", "super_admin"],
    "workflow.reject": ["manager", "admin", "super_admin"],
    "workflow.delegate": ["manager", "admin"],
    "workflow.view_analytics": ["admin", "super_admin"],
    
    # BUSINESS INTELLIGENCE
    "bi.view_kpis": ["manager", "admin", "super_admin"],
    "bi.create_kpis": ["admin", "super_admin"],
    "bi.edit_kpis": ["admin", "super_admin"],
    "bi.delete_kpis": ["super_admin"],
    "bi.view_profitability": ["manager", "admin", "super_admin"],
    "bi.view_predictions": ["manager", "admin", "super_admin"],
    "bi.view_roi": ["manager", "admin", "super_admin"],
    "bi.create_dashboard": ["manager", "admin", "super_admin"],
    "bi.view_analytics": ["manager", "admin", "super_admin"],
    
    # WELLNESS
    "wellness.submit_checkin": ["employee", "manager", "admin", "super_admin"],
    "wellness.view_own_data": ["employee", "manager", "admin", "super_admin"],
    "wellness.view_team_data": ["manager", "hr", "admin", "super_admin"],
    "wellness.create_goals": ["employee", "manager", "admin", "super_admin"],
    "wellness.view_goals": ["employee", "manager", "hr", "admin", "super_admin"],
    "wellness.view_alerts": ["manager", "hr", "admin", "super_admin"],
    "wellness.create_challenges": ["hr", "admin", "super_admin"],
    "wellness.view_resources": ["employee", "manager", "admin", "super_admin"],
    
    # PERFORMANCE
    "performance.create_okr": ["employee", "manager", "admin", "super_admin"],
    "performance.edit_own_okr": ["employee", "manager", "admin", "super_admin"],
    "performance.view_own_okrs": ["employee", "manager", "admin", "super_admin"],
    "performance.view_team_okrs": ["manager", "admin", "super_admin"],
    "performance.create_review": ["manager", "hr", "admin", "super_admin"],
    "performance.submit_feedback": ["employee", "manager", "admin", "super_admin"],
    "performance.view_own_reviews": ["employee", "manager", "admin", "super_admin"],
    "performance.view_team_reviews": ["manager", "hr", "admin", "super_admin"],
    "performance.manage_cycles": ["hr", "admin", "super_admin"],
    "performance.view_analytics": ["hr", "admin", "super_admin"],
}

def check_permission(user_role, permission):
    """Check if user role has permission"""
    allowed_roles = PERMISSIONS.get(permission, [])
    return user_role in allowed_roles

def get_user_permissions(user_role):
    """Get all permissions for a user role"""
    return [perm for perm, roles in PERMISSIONS.items() if user_role in roles]
```

## PERMISSION DECORATOR

```python
# backend/utils/auth.py

from functools import wraps
from fastapi import HTTPException
from .rbac_permissions import check_permission

def require_permission(permission):
    """Decorator to check if user has required permission"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get user from request context
            user_role = kwargs.get('current_user', {}).get('role')
            
            if not check_permission(user_role, permission):
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission denied: {permission}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Usage in routes:
@router.get("/capacity/heatmap")
@require_permission("resource.view_capacity")
async def get_capacity_heatmap():
    # ... implementation
    pass
```

## FRONTEND PERMISSION CHECKING

```javascript
// frontend/src/utils/permissions.js

export const hasPermission = (userRole, permission) => {
  const permissions = {
    'client_portal.view_dashboard': ['client', 'admin', 'super_admin'],
    'resource.view_capacity': ['manager', 'admin', 'super_admin'],
    'workflow.approve': ['manager', 'admin', 'super_admin'],
    'bi.view_kpis': ['manager', 'admin', 'super_admin'],
    'wellness.view_team_data': ['manager', 'hr', 'admin', 'super_admin'],
    'performance.create_review': ['manager', 'hr', 'admin', 'super_admin'],
    // ... all permissions
  };
  
  const allowedRoles = permissions[permission] || [];
  return allowedRoles.includes(userRole);
};

// Usage in components:
import { hasPermission } from '../utils/permissions';

const MyComponent = () => {
  const userRole = localStorage.getItem('user_role');
  
  return (
    <div>
      {hasPermission(userRole, 'resource.view_capacity') && (
        <Button onClick={viewCapacity}>View Capacity</Button>
      )}
    </div>
  );
};
```

## SUMMARY

**Total New Permissions:** 45+

**New Role:** Client (authority: 300)

**Updated Roles:** All roles have new permissions for 6 features

**Permission Categories:**
- Client Portal: 7 permissions
- Resource Planning: 7 permissions
- Workflows: 8 permissions
- Business Intelligence: 9 permissions
- Wellness: 8 permissions
- Performance: 10 permissions

All permissions are role-based and granular for maximum security and flexibility!
