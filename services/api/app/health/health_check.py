"""
Health Check Endpoints
For load balancers and monitoring
"""

from fastapi import APIRouter, Response, status
from sqlalchemy import text
from typing import Dict, Any
import time
import psutil
import logging

from app.database.session import engine

router = APIRouter()
logger = logging.getLogger(__name__)

# Track startup time
startup_time = time.time()

@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Basic health check
    Returns 200 if service is up
    """
    return {
        "status": "healthy",
        "service": "workingtracker-api",
        "timestamp": time.time()
    }

@router.get("/health/ready")
async def readiness_check(response: Response) -> Dict[str, Any]:
    """
    Readiness check for load balancers
    Checks if service can accept traffic
    """
    checks = {
        "database": False,
        "ai_models": False,
        "dependencies": False
    }
    
    # Check database
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception as e:
        logger.error(f"Database check failed: {e}")
    
    # Check AI models loaded
    try:
        from app.ai_engines.performance import performance_predictor
        checks["ai_models"] = True
    except Exception as e:
        logger.error(f"AI models check failed: {e}")
    
    # Check dependencies
    checks["dependencies"] = True  # Add specific checks as needed
    
    all_healthy = all(checks.values())
    
    if not all_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    return {
        "status": "ready" if all_healthy else "not_ready",
        "checks": checks,
        "timestamp": time.time()
    }

@router.get("/health/live")
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness check
    Returns 200 if service should not be restarted
    """
    uptime = time.time() - startup_time
    
    # Check if service is responsive
    try:
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        
        # If resources are extremely high, might indicate deadlock
        if cpu_percent > 95 and memory_percent > 95:
            return {
                "status": "unhealthy",
                "reason": "resource_exhaustion",
                "uptime": uptime
            }
    except:
        pass
    
    return {
        "status": "alive",
        "uptime": uptime,
        "timestamp": time.time()
    }

@router.get("/health/detailed")
async def detailed_health() -> Dict[str, Any]:
    """
    Detailed health information
    For monitoring and debugging
    """
    health_info = {
        "status": "healthy",
        "uptime": time.time() - startup_time,
        "timestamp": time.time(),
        "system": {},
        "database": {},
        "ai": {}
    }
    
    # System info
    try:
        health_info["system"] = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
    except:
        pass
    
    # Database info
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            health_info["database"]["status"] = "connected"
            health_info["database"]["version"] = result.scalar()
    except Exception as e:
        health_info["database"]["status"] = "error"
        health_info["database"]["error"] = str(e)
    
    # AI models info
    try:
        from app.ai_engines.performance import performance_predictor
        health_info["ai"]["models_loaded"] = True
    except:
        health_info["ai"]["models_loaded"] = False
    
    return health_info
