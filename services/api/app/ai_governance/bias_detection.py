"""
AI Bias Detection & Monitoring
Enterprise requirement: Detect and prevent biased AI decisions
"""
from typing import Dict, List, Any
from enum import Enum
import numpy as np

class ProtectedAttribute(Enum):
    GENDER = "gender"
    AGE = "age"
    RACE = "race"
    ETHNICITY = "ethnicity"
    RELIGION = "religion"
    DISABILITY = "disability"
    NATIONALITY = "nationality"

class BiasMetric(Enum):
    DEMOGRAPHIC_PARITY = "demographic_parity"
    EQUAL_OPPORTUNITY = "equal_opportunity"
    EQUALIZED_ODDS = "equalized_odds"
    DISPARATE_IMPACT = "disparate_impact"

class BiasDetector:
    """Detects bias in AI predictions"""
    
    # Thresholds for bias detection
    DISPARATE_IMPACT_THRESHOLD = 0.8  # 80% rule
    DEMOGRAPHIC_PARITY_THRESHOLD = 0.1  # 10% difference max
    
    def check_bias(self, predictions: List[Any], protected_attributes: Dict[str, List[Any]], 
                   actual_outcomes: List[Any] = None) -> Dict:
        """Check for bias in predictions"""
        
        bias_report = {
            'has_bias': False,
            'bias_detected_in': [],
            'metrics': {},
            'recommendations': []
        }
        
        for attr_name, attr_values in protected_attributes.items():
            # Check demographic parity
            parity_result = self._check_demographic_parity(predictions, attr_values)
            bias_report['metrics'][f'{attr_name}_demographic_parity'] = parity_result
            
            if parity_result['biased']:
                bias_report['has_bias'] = True
                bias_report['bias_detected_in'].append(attr_name)
            
            # Check disparate impact
            impact_result = self._check_disparate_impact(predictions, attr_values)
            bias_report['metrics'][f'{attr_name}_disparate_impact'] = impact_result
            
            if impact_result['biased']:
                bias_report['has_bias'] = True
                if attr_name not in bias_report['bias_detected_in']:
                    bias_report['bias_detected_in'].append(attr_name)
            
            # If actual outcomes provided, check equal opportunity
            if actual_outcomes:
                eq_opp_result = self._check_equal_opportunity(
                    predictions, attr_values, actual_outcomes
                )
                bias_report['metrics'][f'{attr_name}_equal_opportunity'] = eq_opp_result
                
                if eq_opp_result['biased']:
                    bias_report['has_bias'] = True
                    if attr_name not in bias_report['bias_detected_in']:
                        bias_report['bias_detected_in'].append(attr_name)
        
        # Generate recommendations
        if bias_report['has_bias']:
            bias_report['recommendations'] = self._generate_recommendations(
                bias_report['bias_detected_in']
            )
        
        return bias_report
    
    def _check_demographic_parity(self, predictions: List, attributes: List) -> Dict:
        """Check if positive outcome rate is similar across groups"""
        groups = {}
        
        # Group by attribute
        for pred, attr in zip(predictions, attributes):
            if attr not in groups:
                groups[attr] = []
            groups[attr].append(pred)
        
        # Calculate positive rate for each group
        positive_rates = {}
        for group, preds in groups.items():
            positive_count = sum(1 for p in preds if self._is_positive(p))
            positive_rates[group] = positive_count / len(preds) if preds else 0
        
        # Check if rates are similar
        if len(positive_rates) > 1:
            max_rate = max(positive_rates.values())
            min_rate = min(positive_rates.values())
            difference = max_rate - min_rate
            
            biased = difference > self.DEMOGRAPHIC_PARITY_THRESHOLD
            
            return {
                'biased': biased,
                'difference': difference,
                'rates_by_group': positive_rates,
                'threshold': self.DEMOGRAPHIC_PARITY_THRESHOLD
            }
        
        return {'biased': False, 'rates_by_group': positive_rates}
    
    def _check_disparate_impact(self, predictions: List, attributes: List) -> Dict:
        """Check 80% rule - ratio of selection rates"""
        groups = {}
        
        # Group by attribute
        for pred, attr in zip(predictions, attributes):
            if attr not in groups:
                groups[attr] = []
            groups[attr].append(pred)
        
        # Calculate selection rates
        selection_rates = {}
        for group, preds in groups.items():
            positive_count = sum(1 for p in preds if self._is_positive(p))
            selection_rates[group] = positive_count / len(preds) if preds else 0
        
        # Calculate disparate impact ratio
        if len(selection_rates) >= 2:
            max_rate = max(selection_rates.values())
            min_rate = min(selection_rates.values())
            
            if max_rate > 0:
                ratio = min_rate / max_rate
                biased = ratio < self.DISPARATE_IMPACT_THRESHOLD
                
                return {
                    'biased': biased,
                    'ratio': ratio,
                    'selection_rates': selection_rates,
                    'threshold': self.DISPARATE_IMPACT_THRESHOLD
                }
        
        return {'biased': False, 'selection_rates': selection_rates}
    
    def _check_equal_opportunity(self, predictions: List, attributes: List, 
                                 actual_outcomes: List) -> Dict:
        """Check if true positive rate is equal across groups"""
        groups = {}
        
        # Group by attribute
        for pred, attr, actual in zip(predictions, attributes, actual_outcomes):
            if attr not in groups:
                groups[attr] = {'tp': 0, 'fn': 0}
            
            if self._is_positive(actual):
                if self._is_positive(pred):
                    groups[attr]['tp'] += 1
                else:
                    groups[attr]['fn'] += 1
        
        # Calculate true positive rates
        tpr_by_group = {}
        for group, counts in groups.items():
            total_positives = counts['tp'] + counts['fn']
            tpr_by_group[group] = counts['tp'] / total_positives if total_positives > 0 else 0
        
        # Check if rates are similar
        if len(tpr_by_group) > 1:
            max_tpr = max(tpr_by_group.values())
            min_tpr = min(tpr_by_group.values())
            difference = max_tpr - min_tpr
            
            biased = difference > 0.1  # 10% threshold
            
            return {
                'biased': biased,
                'difference': difference,
                'tpr_by_group': tpr_by_group
            }
        
        return {'biased': False, 'tpr_by_group': tpr_by_group}
    
    def _is_positive(self, prediction: Any) -> bool:
        """Determine if prediction is positive outcome"""
        if isinstance(prediction, (bool, np.bool_)):
            return bool(prediction)
        elif isinstance(prediction, (int, float)):
            return prediction > 0.5
        elif isinstance(prediction, str):
            return prediction.lower() in ['true', 'yes', '1', 'positive', 'high']
        return False
    
    def _generate_recommendations(self, biased_attributes: List[str]) -> List[str]:
        """Generate recommendations for addressing bias"""
        recommendations = [
            "Review and rebalance training data across demographic groups",
            "Consider implementing fairness constraints in model training",
            "Perform regular bias audits on production predictions",
            "Document and monitor bias metrics as part of model governance"
        ]
        
        for attr in biased_attributes:
            recommendations.append(
                f"Specific attention needed for {attr} - consider separate model evaluation"
            )
        
        recommendations.append(
            "Implement human review for decisions affecting protected groups"
        )
        
        return recommendations

# Global bias detector
bias_detector = BiasDetector()
