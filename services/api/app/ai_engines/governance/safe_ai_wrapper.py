"""
Safe AI Wrapper
Wraps all AI operations with safety checks
"""

from typing import Dict, Any, Optional
from app.ai_engines.governance.policy_engine import policy_engine, PolicyDecision
from app.logging.logging_config import log_audit_event
import logging
import time

logger = logging.getLogger(__name__)

class SafeAIWrapper:
    """
    Wraps AI models with safety, governance, and monitoring
    ALL AI calls must go through this
    """
    
    def __init__(self, model, model_name: str):
        self.model = model
        self.model_name = model_name
        self.is_enabled = True
    
    def predict(
        self,
        input_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Safe prediction with full governance
        
        Returns:
            {
                'success': bool,
                'result': Any,
                'confidence': float,
                'policy_decision': str,
                'warnings': List[str]
            }
        """
        start_time = time.time()
        warnings = []
        
        # Check if AI is globally enabled
        if not self.is_enabled:
            return {
                'success': False,
                'error': 'AI system disabled',
                'policy_decision': PolicyDecision.BLOCK.value
            }
        
        # Check user-level AI permissions
        if user_context.get('ai_disabled', False):
            log_audit_event(
                event_type='ai_access_denied',
                user_id=user_context.get('user_id'),
                resource=self.model_name,
                action='predict',
                details={'reason': 'AI disabled for user'}
            )
            return {
                'success': False,
                'error': 'AI access disabled for this user',
                'policy_decision': PolicyDecision.BLOCK.value
            }
        
        # Policy check - input
        input_decision, input_reason = policy_engine.evaluate_input(
            input_data, user_context
        )
        
        if input_decision == PolicyDecision.BLOCK:
            log_audit_event(
                event_type='ai_input_blocked',
                user_id=user_context.get('user_id'),
                resource=self.model_name,
                action='predict',
                details={'reason': input_reason}
            )
            return {
                'success': False,
                'error': f'Input blocked by policy: {input_reason}',
                'policy_decision': input_decision.value
            }
        
        if input_decision == PolicyDecision.REVIEW:
            warnings.append(input_reason)
        
        # Run model prediction
        try:
            raw_result = self.model.predict(input_data)
            confidence = self._extract_confidence(raw_result)
        except Exception as e:
            logger.error(f"Model prediction failed: {e}")
            log_audit_event(
                event_type='ai_error',
                user_id=user_context.get('user_id'),
                resource=self.model_name,
                action='predict',
                details={'error': str(e)}
            )
            return {
                'success': False,
                'error': 'Model prediction failed',
                'policy_decision': PolicyDecision.BLOCK.value
            }
        
        # Policy check - output
        output_decision, output_reason, modified_result = policy_engine.evaluate_output(
            raw_result,
            {
                'confidence': confidence,
                'model_name': self.model_name
            }
        )
        
        if output_decision == PolicyDecision.BLOCK:
            log_audit_event(
                event_type='ai_output_blocked',
                user_id=user_context.get('user_id'),
                resource=self.model_name,
                action='predict',
                details={'reason': output_reason, 'confidence': confidence}
            )
            return {
                'success': False,
                'error': f'Output blocked by policy: {output_reason}',
                'confidence': confidence,
                'policy_decision': output_decision.value
            }
        
        if output_decision == PolicyDecision.REVIEW:
            warnings.append(output_reason)
        
        # Log successful prediction
        inference_time = time.time() - start_time
        log_audit_event(
            event_type='ai_prediction',
            user_id=user_context.get('user_id'),
            resource=self.model_name,
            action='predict',
            details={
                'confidence': confidence,
                'inference_time': inference_time,
                'policy_decision': output_decision.value,
                'warnings': warnings
            }
        )
        
        return {
            'success': True,
            'result': modified_result if modified_result is not None else raw_result,
            'confidence': confidence,
            'policy_decision': output_decision.value,
            'warnings': warnings,
            'inference_time': inference_time
        }
    
    def _extract_confidence(self, result: Any) -> float:
        """Extract confidence score from model output"""
        if isinstance(result, dict) and 'confidence' in result:
            return result['confidence']
        return 1.0
    
    def disable(self):
        """Emergency kill switch"""
        self.is_enabled = False
        logger.critical(f"AI model {self.model_name} DISABLED")
    
    def enable(self):
        """Re-enable AI"""
        self.is_enabled = True
        logger.info(f"AI model {self.model_name} enabled")

def wrap_model(model, model_name: str) -> SafeAIWrapper:
    """Wrap any model with safety"""
    return SafeAIWrapper(model, model_name)
