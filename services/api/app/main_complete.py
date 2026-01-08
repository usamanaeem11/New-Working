"""
Complete Main Application
All middleware properly wired, all routes registered
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

# Import all routers
from app.routers import (
    dashboard,
    auth,
    users,
    employees,
    time_tracking,
    payroll,
    reports,
    admin,
    ai,
    dashboard
)

# Import middleware
from app.middleware.rbac_middleware import setup_rbac_middleware
from app.middleware.validation_middleware import setup_validation_middleware
from app.middleware.rate_limit_middleware import setup_rate_limit_middleware
from app.middleware.error_handler import setup_error_handler
from app.monitoring.performance_monitor import setup_performance_monitoring

# Import health checks
from app.health.health_check import router as health_router

# Database
from app.database.session import engine, Base

# Logging
from app.logging.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Lifespan for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting WorkingTracker API...")
    
    # Startup: Create tables if needed
    # Base.metadata.create_all(bind=engine)
    
    # Load AI models
    try:
        from app.ai_engines.performance import performance_predictor
        from app.ai_engines.forecasting import turnover_predictor
        
        # Wrap with safety
        from app.ai_engines.governance.safe_ai_wrapper import wrap_model
        
        global safe_performance
        global safe_turnover
        
        safe_performance = wrap_model(performance_predictor, "performance_predictor")
        safe_turnover = wrap_model(turnover_predictor, "turnover_predictor")
        
        logger.info("AI models loaded and wrapped with safety layer")
    except Exception as e:
        logger.error(f"Failed to load AI models: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down WorkingTracker API...")

# Create FastAPI app
app = FastAPI(
    title="WorkingTracker API",
    description="Enterprise HR & Time Tracking System",
    version="1.0.0",
    lifespan=lifespan
)

# ============================================================
# MIDDLEWARE SETUP (ORDER MATTERS)
# ============================================================

# 1. CORS - Allow frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://app.workingtracker.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. GZip - Compress responses
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 3. Performance monitoring - Track all requests
setup_performance_monitoring(app)

# 4. Error handler - Catch all errors
setup_error_handler(app)

# 5. Validation - Validate all inputs
setup_validation_middleware(app)

# 6. Rate limiting - Prevent abuse
setup_rate_limit_middleware(app)

# 7. RBAC - Enforce permissions (MUST BE LAST)
setup_rbac_middleware(app)

logger.info("All middleware installed successfully")

# ============================================================
# ROUTER REGISTRATION
# ============================================================

# Health checks (public)
app.include_router(
    health_router,
    tags=["Health"]
)

# Authentication (public)
app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Authentication"]
)

# Dashboard (protected)
app.include_router(
    dashboard.router,
    prefix="/api/dashboard",
    tags=["Dashboard"]
)

# Users (protected)
app.include_router(
    users.router,
    prefix="/api/users",
    tags=["Users"]
)

# Employees (protected)
app.include_router(
    employees.router,
    prefix="/api/employees",
    tags=["Employees"]
)

# Time Tracking (protected)
app.include_router(
    time_tracking.router,
    prefix="/api/time",
    tags=["Time Tracking"]
)

# Payroll (protected)
app.include_router(
    payroll.router,
    prefix="/api/payroll",
    tags=["Payroll"]
)

# Reports (protected)
app.include_router(
    reports.router,
    prefix="/api/reports",
    tags=["Reports"]
)

# AI & Analytics (protected)
app.include_router(
    ai.router,
    prefix="/api/ai",
    tags=["AI & Analytics"]
)

# Admin (protected)
app.include_router(
    admin.router,
    prefix="/api/admin",
    tags=["Administration"]
)

logger.info("All routers registered successfully")

# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "service": "WorkingTracker API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }

# ============================================================
# GLOBAL EXCEPTION HANDLER
# ============================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch any unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "path": request.url.path
        }
    )

logger.info("WorkingTracker API initialized successfully")
