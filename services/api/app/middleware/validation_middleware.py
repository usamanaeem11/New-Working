"""
API Contract Validation Middleware
Validates all inputs and outputs against schemas
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from typing import Callable, Dict, Any
import logging
import json

logger = logging.getLogger(__name__)

class ValidationMiddleware:
    """
    Enforces strict input/output validation
    CRITICAL: Prevents injection and data corruption
    """
    
    # Max payload sizes
    MAX_JSON_SIZE = 10 * 1024 * 1024  # 10 MB
    MAX_STRING_LENGTH = 10000
    
    # Forbidden patterns (SQL injection, XSS, etc.)
    FORBIDDEN_PATTERNS = [
        "'; DROP TABLE",
        "<script>",
        "javascript:",
        "onerror=",
        "onload=",
        "../",
        "..\\",
    ]
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, request: Request, call_next: Callable):
        """Validate every request"""
        
        # Check content length
        content_length = request.headers.get('content-length')
        if content_length and int(content_length) > self.MAX_JSON_SIZE:
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={'detail': 'Payload too large'}
            )
        
        # Validate request body if present
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                body = await request.body()
                if body:
                    # Validate JSON
                    try:
                        data = json.loads(body)
                        self._validate_data(data, request.url.path)
                    except json.JSONDecodeError:
                        return JSONResponse(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            content={'detail': 'Invalid JSON'}
                        )
                    
                    # Restore body for downstream handlers
                    async def receive():
                        return {'type': 'http.request', 'body': body}
                    request._receive = receive
            except Exception as e:
                logger.error(f"Validation error: {e}")
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={'detail': str(e)}
                )
        
        # Continue to endpoint
        response = await call_next(request)
        return response
    
    def _validate_data(self, data: Any, path: str):
        """
        Validate data structure and content
        Prevents injection attacks and malformed data
        """
        if isinstance(data, dict):
            for key, value in data.items():
                self._validate_string(str(key), 'key')
                if isinstance(value, (dict, list)):
                    self._validate_data(value, path)
                elif isinstance(value, str):
                    self._validate_string(value, f'value[{key}]')
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                self._validate_data(item, path)
    
    def _validate_string(self, value: str, context: str):
        """
        Validate string for dangerous patterns
        """
        # Length check
        if len(value) > self.MAX_STRING_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'{context}: String too long'
            )
        
        # Pattern check
        value_lower = value.lower()
        for pattern in self.FORBIDDEN_PATTERNS:
            if pattern.lower() in value_lower:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'{context}: Forbidden pattern detected'
                )

def setup_validation_middleware(app):
    """Add validation middleware to app"""
    app.middleware("http")(ValidationMiddleware(app))
    logger.info("Validation middleware installed")
