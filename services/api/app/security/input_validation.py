"""
Input Validation Framework - Comprehensive input validation
"""
import re
from typing import Dict, Any

class InputValidator:
    """Enterprise input validation"""
    
    def validate_string(self, value: str, max_length: int = 255,
                       pattern: str = None) -> Dict:
        """Validate string input"""
        if len(value) > max_length:
            return {'valid': False, 'error': 'String too long'}
        
        if pattern and not re.match(pattern, value):
            return {'valid': False, 'error': 'Pattern mismatch'}
        
        # XSS prevention
        dangerous_chars = ['<', '>', 'script', 'javascript:']
        if any(char in value.lower() for char in dangerous_chars):
            return {'valid': False, 'error': 'Dangerous characters detected'}
        
        return {'valid': True, 'sanitized': value}
    
    def validate_email(self, email: str) -> Dict:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return {'valid': False, 'error': 'Invalid email format'}
        return {'valid': True}

input_validator = InputValidator()
