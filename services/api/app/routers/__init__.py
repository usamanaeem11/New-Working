"""
API Router Exports
"""
from .auth import router as auth_router
from .users import router as users_router
from .employees import router as employees_router
from .time_tracking import router as time_tracking_router
from .payroll import router as payroll_router
from .reports import router as reports_router
from .admin import router as admin_router
from .ai import router as ai_router

__all__ = [
    "auth_router",
    "users_router",
    "employees_router",
    "time_tracking_router",
    "payroll_router",
    "reports_router",
    "admin_router",
    "ai_router"
]
