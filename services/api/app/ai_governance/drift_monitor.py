"""
AI Model Drift Monitor
Detects data drift and concept drift in production models
"""
from typing import Dict, List
import numpy as np
from scipy import stats
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DriftMonitor:
    """Monitor AI model drift and performance degradation"""
    
    # Thresholds for drift detection
    PSI_THRESHOLD = 0.2  # Population Stability Index
    KS_THRESHOLD = 0.1   # Kolmogorov-Smirnov statistic
    ACCURACY_DROP_ALERT = 0.05  # 5% accuracy drop
    ACCURACY_DROP_CRITICAL = 0.10  # 10% accuracy drop
    
    def __init__(self):
        self.baseline_distributions = {}
        self.performance_history = {}
        self.drift_alerts = []
    
    def set_baseline(self, model_name: str, feature_data: Dict[str, List]):
        """Set baseline distribution for drift detection"""
        self.baseline_distributions[model_name] = {
            feature_name: self._calculate_distribution(values)
            for feature_name, values in feature_data.items()
        }
        logger.info(f"Baseline set for model: {model_name}")
    
    def detect_data_drift(self, model_name: str, current_data: Dict[str, List]) -> Dict:
        """Detect statistical drift in input data"""
        if model_name not in self.baseline_distributions:
            return {'error': 'No baseline set for model'}
        
        baseline = self.baseline_distributions[model_name]
        drift_results = {
            'model': model_name,
            'timestamp': datetime.utcnow().isoformat(),
            'has_drift': False,
            'features_with_drift': [],
            'metrics': {}
        }
        
        for feature_name, current_values in current_data.items():
            if feature_name not in baseline:
                continue
            
            # Calculate PSI (Population Stability Index)
            psi = self._calculate_psi(
                baseline[feature_name],
                self._calculate_distribution(current_values)
            )
            
            # Calculate KS statistic
            ks_stat = self._calculate_ks_statistic(
                baseline[feature_name]['values'],
                current_values
            )
            
            drift_results['metrics'][feature_name] = {
                'psi': psi,
                'ks_statistic': ks_stat,
                'drift_detected': psi > self.PSI_THRESHOLD or ks_stat > self.KS_THRESHOLD
            }
            
            if psi > self.PSI_THRESHOLD or ks_stat > self.KS_THRESHOLD:
                drift_results['has_drift'] = True
                drift_results['features_with_drift'].append(feature_name)
        
        # Log drift detection
        if drift_results['has_drift']:
            self._log_drift_alert(model_name, drift_results)
        
        return drift_results
    
    def detect_concept_drift(self, model_name: str, predictions: List, 
                            actuals: List, window_size: int = 1000) -> Dict:
        """Detect if relationship between features and target changed"""
        if model_name not in self.performance_history:
            self.performance_history[model_name] = []
        
        # Calculate current accuracy
        current_accuracy = self._calculate_accuracy(predictions, actuals)
        
        # Store in history
        self.performance_history[model_name].append({
            'timestamp': datetime.utcnow(),
            'accuracy': current_accuracy,
            'sample_size': len(predictions)
        })
        
        # Check for concept drift
        if len(self.performance_history[model_name]) < 2:
            return {'insufficient_history': True}
        
        # Get baseline accuracy (first measurement or average of first N)
        baseline_accuracy = self._get_baseline_accuracy(model_name)
        
        # Calculate accuracy drop
        accuracy_drop = baseline_accuracy - current_accuracy
        
        drift_result = {
            'model': model_name,
            'timestamp': datetime.utcnow().isoformat(),
            'baseline_accuracy': baseline_accuracy,
            'current_accuracy': current_accuracy,
            'accuracy_drop': accuracy_drop,
            'concept_drift_detected': False,
            'severity': 'none'
        }
        
        if accuracy_drop >= self.ACCURACY_DROP_CRITICAL:
            drift_result['concept_drift_detected'] = True
            drift_result['severity'] = 'critical'
            self._trigger_retraining_alert(model_name, 'critical', drift_result)
        
        elif accuracy_drop >= self.ACCURACY_DROP_ALERT:
            drift_result['concept_drift_detected'] = True
            drift_result['severity'] = 'warning'
            self._trigger_retraining_alert(model_name, 'warning', drift_result)
        
        return drift_result
    
    def monitor_performance(self, model_name: str, period_days: int = 30) -> Dict:
        """Monitor model performance metrics over time"""
        if model_name not in self.performance_history:
            return {'error': 'No performance history'}
        
        cutoff_date = datetime.utcnow() - timedelta(days=period_days)
        recent_history = [
            h for h in self.performance_history[model_name]
            if h['timestamp'] > cutoff_date
        ]
        
        if not recent_history:
            return {'error': 'No recent history'}
        
        accuracies = [h['accuracy'] for h in recent_history]
        
        return {
            'model': model_name,
            'period_days': period_days,
            'data_points': len(recent_history),
            'current_accuracy': accuracies[-1] if accuracies else None,
            'average_accuracy': np.mean(accuracies) if accuracies else None,
            'min_accuracy': min(accuracies) if accuracies else None,
            'max_accuracy': max(accuracies) if accuracies else None,
            'std_dev': np.std(accuracies) if accuracies else None,
            'trend': self._calculate_trend(accuracies)
        }
    
    def _calculate_distribution(self, values: List) -> Dict:
        """Calculate distribution statistics"""
        values_array = np.array(values)
        
        # Create bins for PSI calculation
        bins = 10
        hist, bin_edges = np.histogram(values_array, bins=bins)
        
        return {
            'values': values,
            'mean': np.mean(values_array),
            'std': np.std(values_array),
            'histogram': hist.tolist(),
            'bin_edges': bin_edges.tolist()
        }
    
    def _calculate_psi(self, baseline_dist: Dict, current_dist: Dict) -> float:
        """Calculate Population Stability Index"""
        baseline_hist = np.array(baseline_dist['histogram']) + 1e-10  # Avoid div by zero
        current_hist = np.array(current_dist['histogram']) + 1e-10
        
        # Normalize
        baseline_prop = baseline_hist / baseline_hist.sum()
        current_prop = current_hist / current_hist.sum()
        
        # Calculate PSI
        psi = np.sum((current_prop - baseline_prop) * np.log(current_prop / baseline_prop))
        
        return float(psi)
    
    def _calculate_ks_statistic(self, baseline_values: List, current_values: List) -> float:
        """Calculate Kolmogorov-Smirnov statistic"""
        ks_stat, _ = stats.ks_2samp(baseline_values, current_values)
        return float(ks_stat)
    
    def _calculate_accuracy(self, predictions: List, actuals: List) -> float:
        """Calculate prediction accuracy"""
        if len(predictions) != len(actuals):
            return 0.0
        
        correct = sum(1 for p, a in zip(predictions, actuals) if p == a)
        return correct / len(predictions)
    
    def _get_baseline_accuracy(self, model_name: str) -> float:
        """Get baseline accuracy for comparison"""
        history = self.performance_history[model_name]
        
        # Use average of first 5 measurements as baseline
        baseline_measurements = history[:min(5, len(history))]
        baseline_accuracy = np.mean([h['accuracy'] for h in baseline_measurements])
        
        return baseline_accuracy
    
    def _calculate_trend(self, values: List) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return 'stable'
        
        # Simple linear regression to detect trend
        x = np.arange(len(values))
        slope, _ = np.polyfit(x, values, 1)
        
        if slope > 0.01:
            return 'improving'
        elif slope < -0.01:
            return 'degrading'
        else:
            return 'stable'
    
    def _log_drift_alert(self, model_name: str, drift_results: Dict):
        """Log drift detection alert"""
        from .ai_audit_logs import AIAuditLogger
        
        alert = {
            'type': 'data_drift',
            'model': model_name,
            'timestamp': datetime.utcnow(),
            'features_affected': drift_results['features_with_drift'],
            'severity': 'high'
        }
        
        self.drift_alerts.append(alert)
        
        logger.warning(f"Data drift detected in {model_name}: {drift_results['features_with_drift']}")
        
        # Log to audit trail
        audit_logger = AIAuditLogger()
        audit_logger.log_event(
            event_type='drift_detected',
            model_id=model_name,
            details=drift_results
        )
    
    def _trigger_retraining_alert(self, model_name: str, severity: str, details: Dict):
        """Trigger model retraining workflow"""
        alert = {
            'type': 'concept_drift',
            'model': model_name,
            'timestamp': datetime.utcnow(),
            'severity': severity,
            'details': details
        }
        
        self.drift_alerts.append(alert)
        
        logger.error(f"Concept drift detected in {model_name} - Severity: {severity}")
        
        # Log to audit trail
        from .ai_audit_logs import AIAuditLogger
        audit_logger = AIAuditLogger()
        audit_logger.log_event(
            event_type='retraining_required',
            model_id=model_name,
            details={'severity': severity, 'metrics': details}
        )
        
        # In production, this would trigger actual retraining workflow
        # e.g., create ticket, notify data science team, queue training job

# Global drift monitor instance
drift_monitor = DriftMonitor()
