"""
AI Explainability Engine
Enterprise requirement: All AI decisions must be explainable
"""
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import json

class Explanation(BaseModel):
    prediction: Any
    confidence: float
    reasoning: List[str]
    key_factors: Dict[str, float]
    limitations: List[str]
    alternative_outcomes: List[Dict]
    data_used: Dict[str, Any]
    model_info: Dict[str, str]

class ExplainabilityEngine:
    """Provides human-readable explanations for AI predictions"""
    
    def explain_prediction(self, model_name: str, prediction: Any, 
                          input_data: Dict, confidence: float, 
                          feature_importance: Dict = None) -> Explanation:
        """Generate explanation for a prediction"""
        
        # Extract key factors
        key_factors = self._extract_key_factors(feature_importance or {})
        
        # Generate reasoning
        reasoning = self._generate_reasoning(model_name, prediction, key_factors, input_data)
        
        # Get limitations
        limitations = self._get_model_limitations(model_name)
        
        # Generate alternatives
        alternatives = self._generate_alternatives(prediction, confidence)
        
        # Get model info
        model_info = self._get_model_info(model_name)
        
        return Explanation(
            prediction=prediction,
            confidence=confidence,
            reasoning=reasoning,
            key_factors=key_factors,
            limitations=limitations,
            alternative_outcomes=alternatives,
            data_used=self._sanitize_data(input_data),
            model_info=model_info
        )
    
    def _extract_key_factors(self, feature_importance: Dict) -> Dict[str, float]:
        """Extract and sort key factors"""
        # Sort by importance
        sorted_factors = sorted(feature_importance.items(), 
                               key=lambda x: abs(x[1]), 
                               reverse=True)
        
        # Take top 5 most important
        return dict(sorted_factors[:5])
    
    def _generate_reasoning(self, model_name: str, prediction: Any, 
                           key_factors: Dict, input_data: Dict) -> List[str]:
        """Generate human-readable reasoning"""
        reasoning = []
        
        # Model-specific reasoning
        if 'attrition' in model_name.lower():
            if prediction == 'high_risk':
                reasoning.append("Employee shows elevated attrition risk based on multiple factors")
                if 'tenure' in key_factors:
                    reasoning.append(f"Tenure is a significant factor (importance: {key_factors['tenure']:.2f})")
                if 'satisfaction' in key_factors:
                    reasoning.append(f"Satisfaction score is influencing prediction (importance: {key_factors['satisfaction']:.2f})")
        
        elif 'performance' in model_name.lower():
            reasoning.append(f"Performance prediction based on historical patterns and current metrics")
            for factor, importance in key_factors.items():
                reasoning.append(f"{factor} contributes {importance:.1%} to this prediction")
        
        elif 'fraud' in model_name.lower():
            if prediction == 'anomaly':
                reasoning.append("Unusual pattern detected in time tracking data")
                for factor in key_factors:
                    reasoning.append(f"Anomaly in {factor}")
        
        # Generic reasoning if no specific template
        if not reasoning:
            reasoning.append(f"Prediction made using {model_name} model")
            reasoning.append(f"Based on {len(input_data)} input features")
            reasoning.append(f"Top influencing factors: {', '.join(list(key_factors.keys())[:3])}")
        
        return reasoning
    
    def _get_model_limitations(self, model_name: str) -> List[str]:
        """Get known limitations of the model"""
        # Model-specific limitations
        limitations_map = {
            'attrition': [
                "Based on historical data - may not account for recent organizational changes",
                "Individual circumstances may override statistical patterns",
                "Prediction is probabilistic, not deterministic"
            ],
            'performance': [
                "Past performance is not always indicative of future results",
                "External factors not captured in model may influence outcomes",
                "Should be used as guidance, not sole decision factor"
            ],
            'fraud': [
                "May generate false positives",
                "Legitimate unusual patterns may be flagged",
                "Requires human verification before action"
            ]
        }
        
        # Find matching limitations
        for key, limits in limitations_map.items():
            if key in model_name.lower():
                return limits
        
        # Default limitations
        return [
            "AI predictions should supplement, not replace, human judgment",
            "Model trained on historical data - may not reflect current conditions",
            "Always verify predictions with additional context"
        ]
    
    def _generate_alternatives(self, prediction: Any, confidence: float) -> List[Dict]:
        """Generate alternative outcomes with probabilities"""
        # If confidence is low, show alternatives
        if confidence < 0.8:
            return [
                {
                    'outcome': 'alternative_1',
                    'probability': 1.0 - confidence,
                    'description': 'Alternative outcome with lower confidence'
                }
            ]
        return []
    
    def _get_model_info(self, model_name: str) -> Dict[str, str]:
        """Get model metadata"""
        from .model_registry import registry
        
        model = registry.get_model(model_name)
        if model:
            return {
                'name': model.name,
                'version': model.version,
                'type': model.type,
                'trained_date': model.trained_date.isoformat(),
                'status': model.status
            }
        
        return {'name': model_name, 'version': 'unknown'}
    
    def _sanitize_data(self, data: Dict) -> Dict:
        """Remove sensitive data from explanation"""
        sanitized = {}
        
        # List of sensitive fields to exclude
        sensitive_fields = ['password', 'ssn', 'tax_id', 'bank_account', 'salary']
        
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_fields):
                sanitized[key] = '[REDACTED]'
            else:
                sanitized[key] = value
        
        return sanitized

# Global explainability engine
explainability = ExplainabilityEngine()
