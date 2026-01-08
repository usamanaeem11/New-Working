"""
AI Policy Engine
Every AI output goes through this - NO EXCEPTIONS
Legal safety layer
"""

import re
import logging
from typing import Dict, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class AIPolicy:
    """
    AI Output Policy Engine
    Blocks/modifies/allows AI responses based on rules
    """
    
    # Sensitive patterns to redact
    SENSITIVE_PATTERNS = [
        r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
        r'\b\d{16}\b',  # Credit card
        r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b',  # Email
        r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # Phone
    ]
    
    # Confidence thresholds
    MIN_CONFIDENCE = 0.7  # Below this, reject
    WARN_CONFIDENCE = 0.85  # Below this, warn
    
    def __init__(self):
        self.blocked_count = 0
        self.modified_count = 0
        self.allowed_count = 0
    
    def evaluate(
        self,
        output: str,
        confidence: float,
        model_version: str,
        user_context: Dict[str, Any]
    ) -> Tuple[str, str, Dict[str, Any]]:
        """
        Evaluate AI output against policies
        
        Args:
            output: AI generated text
            confidence: Model confidence score
            model_version: Model identifier
            user_context: User permissions/role
            
        Returns:
            (status, modified_output, metadata)
            status: 'allowed', 'modified', 'blocked'
        """
        
        metadata = {
            'timestamp': datetime.utcnow().isoformat(),
            'model_version': model_version,
            'original_confidence': confidence,
            'checks_performed': []
        }
        
        # Check 1: Confidence threshold
        if confidence < self.MIN_CONFIDENCE:
            logger.warning(f"Low confidence: {confidence}")
            metadata['checks_performed'].append('confidence_fail')
            self.blocked_count += 1
            return 'blocked', '', metadata
        
        # Check 2: Sensitive data detection
        modified_output, has_sensitive = self._redact_sensitive(output)
        if has_sensitive:
            metadata['checks_performed'].append('sensitive_data_redacted')
            self.modified_count += 1
            return 'modified', modified_output, metadata
        
        # Check 3: Role-based AI permissions
        if not self._check_user_permissions(user_context):
            logger.warning(f"User lacks AI permissions: {user_context.get('user_id')}")
            metadata['checks_performed'].append('permission_fail')
            self.blocked_count += 1
            return 'blocked', '', metadata
        
        # Check 4: Output length validation
        if len(output) > 10000:
            logger.warning(f"Output too long: {len(output)} chars")
            metadata['checks_performed'].append('length_violation')
            self.blocked_count += 1
            return 'blocked', '', metadata
        
        # Check 5: Hallucination patterns
        if self._detect_hallucination(output):
            logger.warning("Potential hallucination detected")
            metadata['checks_performed'].append('hallucination_risk')
            self.blocked_count += 1
            return 'blocked', '', metadata
        
        # All checks passed
        metadata['checks_performed'].append('all_passed')
        self.allowed_count += 1
        return 'allowed', output, metadata
    
    def _redact_sensitive(self, text: str) -> Tuple[str, bool]:
        """Redact sensitive information"""
        modified = text
        has_sensitive = False
        
        for pattern in self.SENSITIVE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                modified = re.sub(pattern, '[REDACTED]', modified, flags=re.IGNORECASE)
                has_sensitive = True
        
        return modified, has_sensitive
    
    def _check_user_permissions(self, user_context: Dict) -> bool:
        """Verify user has AI access permission"""
        permissions = user_context.get('permissions', [])
        return 'AI_VIEW_INSIGHTS' in permissions or 'AI_CONFIGURE' in permissions
    
    def _detect_hallucination(self, output: str) -> bool:
        """
        Detect potential hallucination patterns
        This is a simple heuristic - production should use more sophisticated methods
        """
        # Check for uncertainty markers
        uncertainty_words = [
            'i think', 'maybe', 'possibly', 'i believe',
            'i\'m not sure', 'uncertain'
        ]
        
        lower_output = output.lower()
        uncertainty_count = sum(1 for word in uncertainty_words if word in lower_output)
        
        # If too many uncertainty markers, flag
        return uncertainty_count > 3
    
    def get_stats(self) -> Dict[str, int]:
        """Get policy enforcement statistics"""
        return {
            'blocked': self.blocked_count,
            'modified': self.modified_count,
            'allowed': self.allowed_count,
            'total': self.blocked_count + self.modified_count + self.allowed_count
        }

# Global instance
ai_policy = AIPolicy()
