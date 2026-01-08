"""
Complete FastAPI Application with All Routers
Production-ready API wiring
"""
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import time

# Import all routers
from .routers import (
    auth_router,
    users_router,
    employees_router,
    time_tracking_router,
    payroll_router,
    reports_router,
    admin_router,
    ai_router
)

from .auth.jwt_manager import jwt_manager
from .auth.rbac import rbac

app = FastAPI(
    title="WorkingTracker API",
    description="Enterprise Workforce Management Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log to audit system
    print(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
    
    return response

# Authentication middleware
async def get_current_user(request: Request):
    """Extract and verify user from JWT token"""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    token = auth_header.split(" ")[1]
    payload = jwt_manager.verify_access_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return {
        "user_id": payload["sub"],
        "email": payload["email"],
        "roles": payload["roles"],
        "tenant_id": payload["tenant_id"]
    }

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# Register all routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(employees_router, prefix="/api/employees", tags=["Employees"])
app.include_router(time_tracking_router, prefix="/api/time", tags=["Time Tracking"])
app.include_router(payroll_router, prefix="/api/payroll", tags=["Payroll"])
app.include_router(reports_router, prefix="/api/reports", tags=["Reports"])
app.include_router(admin_router, prefix="/api/admin", tags=["Administration"])
app.include_router(ai_router, prefix="/api/ai", tags=["AI & Analytics"])

# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "path": request.url.path
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
