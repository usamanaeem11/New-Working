"""
Central Authentication Middleware
Enforces auth on ALL requests - no bypasses
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging
from app.auth.jwt_manager import verify_access_token
from app.logging.logging_config import log_audit_event

logger = logging.getLogger(__name__)

# Public endpoints that don't require auth
PUBLIC_ENDPOINTS = {
    '/api/auth/login',
    '/api/auth/register',
    '/api/auth/refresh',
    '/api/health',
    '/api/docs',
    '/api/openapi.json',
}

class AuthMiddleware(BaseHTTPMiddleware):
    """
    Central auth enforcement
    Every request goes through here - NO EXCEPTIONS
    """
    
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # Allow public endpoints
        if path in PUBLIC_ENDPOINTS or path.startswith('/api/docs'):
            return await call_next(request)
        
        # Extract token
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            logger.warning(f"Missing auth header: {path}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={'detail': 'Authentication required'}
            )
        
        token = auth_header.split(' ')[1]
        
        try:
            # Verify token
            payload = verify_access_token(token)
            
            # Attach user to request state
            request.state.user = payload
            request.state.user_id = payload['user_id']
            request.state.tenant_id = payload['tenant_id']
            
            # Log access
            log_audit_event(
                event_type='api_access',
                user_id=payload['user_id'],
                tenant_id=payload['tenant_id'],
                resource=path,
                action='access'
            )
            
            response = await call_next(request)
            return response
            
        except Exception as e:
            logger.error(f"Auth failed for {path}: {e}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={'detail': 'Invalid or expired token'}
            )
