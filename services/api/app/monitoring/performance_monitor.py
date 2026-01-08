"""
Performance Monitoring
Tracks API performance and bottlenecks
"""

from fastapi import Request
import time
import logging
from typing import Dict
from collections import defaultdict

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """
    Monitors endpoint performance
    Tracks response times and identifies slow endpoints
    """
    
    def __init__(self):
        self.metrics: Dict[str, list] = defaultdict(list)
        self.max_samples = 1000  # Keep last 1000 samples per endpoint
    
    async def __call__(self, request: Request, call_next):
        """Monitor request performance"""
        
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Record metric
        endpoint = f"{request.method} {request.url.path}"
        self.record_metric(endpoint, duration)
        
        # Add performance header
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        
        # Log slow requests (> 1 second)
        if duration > 1.0:
            logger.warning(
                f"Slow request: {endpoint} took {duration:.3f}s"
            )
        
        return response
    
    def record_metric(self, endpoint: str, duration: float):
        """Record performance metric"""
        self.metrics[endpoint].append({
            'duration': duration,
            'timestamp': time.time()
        })
        
        # Keep only recent samples
        if len(self.metrics[endpoint]) > self.max_samples:
            self.metrics[endpoint] = self.metrics[endpoint][-self.max_samples:]
    
    def get_stats(self, endpoint: str = None) -> Dict:
        """Get performance statistics"""
        if endpoint:
            samples = self.metrics.get(endpoint, [])
            return self._calculate_stats(samples)
        else:
            # All endpoints
            stats = {}
            for ep, samples in self.metrics.items():
                stats[ep] = self._calculate_stats(samples)
            return stats
    
    def _calculate_stats(self, samples: list) -> Dict:
        """Calculate statistics from samples"""
        if not samples:
            return {}
        
        durations = [s['duration'] for s in samples]
        
        return {
            'count': len(durations),
            'avg': sum(durations) / len(durations),
            'min': min(durations),
            'max': max(durations),
            'p95': self._percentile(durations, 95),
            'p99': self._percentile(durations, 99)
        }
    
    def _percentile(self, values: list, percentile: int) -> float:
        """Calculate percentile"""
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values)-1)]

# Global instance
performance_monitor = PerformanceMonitor()

def setup_performance_monitoring(app):
    """Install performance monitoring"""
    app.middleware("http")(performance_monitor)
    logger.info("Performance monitoring installed")
