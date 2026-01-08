"""
Global Error Handler Middleware
Catches all errors and returns consistent responses
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import traceback

from app.logging.logging_config import log_audit_event

logger = logging.getLogger(__name__)

class ErrorHandlerMiddleware:
    """
    Global error handler
    Prevents unhandled exceptions from crashing the service
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, request: Request, call_next):
        """Handle all errors gracefully"""
        try:
            response = await call_next(request)
            return response
        
        except RequestValidationError as e:
            # Validation errors (422)
            log_audit_event(
                event_type='validation_error',
                resource=request.url.path,
                action=request.method,
                details={'errors': str(e)}
            )
            
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    'detail': 'Validation error',
                    'errors': e.errors()
                }
            )
        
        except PermissionError as e:
            # Permission denied (403)
            log_audit_event(
                event_type='permission_error',
                resource=request.url.path,
                action=request.method,
                details={'error': str(e)}
            )
            
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={'detail': 'Permission denied'}
            )
        
        except ValueError as e:
            # Bad request (400)
            logger.warning(f"ValueError: {e}")
            
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={'detail': str(e)}
            )
        
        except Exception as e:
            # Unexpected error (500)
            logger.error(f"Unhandled exception: {e}")
            logger.error(traceback.format_exc())
            
            log_audit_event(
                event_type='system_error',
                resource=request.url.path,
                action=request.method,
                details={
                    'error_type': type(e).__name__,
                    'error': str(e)
                }
            )
            
            # Don't leak internal errors to client
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    'detail': 'Internal server error',
                    'error_id': f"{int(time.time())}"  # For log correlation
                }
            )

def setup_error_handler(app):
    """Install error handler middleware"""
    app.middleware("http")(ErrorHandlerMiddleware(app))
    logger.info("Error handler middleware installed")

import time
