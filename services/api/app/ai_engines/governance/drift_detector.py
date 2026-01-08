"""
AI Drift Detection
Monitors model performance and data distribution
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
import logging
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)

class DriftDetector:
    """
    Detects model drift and data distribution changes
    """
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.baseline_metrics = {}
        self.recent_predictions = []
        self.input_distributions = defaultdict(list)
        self.alert_threshold = 0.15  # 15% degradation triggers alert
        
    def record_prediction(
        self,
        input_features: Dict[str, Any],
        prediction: Any,
        actual: Any = None,
        confidence: float = None
    ):
        """
        Record a prediction for drift analysis
        
        Args:
            input_features: Input data used
            prediction: Model prediction
            actual: Actual value (if available)
            confidence: Prediction confidence
        """
        record = {
            'timestamp': datetime.utcnow(),
            'input': input_features,
            'prediction': prediction,
            'actual': actual,
            'confidence': confidence
        }
        
        self.recent_predictions.append(record)
        
        # Keep only last 1000 predictions
        if len(self.recent_predictions) > 1000:
            self.recent_predictions = self.recent_predictions[-1000:]
        
        # Track input distributions
        for key, value in input_features.items():
            if isinstance(value, (int, float)):
                self.input_distributions[key].append(value)
                
                # Keep only last 1000 values per feature
                if len(self.input_distributions[key]) > 1000:
                    self.input_distributions[key] = self.input_distributions[key][-1000:]
    
    def set_baseline(self, metrics: Dict[str, float]):
        """
        Set baseline performance metrics
        
        Args:
            metrics: Dict like {'accuracy': 0.85, 'precision': 0.82}
        """
        self.baseline_metrics = metrics.copy()
        logger.info(f"Baseline set for {self.model_name}: {metrics}")
    
    def check_performance_drift(self) -> Dict[str, Any]:
        """
        Check for performance degradation
        
        Returns:
            {
                'drift_detected': bool,
                'current_metrics': dict,
                'baseline_metrics': dict,
                'degradation': float
            }
        """
        if not self.baseline_metrics:
            return {'drift_detected': False, 'reason': 'No baseline set'}
        
        # Calculate current metrics from recent predictions
        predictions_with_actuals = [
            p for p in self.recent_predictions 
            if p.get('actual') is not None
        ]
        
        if len(predictions_with_actuals) < 10:
            return {'drift_detected': False, 'reason': 'Insufficient data'}
        
        # Calculate accuracy
        correct = sum(
            1 for p in predictions_with_actuals 
            if self._is_correct(p['prediction'], p['actual'])
        )
        current_accuracy = correct / len(predictions_with_actuals)
        
        current_metrics = {'accuracy': current_accuracy}
        
        # Check degradation
        baseline_accuracy = self.baseline_metrics.get('accuracy', 1.0)
        degradation = baseline_accuracy - current_accuracy
        
        drift_detected = degradation > self.alert_threshold
        
        if drift_detected:
            logger.warning(
                f"Performance drift detected for {self.model_name}: "
                f"Baseline: {baseline_accuracy:.3f}, "
                f"Current: {current_accuracy:.3f}, "
                f"Degradation: {degradation:.3f}"
            )
        
        return {
            'drift_detected': drift_detected,
            'current_metrics': current_metrics,
            'baseline_metrics': self.baseline_metrics,
            'degradation': degradation,
            'samples_evaluated': len(predictions_with_actuals)
        }
    
    def check_input_drift(self) -> Dict[str, Any]:
        """
        Check for input distribution changes
        
        Returns:
            {
                'drift_detected': bool,
                'drifted_features': List[str],
                'details': dict
            }
        """
        drifted_features = []
        details = {}
        
        for feature, values in self.input_distributions.items():
            if len(values) < 100:
                continue
            
            # Split into two halves
            mid = len(values) // 2
            old_values = values[:mid]
            new_values = values[mid:]
            
            # Calculate statistics
            old_mean = np.mean(old_values)
            new_mean = np.mean(new_values)
            old_std = np.std(old_values)
            
            # Check if mean shifted significantly
            if old_std > 0:
                z_score = abs(new_mean - old_mean) / old_std
                
                if z_score > 2.0:  # 2 standard deviations
                    drifted_features.append(feature)
                    details[feature] = {
                        'old_mean': float(old_mean),
                        'new_mean': float(new_mean),
                        'z_score': float(z_score)
                    }
        
        drift_detected = len(drifted_features) > 0
        
        if drift_detected:
            logger.warning(
                f"Input drift detected for {self.model_name}: "
                f"Features: {drifted_features}"
            )
        
        return {
            'drift_detected': drift_detected,
            'drifted_features': drifted_features,
            'details': details
        }
    
    def check_confidence_drift(self) -> Dict[str, Any]:
        """
        Check for confidence score changes
        
        Returns:
            {
                'drift_detected': bool,
                'avg_confidence': float,
                'confidence_trend': str
            }
        """
        predictions_with_confidence = [
            p for p in self.recent_predictions 
            if p.get('confidence') is not None
        ]
        
        if len(predictions_with_confidence) < 10:
            return {'drift_detected': False, 'reason': 'Insufficient data'}
        
        confidences = [p['confidence'] for p in predictions_with_confidence]
        avg_confidence = np.mean(confidences)
        
        # Check if confidence is declining
        if len(confidences) >= 50:
            recent = confidences[-25:]
            older = confidences[-50:-25]
            
            recent_avg = np.mean(recent)
            older_avg = np.mean(older)
            
            decline = older_avg - recent_avg
            
            if decline > 0.1:  # 10% decline
                return {
                    'drift_detected': True,
                    'avg_confidence': float(avg_confidence),
                    'confidence_trend': 'declining',
                    'decline_amount': float(decline)
                }
        
        return {
            'drift_detected': False,
            'avg_confidence': float(avg_confidence),
            'confidence_trend': 'stable'
        }
    
    def get_drift_report(self) -> Dict[str, Any]:
        """
        Get comprehensive drift report
        
        Returns:
            Complete drift analysis
        """
        return {
            'model_name': self.model_name,
            'timestamp': datetime.utcnow().isoformat(),
            'performance_drift': self.check_performance_drift(),
            'input_drift': self.check_input_drift(),
            'confidence_drift': self.check_confidence_drift(),
            'total_predictions': len(self.recent_predictions)
        }
    
    def _is_correct(self, prediction: Any, actual: Any, tolerance: float = 0.1) -> bool:
        """Check if prediction matches actual (with tolerance for regression)"""
        if isinstance(prediction, (int, float)) and isinstance(actual, (int, float)):
            # Regression - allow 10% error
            error = abs(prediction - actual) / max(abs(actual), 1)
            return error <= tolerance
        else:
            # Classification - exact match
            return prediction == actual

# Global drift detectors
drift_detectors = {}

def get_drift_detector(model_name: str) -> DriftDetector:
    """Get or create drift detector for model"""
    if model_name not in drift_detectors:
        drift_detectors[model_name] = DriftDetector(model_name)
    return drift_detectors[model_name]
