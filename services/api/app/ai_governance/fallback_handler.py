"""
AI Fallback Handler - What happens when AI fails
Enterprise-grade fallback mechanisms
"""
from typing import Optional, Dict, Any, Callable
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class FallbackStrategy(Enum):
    MANUAL_REVIEW = "manual_review"
    DEFAULT_VALUE = "default_value"
    RULE_BASED = "rule_based"
    CACHED_RESULT = "cached_result"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    USER_PROMPT = "user_prompt"

class FallbackHandler:
    """Handles AI failures with enterprise-grade fallback strategies"""
    
    def __init__(self):
        self.fallback_strategies: Dict[str, FallbackStrategy] = {}
        self.rule_based_fallbacks: Dict[str, Callable] = {}
        self.default_values: Dict[str, Any] = {}
        self.failure_counts: Dict[str, int] = {}
    
    def register_fallback(self, use_case: str, strategy: FallbackStrategy, 
                         fallback_value: Any = None, rule_function: Callable = None):
        """Register fallback strategy for a use case"""
        self.fallback_strategies[use_case] = strategy
        
        if strategy == FallbackStrategy.DEFAULT_VALUE and fallback_value is not None:
            self.default_values[use_case] = fallback_value
        
        if strategy == FallbackStrategy.RULE_BASED and rule_function is not None:
            self.rule_based_fallbacks[use_case] = rule_function
    
    def handle_failure(self, use_case: str, context: Dict, error: Exception) -> Dict:
        """Handle AI failure and return fallback result"""
        # Log the failure
        self._log_failure(use_case, error)
        
        # Increment failure count
        self.failure_counts[use_case] = self.failure_counts.get(use_case, 0) + 1
        
        # Get fallback strategy
        strategy = self.fallback_strategies.get(use_case, FallbackStrategy.MANUAL_REVIEW)
        
        # Execute fallback
        if strategy == FallbackStrategy.MANUAL_REVIEW:
            return self._manual_review_fallback(use_case, context)
        
        elif strategy == FallbackStrategy.DEFAULT_VALUE:
            return self._default_value_fallback(use_case)
        
        elif strategy == FallbackStrategy.RULE_BASED:
            return self._rule_based_fallback(use_case, context)
        
        elif strategy == FallbackStrategy.CACHED_RESULT:
            return self._cached_result_fallback(use_case, context)
        
        elif strategy == FallbackStrategy.GRACEFUL_DEGRADATION:
            return self._graceful_degradation(use_case, context)
        
        elif strategy == FallbackStrategy.USER_PROMPT:
            return self._user_prompt_fallback(use_case, context)
        
        else:
            return self._manual_review_fallback(use_case, context)
    
    def _manual_review_fallback(self, use_case: str, context: Dict) -> Dict:
        """Queue for manual review"""
        return {
            'status': 'pending_manual_review',
            'use_case': use_case,
            'requires_human': True,
            'context': context,
            'message': 'AI unavailable - queued for manual review'
        }
    
    def _default_value_fallback(self, use_case: str) -> Dict:
        """Return default value"""
        default = self.default_values.get(use_case, None)
        return {
            'status': 'fallback_applied',
            'value': default,
            'fallback_type': 'default_value',
            'message': 'Using default value due to AI failure'
        }
    
    def _rule_based_fallback(self, use_case: str, context: Dict) -> Dict:
        """Use rule-based logic"""
        rule_function = self.rule_based_fallbacks.get(use_case)
        if rule_function:
            try:
                result = rule_function(context)
                return {
                    'status': 'fallback_applied',
                    'value': result,
                    'fallback_type': 'rule_based',
                    'message': 'Using rule-based logic due to AI failure'
                }
            except Exception as e:
                logger.error(f"Rule-based fallback failed: {e}")
                return self._manual_review_fallback(use_case, context)
        
        return self._manual_review_fallback(use_case, context)
    
    def _cached_result_fallback(self, use_case: str, context: Dict) -> Dict:
        """Try to use cached result"""
        # Implementation would check cache
        return {
            'status': 'fallback_applied',
            'fallback_type': 'cached',
            'message': 'Using cached result due to AI failure'
        }
    
    def _graceful_degradation(self, use_case: str, context: Dict) -> Dict:
        """Degrade gracefully - provide limited functionality"""
        return {
            'status': 'degraded',
            'fallback_type': 'graceful_degradation',
            'message': 'Limited functionality available - AI temporarily unavailable'
        }
    
    def _user_prompt_fallback(self, use_case: str, context: Dict) -> Dict:
        """Prompt user for input"""
        return {
            'status': 'user_input_required',
            'fallback_type': 'user_prompt',
            'message': 'Please provide input - AI temporarily unavailable'
        }
    
    def _log_failure(self, use_case: str, error: Exception):
        """Log AI failure for monitoring"""
        from .ai_audit_logs import AIAuditLogger
        audit_logger = AIAuditLogger()
        audit_logger.log_event(
            event_type='ai_failure',
            use_case=use_case,
            details={'error': str(error), 'failure_count': self.failure_counts.get(use_case, 0)}
        )
        logger.error(f"AI failure in {use_case}: {error}")
    
    def get_failure_stats(self) -> Dict:
        """Get failure statistics"""
        return {
            'total_failures': sum(self.failure_counts.values()),
            'by_use_case': dict(self.failure_counts)
        }

# Global fallback handler
fallback_handler = FallbackHandler()

# Register default fallbacks for critical use cases
fallback_handler.register_fallback('employee_attrition', FallbackStrategy.MANUAL_REVIEW)
fallback_handler.register_fallback('performance_prediction', FallbackStrategy.MANUAL_REVIEW)
fallback_handler.register_fallback('hiring_recommendation', FallbackStrategy.MANUAL_REVIEW)
fallback_handler.register_fallback('time_fraud_detection', FallbackStrategy.RULE_BASED)
fallback_handler.register_fallback('payroll_anomaly', FallbackStrategy.MANUAL_REVIEW)
