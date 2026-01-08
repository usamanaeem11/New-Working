"""
SLA Monitoring System
Track and enforce service level agreements
"""
from typing import Dict, List
from datetime import datetime, timedelta
from enum import Enum

class SLAMetric(Enum):
    UPTIME = "uptime"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"

class SLAMonitor:
    """
    Service Level Agreement Monitoring
    - Track SLA metrics
    - Alert on violations
    - Generate SLA reports
    - Calculate credits
    """
    
    def __init__(self):
        self.sla_targets = {}
        self.measurements = []
        self.violations = []
    
    def define_sla(self, service_tier: str, targets: Dict):
        """
        Define SLA targets for service tier
        
        Example:
        {
            'uptime_percentage': 99.9,
            'response_time_p95_ms': 500,
            'error_rate_max': 0.01,
            'throughput_min_rps': 100
        }
        """
        self.sla_targets[service_tier] = {
            'targets': targets,
            'defined_at': datetime.utcnow().isoformat()
        }
    
    def record_measurement(self, metric: SLAMetric, value: float,
                          service_tier: str):
        """Record SLA measurement"""
        measurement = {
            'timestamp': datetime.utcnow().isoformat(),
            'metric': metric.value,
            'value': value,
            'service_tier': service_tier
        }
        
        self.measurements.append(measurement)
        
        # Check for violation
        self._check_violation(metric, value, service_tier)
    
    def calculate_uptime(self, start_date: datetime, 
                        end_date: datetime) -> float:
        """
        Calculate uptime percentage for period
        
        Returns:
            Uptime percentage (0-100)
        """
        total_minutes = (end_date - start_date).total_seconds() / 60
        
        # Get downtime incidents in period
        downtime_minutes = self._get_downtime(start_date, end_date)
        
        uptime_minutes = total_minutes - downtime_minutes
        uptime_percentage = (uptime_minutes / total_minutes) * 100
        
        return round(uptime_percentage, 2)
    
    def generate_sla_report(self, service_tier: str,
                           period_start: datetime,
                           period_end: datetime) -> Dict:
        """Generate comprehensive SLA report"""
        
        targets = self.sla_targets.get(service_tier, {}).get('targets', {})
        
        # Calculate actual metrics
        uptime = self.calculate_uptime(period_start, period_end)
        avg_response_time = self._calculate_avg_response_time(
            period_start, period_end
        )
        error_rate = self._calculate_error_rate(period_start, period_end)
        
        # Determine compliance
        compliance = {
            'uptime': {
                'target': targets.get('uptime_percentage', 99.9),
                'actual': uptime,
                'met': uptime >= targets.get('uptime_percentage', 99.9)
            },
            'response_time': {
                'target': targets.get('response_time_p95_ms', 500),
                'actual': avg_response_time,
                'met': avg_response_time <= targets.get('response_time_p95_ms', 500)
            },
            'error_rate': {
                'target': targets.get('error_rate_max', 0.01),
                'actual': error_rate,
                'met': error_rate <= targets.get('error_rate_max', 0.01)
            }
        }
        
        # Calculate credits owed
        credits = self._calculate_credits(service_tier, compliance)
        
        return {
            'service_tier': service_tier,
            'period': {
                'start': period_start.isoformat(),
                'end': period_end.isoformat()
            },
            'compliance': compliance,
            'violations': self._get_violations_in_period(period_start, period_end),
            'credits_owed': credits,
            'sla_met': all(m['met'] for m in compliance.values())
        }
    
    def _check_violation(self, metric: SLAMetric, value: float,
                        service_tier: str):
        """Check if measurement violates SLA"""
        if service_tier not in self.sla_targets:
            return
        
        targets = self.sla_targets[service_tier]['targets']
        
        violated = False
        threshold = None
        
        if metric == SLAMetric.UPTIME:
            threshold = targets.get('uptime_percentage', 99.9)
            violated = value < threshold
        elif metric == SLAMetric.RESPONSE_TIME:
            threshold = targets.get('response_time_p95_ms', 500)
            violated = value > threshold
        elif metric == SLAMetric.ERROR_RATE:
            threshold = targets.get('error_rate_max', 0.01)
            violated = value > threshold
        
        if violated:
            violation = {
                'timestamp': datetime.utcnow().isoformat(),
                'metric': metric.value,
                'threshold': threshold,
                'actual_value': value,
                'service_tier': service_tier
            }
            self.violations.append(violation)
            self._alert_sla_violation(violation)
    
    def _alert_sla_violation(self, violation: Dict):
        """Alert about SLA violation"""
        # In production: send to PagerDuty, Slack, email
        print(f"🚨 SLA VIOLATION: {violation['metric']} - {violation['actual_value']}")
    
    def _get_downtime(self, start: datetime, end: datetime) -> float:
        """Get total downtime minutes in period"""
        # In production: query incident database
        return 5.0  # 5 minutes of downtime
    
    def _calculate_avg_response_time(self, start: datetime, 
                                     end: datetime) -> float:
        """Calculate average response time"""
        # In production: query metrics database
        return 245.0  # milliseconds
    
    def _calculate_error_rate(self, start: datetime, end: datetime) -> float:
        """Calculate error rate"""
        # In production: query error logs
        return 0.005  # 0.5% error rate
    
    def _get_violations_in_period(self, start: datetime, 
                                  end: datetime) -> List[Dict]:
        """Get violations in time period"""
        return [
            v for v in self.violations
            if start <= datetime.fromisoformat(v['timestamp']) <= end
        ]
    
    def _calculate_credits(self, service_tier: str, 
                          compliance: Dict) -> Dict:
        """Calculate service credits owed for SLA misses"""
        credits = {
            'percentage': 0,
            'reason': []
        }
        
        uptime = compliance['uptime']['actual']
        
        if uptime < 99.0:
            credits['percentage'] = 50
            credits['reason'].append('Uptime below 99%')
        elif uptime < 99.5:
            credits['percentage'] = 25
            credits['reason'].append('Uptime below 99.5%')
        elif uptime < 99.9:
            credits['percentage'] = 10
            credits['reason'].append('Uptime below 99.9%')
        
        return credits

sla_monitor = SLAMonitor()
