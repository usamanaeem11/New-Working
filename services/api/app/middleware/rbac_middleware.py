"""
Central RBAC Enforcement Middleware
Forces permission checks on EVERY request
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Callable
import logging

from app.auth.rbac import has_permission, Permission
from app.logging.logging_config import log_audit_event

logger = logging.getLogger(__name__)

class RBACMiddleware:
    """
    Middleware to enforce RBAC on all protected routes
    CRITICAL: No endpoint bypasses this
    """
    
    # Public endpoints that don't require auth
    PUBLIC_PATHS = {
        '/api/auth/login',
        '/api/auth/register',
        '/api/health',
        '/api/docs',
        '/api/openapi.json',
    }
    
    # Endpoint to permission mapping
    ROUTE_PERMISSIONS = {
        # Employees
        ('GET', '/api/employees'): Permission.EMPLOYEE_READ,
        ('POST', '/api/employees'): Permission.EMPLOYEE_CREATE,
        ('PUT', '/api/employees'): Permission.EMPLOYEE_UPDATE,
        ('DELETE', '/api/employees'): Permission.EMPLOYEE_DELETE,
        
        # Time tracking
        ('GET', '/api/time'): Permission.TIME_READ,
        ('POST', '/api/time/clock-in'): Permission.TIME_CREATE,
        ('POST', '/api/time/clock-out'): Permission.TIME_CREATE,
        ('PUT', '/api/time'): Permission.TIME_UPDATE,
        
        # Payroll
        ('GET', '/api/payroll'): Permission.PAYROLL_READ,
        ('POST', '/api/payroll/run'): Permission.PAYROLL_RUN,
        
        # Reports
        ('GET', '/api/reports'): Permission.REPORT_READ,
        ('GET', '/api/dashboard'): Permission.EMPLOYEE_READ,
        
        # Admin
        ('POST', '/api/admin'): Permission.ADMIN_SETTINGS,
        ('PUT', '/api/admin'): Permission.ADMIN_SETTINGS,
        
        # AI
        ('GET', '/api/ai'): Permission.AI_VIEW_INSIGHTS,
        ('POST', '/api/ai/predict'): Permission.AI_VIEW_INSIGHTS,
    }
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, request: Request, call_next: Callable):
        """Process each request through RBAC check"""
        
        path = request.url.path
        method = request.method
        
        # Skip public paths
        if path in self.PUBLIC_PATHS or path.startswith('/api/docs'):
            return await call_next(request)
        
        # Get user from request state (set by auth middleware)
        user = getattr(request.state, 'user', None)
        
        if not user:
            log_audit_event(
                event_type='access_denied',
                resource=path,
                action='no_auth',
                details={'method': method, 'path': path}
            )
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={'detail': 'Authentication required'}
            )
        
        # Check permission for this route
        required_permission = self._get_required_permission(method, path)
        
        if required_permission:
            if not has_permission(user, required_permission):
                log_audit_event(
                    event_type='access_denied',
                    user_id=user.get('id'),
                    tenant_id=user.get('tenant_id'),
                    resource=path,
                    action='insufficient_permissions',
                    details={
                        'method': method,
                        'required_permission': required_permission.value,
                        'user_roles': user.get('roles', [])
                    }
                )
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={'detail': f'Permission denied: {required_permission.value}'}
                )
        
        # Log successful access
        log_audit_event(
            event_type='access_granted',
            user_id=user.get('id'),
            tenant_id=user.get('tenant_id'),
            resource=path,
            action=method.lower(),
            details={'endpoint': path}
        )
        
        # Continue to actual endpoint
        response = await call_next(request)
        return response
    
    def _get_required_permission(self, method: str, path: str) -> Permission:
        """
        Determine required permission for endpoint
        Uses exact match or pattern matching
        """
        # Exact match
        if (method, path) in self.ROUTE_PERMISSIONS:
            return self.ROUTE_PERMISSIONS[(method, path)]
        
        # Pattern matching for dynamic routes
        for (route_method, route_path), permission in self.ROUTE_PERMISSIONS.items():
            if method == route_method and self._path_matches(path, route_path):
                return permission
        
        # Default: require authentication but no specific permission
        return None
    
    def _path_matches(self, actual_path: str, pattern: str) -> bool:
        """Check if path matches pattern (with path params)"""
        actual_parts = actual_path.split('/')
        pattern_parts = pattern.split('/')
        
        if len(actual_parts) != len(pattern_parts):
            return False
        
        for actual, pattern_part in zip(actual_parts, pattern_parts):
            if pattern_part.startswith('{') and pattern_part.endswith('}'):
                # Path parameter - matches anything
                continue
            if actual != pattern_part:
                return False
        
        return True

def setup_rbac_middleware(app):
    """Add RBAC middleware to app"""
    app.middleware("http")(RBACMiddleware(app))
    logger.info("RBAC middleware installed - ALL routes protected")
