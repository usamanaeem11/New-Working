"""
Global Rate Limiting Middleware
Prevents abuse and DDoS
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from typing import Dict
import time
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware:
    """
    Global rate limiting
    Different limits for different endpoint types
    """
    
    def __init__(self, app):
        self.app = app
        # IP -> endpoint -> [timestamps]
        self.request_history: Dict[str, Dict[str, list]] = {}
        
        # Rate limits (requests per minute)
        self.limits = {
            'default': 60,      # 60 per minute
            'auth': 10,         # 10 login attempts per minute
            'ai': 20,           # 20 AI requests per minute
            'heavy': 10,        # 10 heavy operations per minute
        }
    
    async def __call__(self, request: Request, call_next):
        """Check rate limit before processing request"""
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        path = request.url.path
        
        # Determine rate limit category
        limit_category = self._get_limit_category(path)
        max_requests = self.limits[limit_category]
        
        # Check rate limit
        if not self._check_rate_limit(client_ip, path, max_requests):
            logger.warning(f"Rate limit exceeded: {client_ip} -> {path}")
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    'detail': 'Rate limit exceeded. Please try again later.',
                    'retry_after': 60
                },
                headers={'Retry-After': '60'}
            )
        
        # Continue to endpoint
        response = await call_next(request)
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        # Check X-Forwarded-For header (from load balancer)
        forwarded = request.headers.get('X-Forwarded-For')
        if forwarded:
            return forwarded.split(',')[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        # Fallback to direct client
        return request.client.host if request.client else 'unknown'
    
    def _get_limit_category(self, path: str) -> str:
        """Determine rate limit category for path"""
        if '/auth/' in path:
            return 'auth'
        elif '/ai/' in path:
            return 'ai'
        elif '/payroll/run' in path or '/reports/generate' in path:
            return 'heavy'
        else:
            return 'default'
    
    def _check_rate_limit(self, ip: str, path: str, max_requests: int) -> bool:
        """
        Check if request is within rate limit
        Uses sliding window algorithm
        """
        now = time.time()
        window = 60  # 1 minute window
        
        # Initialize tracking
        if ip not in self.request_history:
            self.request_history[ip] = {}
        
        if path not in self.request_history[ip]:
            self.request_history[ip][path] = []
        
        # Clean old requests (outside window)
        self.request_history[ip][path] = [
            ts for ts in self.request_history[ip][path]
            if now - ts < window
        ]
        
        # Check limit
        if len(self.request_history[ip][path]) >= max_requests:
            return False
        
        # Record this request
        self.request_history[ip][path].append(now)
        
        # Cleanup old IPs (memory management)
        self._cleanup_old_ips(now)
        
        return True
    
    def _cleanup_old_ips(self, now: float):
        """Remove IP tracking data older than 5 minutes"""
        if len(self.request_history) > 10000:  # Only cleanup if large
            for ip in list(self.request_history.keys()):
                # Check if all paths for this IP are old
                all_old = all(
                    all(now - ts > 300 for ts in timestamps)
                    for timestamps in self.request_history[ip].values()
                )
                
                if all_old:
                    del self.request_history[ip]

def setup_rate_limit_middleware(app):
    """Install rate limiting middleware"""
    app.middleware("http")(RateLimitMiddleware(app))
    logger.info("Rate limiting middleware installed")
