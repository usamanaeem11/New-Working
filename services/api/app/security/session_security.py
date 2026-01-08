"""
Session Hardening - Secure session management
"""
import secrets
from typing import Dict
from datetime import datetime, timedelta

class SessionSecurity:
    """Hardened session management"""
    
    def __init__(self):
        self.sessions = {}
    
    def create_session(self, user_id: str, device_info: Dict) -> str:
        """Create secure session"""
        session_token = secrets.token_urlsafe(32)
        
        self.sessions[session_token] = {
            'user_id': user_id,
            'device_info': device_info,
            'created_at': datetime.utcnow(),
            'last_activity': datetime.utcnow(),
            'ip_address': device_info.get('ip')
        }
        
        return session_token
    
    def validate_session(self, session_token: str) -> Dict:
        """Validate session security"""
        if session_token not in self.sessions:
            return {'valid': False, 'error': 'Invalid session'}
        
        session = self.sessions[session_token]
        
        # Check expiration (30 min idle timeout)
        if datetime.utcnow() - session['last_activity'] > timedelta(minutes=30):
            del self.sessions[session_token]
            return {'valid': False, 'error': 'Session expired'}
        
        session['last_activity'] = datetime.utcnow()
        
        return {'valid': True, 'user_id': session['user_id']}

session_security = SessionSecurity()
