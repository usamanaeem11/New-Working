"""
AI Policy Engine
Enforces rules on all AI inputs and outputs
CRITICAL: Safety layer for AI operations
"""

from typing import Dict, Any, List, Tuple
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)

class PolicyDecision(Enum):
    """Policy decision outcomes"""
    ALLOW = "allow"
    MODIFY = "modify"
    BLOCK = "block"
    REVIEW = "review"

class PolicyEngine:
    """
    Central AI policy enforcement
    Every AI operation must pass through this
    """
    
    # Sensitive content patterns
    SENSITIVE_PATTERNS = [
        r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
        r'\b\d{16}\b',  # Credit card
        r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b',  # Email
        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone
    ]
    
    # Confidence thresholds
    MIN_CONFIDENCE = 0.7
    BLOCK_BELOW_CONFIDENCE = 0.5
    
    # Rate limits
    MAX_REQUESTS_PER_USER_PER_HOUR = 100
    
    def __init__(self):
        self.request_counts = {}  # user_id -> count
    
    def evaluate_input(
        self, 
        input_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Tuple[PolicyDecision, str]:
        """
        Evaluate AI input against policies
        
        Returns:
            (decision, reason)
        """
        # Check rate limit
        user_id = user_context.get('user_id')
        if not self._check_rate_limit(user_id):
            return PolicyDecision.BLOCK, "Rate limit exceeded"
        
        # Check user permissions
        if not user_context.get('can_use_ai', False):
            return PolicyDecision.BLOCK, "AI access not permitted for user"
        
        # Sanitize input
        if 'prompt' in input_data:
            prompt = input_data['prompt']
            
            # Check length
            if len(prompt) > 10000:
                return PolicyDecision.BLOCK, "Prompt too long"
            
            # Check for injection attempts
            if self._detect_prompt_injection(prompt):
                return PolicyDecision.BLOCK, "Prompt injection detected"
        
        return PolicyDecision.ALLOW, "Input passed policy check"
    
    def evaluate_output(
        self,
        output: Any,
        model_metadata: Dict[str, Any]
    ) -> Tuple[PolicyDecision, str, Any]:
        """
        Evaluate AI output against policies
        
        Returns:
            (decision, reason, modified_output)
        """
        # Check confidence
        confidence = model_metadata.get('confidence', 1.0)
        
        if confidence < self.BLOCK_BELOW_CONFIDENCE:
            return PolicyDecision.BLOCK, "Confidence too low", None
        
        if confidence < self.MIN_CONFIDENCE:
            return PolicyDecision.REVIEW, "Low confidence - review required", output
        
        # Redact sensitive content
        if isinstance(output, str):
            modified = self._redact_sensitive_data(output)
            if modified != output:
                return PolicyDecision.MODIFY, "Sensitive data redacted", modified
        
        # Check for hallucination indicators
        if self._detect_hallucination_indicators(output, model_metadata):
            return PolicyDecision.REVIEW, "Possible hallucination detected", output
        
        return PolicyDecision.ALLOW, "Output passed policy check", output
    
    def _check_rate_limit(self, user_id: str) -> bool:
        """Check if user is within rate limits"""
        if user_id not in self.request_counts:
            self.request_counts[user_id] = 0
        
        self.request_counts[user_id] += 1
        
        # Reset counts hourly (simplified - use Redis in production)
        if self.request_counts[user_id] > self.MAX_REQUESTS_PER_USER_PER_HOUR:
            return False
        
        return True
    
    def _detect_prompt_injection(self, prompt: str) -> bool:
        """
        Detect prompt injection attempts
        """
        injection_patterns = [
            "ignore previous instructions",
            "disregard",
            "forget everything",
            "new instructions:",
            "system:",
            "jailbreak",
        ]
        
        prompt_lower = prompt.lower()
        for pattern in injection_patterns:
            if pattern in prompt_lower:
                logger.warning(f"Prompt injection detected: {pattern}")
                return True
        
        return False
    
    def _redact_sensitive_data(self, text: str) -> str:
        """
        Redact sensitive information from output
        """
        modified = text
        
        for pattern in self.SENSITIVE_PATTERNS:
            modified = re.sub(pattern, '[REDACTED]', modified, flags=re.IGNORECASE)
        
        return modified
    
    def _detect_hallucination_indicators(
        self,
        output: Any,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Detect potential hallucinations
        """
        # Check for uncertainty markers
        if isinstance(output, str):
            uncertainty_phrases = [
                "i'm not sure",
                "i don't know",
                "probably",
                "might be",
                "could be",
            ]
            
            output_lower = output.lower()
            uncertainty_count = sum(
                1 for phrase in uncertainty_phrases 
                if phrase in output_lower
            )
            
            if uncertainty_count >= 3:
                return True
        
        # Check for low token probabilities
        avg_token_prob = metadata.get('avg_token_probability', 1.0)
        if avg_token_prob < 0.3:
            return True
        
        return False

# Global instance
policy_engine = PolicyEngine()
