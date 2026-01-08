"""
Confidence Threshold Management
Enterprise-grade confidence scoring and thresholds
"""
from typing import Dict, Optional
from enum import Enum

class ConfidenceLevel(Enum):
    VERY_LOW = 0.0
    LOW = 0.4
    MEDIUM = 0.6
    HIGH = 0.8
    VERY_HIGH = 0.95

class ActionRequirement(Enum):
    NO_ACTION = "no_action"  # Confidence too low, don't use
    HUMAN_REVIEW = "human_review"  # Requires human verification
    AUTO_WITH_NOTIFICATION = "auto_with_notification"  # Auto-apply but notify
    FULLY_AUTOMATED = "fully_automated"  # Confidence high enough for full automation

class ConfidenceManager:
    """Manages confidence thresholds for AI predictions"""
    
    # Enterprise confidence thresholds by use case
    THRESHOLDS = {
        'employee_attrition': {
            'no_action': 0.0,
            'human_review': 0.6,
            'auto_with_notification': 0.85,
            'fully_automated': 0.95
        },
        'performance_prediction': {
            'no_action': 0.0,
            'human_review': 0.7,
            'auto_with_notification': 0.9,
            'fully_automated': 0.95
        },
        'hiring_recommendation': {
            'no_action': 0.0,
            'human_review': 0.75,  # Higher threshold for hiring
            'auto_with_notification': 0.9,
            'fully_automated': 0.97  # Nearly perfect confidence required
        },
        'time_fraud_detection': {
            'no_action': 0.0,
            'human_review': 0.65,
            'auto_with_notification': 0.85,
            'fully_automated': 0.95
        },
        'payroll_anomaly': {
            'no_action': 0.0,
            'human_review': 0.7,
            'auto_with_notification': 0.9,
            'fully_automated': 0.98  # Very high threshold for payroll
        }
    }
    
    def get_action_requirement(self, use_case: str, confidence: float) -> ActionRequirement:
        """Determine required action based on confidence"""
        thresholds = self.THRESHOLDS.get(use_case, self.THRESHOLDS['employee_attrition'])
        
        if confidence < thresholds['human_review']:
            return ActionRequirement.NO_ACTION
        elif confidence < thresholds['auto_with_notification']:
            return ActionRequirement.HUMAN_REVIEW
        elif confidence < thresholds['fully_automated']:
            return ActionRequirement.AUTO_WITH_NOTIFICATION
        else:
            return ActionRequirement.FULLY_AUTOMATED
    
    def validate_confidence(self, use_case: str, confidence: float, action: str) -> bool:
        """Validate if action is appropriate for confidence level"""
        required_action = self.get_action_requirement(use_case, confidence)
        
        # Map action strings to enum
        action_map = {
            'no_action': ActionRequirement.NO_ACTION,
            'human_review': ActionRequirement.HUMAN_REVIEW,
            'auto_with_notification': ActionRequirement.AUTO_WITH_NOTIFICATION,
            'fully_automated': ActionRequirement.FULLY_AUTOMATED
        }
        
        requested_action = action_map.get(action)
        
        # Check if requested action is within allowed level
        action_hierarchy = [
            ActionRequirement.NO_ACTION,
            ActionRequirement.HUMAN_REVIEW,
            ActionRequirement.AUTO_WITH_NOTIFICATION,
            ActionRequirement.FULLY_AUTOMATED
        ]
        
        return action_hierarchy.index(requested_action) <= action_hierarchy.index(required_action)
    
    def get_confidence_explanation(self, use_case: str, confidence: float) -> Dict:
        """Get human-readable explanation of confidence level"""
        action = self.get_action_requirement(use_case, confidence)
        
        explanations = {
            ActionRequirement.NO_ACTION: "Confidence too low for any automated action",
            ActionRequirement.HUMAN_REVIEW: "Requires human review before action",
            ActionRequirement.AUTO_WITH_NOTIFICATION: "Can be applied automatically with notification",
            ActionRequirement.FULLY_AUTOMATED: "High confidence - fully automated"
        }
        
        return {
            'confidence': confidence,
            'confidence_level': self._get_confidence_level(confidence).name,
            'action_requirement': action.value,
            'explanation': explanations[action],
            'thresholds': self.THRESHOLDS.get(use_case)
        }
    
    def _get_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Get confidence level enum from score"""
        if confidence >= 0.95:
            return ConfidenceLevel.VERY_HIGH
        elif confidence >= 0.8:
            return ConfidenceLevel.HIGH
        elif confidence >= 0.6:
            return ConfidenceLevel.MEDIUM
        elif confidence >= 0.4:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW

# Global confidence manager
confidence_manager = ConfidenceManager()
