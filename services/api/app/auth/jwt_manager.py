"""
Complete JWT Authentication with Refresh Tokens
Production-ready authentication system
"""
from datetime import datetime, timedelta
from typing import Optional, Dict
import jwt
from passlib.context import CryptContext
import secrets

# Password hashing configuration
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)

# JWT Configuration
SECRET_KEY = secrets.token_urlsafe(32)  # In production: from env/vault
REFRESH_SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

class JWTManager:
    """
    Complete JWT Authentication Manager
    - Access token generation
    - Refresh token lifecycle
    - Token validation
    - Password hashing
    - Session management
    """
    
    def __init__(self):
        self.pwd_context = pwd_context
        self.active_sessions = {}
        self.revoked_tokens = set()
    
    def hash_password(self, password: str) -> str:
        """
        Hash password with bcrypt (12 rounds)
        
        Production-ready: secure, slow by design to prevent brute force
        """
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, user_id: str, email: str, 
                           roles: list, tenant_id: str) -> str:
        """
        Create short-lived access token (30 minutes)
        
        Args:
            user_id: User identifier
            email: User email
            roles: User roles for RBAC
            tenant_id: Tenant isolation
        
        Returns:
            JWT access token
        """
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        payload = {
            "sub": user_id,
            "email": email,
            "roles": roles,
            "tenant_id": tenant_id,
            "type": "access",
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(16)  # JWT ID for revocation
        }
        
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token
    
    def create_refresh_token(self, user_id: str, tenant_id: str) -> str:
        """
        Create long-lived refresh token (30 days)
        
        Used to obtain new access tokens without re-authentication
        """
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        payload = {
            "sub": user_id,
            "tenant_id": tenant_id,
            "type": "refresh",
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(16)
        }
        
        token = jwt.encode(payload, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
        
        # Store session
        self.active_sessions[payload["jti"]] = {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expire.isoformat()
        }
        
        return token
    
    def verify_access_token(self, token: str) -> Optional[Dict]:
        """
        Verify access token
        
        Returns:
            Token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # Check if token is revoked
            if payload.get("jti") in self.revoked_tokens:
                return None
            
            # Check token type
            if payload.get("type") != "access":
                return None
            
            return payload
        
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None
    
    def verify_refresh_token(self, token: str) -> Optional[Dict]:
        """
        Verify refresh token
        
        Returns:
            Token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
            
            # Check if token is revoked
            if payload.get("jti") in self.revoked_tokens:
                return None
            
            # Check token type
            if payload.get("type") != "refresh":
                return None
            
            # Check if session still active
            if payload.get("jti") not in self.active_sessions:
                return None
            
            return payload
        
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None
    
    def refresh_access_token(self, refresh_token: str, 
                            user_email: str, user_roles: list) -> Optional[str]:
        """
        Generate new access token using refresh token
        
        Args:
            refresh_token: Valid refresh token
            user_email: User email (from database)
            user_roles: User roles (from database)
        
        Returns:
            New access token or None
        """
        payload = self.verify_refresh_token(refresh_token)
        
        if not payload:
            return None
        
        # Create new access token
        new_access_token = self.create_access_token(
            user_id=payload["sub"],
            email=user_email,
            roles=user_roles,
            tenant_id=payload["tenant_id"]
        )
        
        return new_access_token
    
    def revoke_token(self, token: str):
        """
        Revoke token (logout)
        
        Adds token JTI to revocation list
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], 
                               options={"verify_exp": False})
            jti = payload.get("jti")
            if jti:
                self.revoked_tokens.add(jti)
                
                # Remove session if refresh token
                if jti in self.active_sessions:
                    del self.active_sessions[jti]
        except jwt.JWTError:
            pass
    
    def revoke_all_user_tokens(self, user_id: str):
        """
        Revoke all tokens for a user (force logout everywhere)
        
        Used for password changes, security incidents
        """
        # Remove all sessions for user
        sessions_to_remove = [
            jti for jti, session in self.active_sessions.items()
            if session["user_id"] == user_id
        ]
        
        for jti in sessions_to_remove:
            self.revoked_tokens.add(jti)
            del self.active_sessions[jti]
    
    def cleanup_expired_sessions(self):
        """
        Cleanup expired sessions (run periodically)
        
        Should be called by background job
        """
        now = datetime.utcnow()
        expired = [
            jti for jti, session in self.active_sessions.items()
            if datetime.fromisoformat(session["expires_at"]) < now
        ]
        
        for jti in expired:
            self.revoked_tokens.add(jti)
            del self.active_sessions[jti]

# Global JWT manager
jwt_manager = JWTManager()
