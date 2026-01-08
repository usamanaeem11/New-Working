"""
Comprehensive Monitoring & Metrics
Prometheus-style metrics for observability
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest
from functools import wraps
import time
import logging

logger = logging.getLogger(__name__)

# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

# Auth metrics
auth_attempts_total = Counter(
    'auth_attempts_total',
    'Total authentication attempts',
    ['result']  # success, failure
)

# RBAC metrics
permission_checks_total = Counter(
    'permission_checks_total',
    'Total permission checks',
    ['result']  # allowed, denied
)

# AI metrics
ai_predictions_total = Counter(
    'ai_predictions_total',
    'Total AI predictions',
    ['model', 'status']  # allowed, blocked, modified
)

ai_prediction_duration = Histogram(
    'ai_prediction_duration_seconds',
    'AI prediction duration',
    ['model']
)

ai_confidence_score = Histogram(
    'ai_confidence_score',
    'AI prediction confidence scores',
    ['model']
)

# Database metrics
db_query_duration = Histogram(
    'db_query_duration_seconds',
    'Database query duration',
    ['operation']
)

db_connections_active = Gauge(
    'db_connections_active',
    'Active database connections'
)

# System metrics
active_users = Gauge(
    'active_users',
    'Currently active users'
)

clocked_in_employees = Gauge(
    'clocked_in_employees',
    'Currently clocked in employees'
)

def track_request_metrics(func):
    """Decorator to track request metrics"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            status = getattr(result, 'status_code', 200)
            http_requests_total.labels(
                method='',
                endpoint='',
                status=status
            ).inc()
            return result
        except Exception as e:
            http_requests_total.labels(
                method='',
                endpoint='',
                status=500
            ).inc()
            raise
        finally:
            duration = time.time() - start_time
            http_request_duration.labels(
                method='',
                endpoint=''
            ).observe(duration)
    
    return wrapper

def track_ai_prediction(model_name: str, confidence: float, status: str):
    """Track AI prediction metrics"""
    ai_predictions_total.labels(model=model_name, status=status).inc()
    ai_confidence_score.labels(model=model_name).observe(confidence)

def track_auth_attempt(success: bool):
    """Track authentication attempts"""
    result = 'success' if success else 'failure'
    auth_attempts_total.labels(result=result).inc()

def track_permission_check(allowed: bool):
    """Track permission checks"""
    result = 'allowed' if allowed else 'denied'
    permission_checks_total.labels(result=result).inc()

def get_metrics():
    """Get all metrics in Prometheus format"""
    return generate_latest()
