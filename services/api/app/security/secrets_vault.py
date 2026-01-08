"""
Enterprise Secrets Management with Rotation
HashiCorp Vault Integration + Automatic Rotation
"""
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import base64
import json
from cryptography.fernet import Fernet

class SecretType:
    DATABASE = "database"
    API_KEY = "api_key"
    ENCRYPTION_KEY = "encryption_key"
    OAUTH_CLIENT = "oauth_client"
    CERTIFICATE = "certificate"

class SecretsVault:
    """
    Enterprise Secrets Management
    - Centralized secret storage
    - Automatic rotation
    - Audit logging
    - Tenant isolation
    - Version control
    """
    
    def __init__(self):
        self.secrets = {}  # In production: HashiCorp Vault
        self.rotation_policies = {}
        self.access_log = []
        self.rotation_schedule = {}
        self.master_key = Fernet.generate_key()
        self.cipher = Fernet(self.master_key)
    
    def store_secret(self, path: str, secret_data: Dict, 
                    secret_type: str, tenant_id: Optional[str] = None,
                    rotation_days: int = 90) -> Dict:
        """
        Store secret in vault with encryption
        
        Args:
            path: Secret path (e.g., 'database/postgres/prod')
            secret_data: Secret values
            secret_type: Type of secret
            tenant_id: Tenant isolation
            rotation_days: Auto-rotation interval
        """
        
        # Tenant isolation
        if tenant_id:
            path = f"tenants/{tenant_id}/{path}"
        
        # Encrypt secret data
        encrypted_data = self._encrypt_secret(secret_data)
        
        # Store with metadata
        secret_record = {
            'path': path,
            'encrypted_data': encrypted_data,
            'secret_type': secret_type,
            'tenant_id': tenant_id,
            'created_at': datetime.utcnow().isoformat(),
            'created_by': 'system',
            'version': 1,
            'rotation_days': rotation_days,
            'last_rotated': datetime.utcnow().isoformat(),
            'next_rotation': (datetime.utcnow() + timedelta(days=rotation_days)).isoformat()
        }
        
        self.secrets[path] = secret_record
        
        # Set up rotation policy
        if rotation_days > 0:
            self._schedule_rotation(path, rotation_days)
        
        # Audit log
        self._log_access('store', path, 'system', success=True)
        
        return {
            'path': path,
            'version': 1,
            'next_rotation': secret_record['next_rotation']
        }
    
    def retrieve_secret(self, path: str, requester_id: str,
                       tenant_id: Optional[str] = None) -> Optional[Dict]:
        """
        Retrieve and decrypt secret
        
        Returns:
            Decrypted secret data or None if not found/unauthorized
        """
        
        # Tenant isolation check
        if tenant_id:
            full_path = f"tenants/{tenant_id}/{path}"
        else:
            full_path = path
        
        # Check existence
        if full_path not in self.secrets:
            self._log_access('retrieve', full_path, requester_id, success=False)
            return None
        
        secret_record = self.secrets[full_path]
        
        # Verify tenant access
        if tenant_id and secret_record['tenant_id'] != tenant_id:
            self._log_access('retrieve', full_path, requester_id, 
                           success=False, reason='tenant_mismatch')
            return None
        
        # Decrypt
        decrypted_data = self._decrypt_secret(secret_record['encrypted_data'])
        
        # Audit log
        self._log_access('retrieve', full_path, requester_id, success=True)
        
        # Check if rotation needed
        self._check_rotation_needed(full_path)
        
        return {
            'data': decrypted_data,
            'version': secret_record['version'],
            'last_rotated': secret_record['last_rotated']
        }
    
    def rotate_secret(self, path: str, new_secret_data: Dict,
                     rotated_by: str) -> Dict:
        """
        Rotate secret to new value
        
        Maintains old version temporarily for zero-downtime rotation
        """
        
        if path not in self.secrets:
            return {'error': 'Secret not found'}
        
        old_record = self.secrets[path]
        
        # Encrypt new secret
        encrypted_data = self._encrypt_secret(new_secret_data)
        
        # Store old version
        old_version_path = f"{path}@v{old_record['version']}"
        self.secrets[old_version_path] = old_record.copy()
        
        # Update with new secret
        self.secrets[path].update({
            'encrypted_data': encrypted_data,
            'version': old_record['version'] + 1,
            'last_rotated': datetime.utcnow().isoformat(),
            'next_rotation': (
                datetime.utcnow() + 
                timedelta(days=old_record['rotation_days'])
            ).isoformat(),
            'rotated_by': rotated_by
        })
        
        # Audit log
        self._log_access('rotate', path, rotated_by, success=True)
        
        # Notify dependent services
        self._notify_rotation(path, old_record['version'] + 1)
        
        return {
            'path': path,
            'new_version': old_record['version'] + 1,
            'old_version_retained': True,
            'retention_period_days': 7
        }
    
    def auto_rotate_check(self):
        """Check all secrets for rotation needs (run daily)"""
        now = datetime.utcnow()
        rotated = []
        
        for path, secret in self.secrets.items():
            if '@v' in path:  # Skip old versions
                continue
            
            next_rotation = datetime.fromisoformat(secret['next_rotation'])
            
            if now >= next_rotation:
                # Auto-rotation needed
                result = self._trigger_auto_rotation(path, secret)
                rotated.append({
                    'path': path,
                    'result': result
                })
        
        return {
            'checked': len(self.secrets),
            'rotated': len(rotated),
            'details': rotated
        }
    
    def _trigger_auto_rotation(self, path: str, secret: Dict) -> Dict:
        """Trigger automatic rotation based on secret type"""
        secret_type = secret['secret_type']
        
        if secret_type == SecretType.DATABASE:
            # Generate new password
            new_secret = {
                'password': self._generate_secure_password()
            }
            return self.rotate_secret(path, new_secret, 'auto_rotation')
        
        elif secret_type == SecretType.API_KEY:
            # Generate new API key
            new_secret = {
                'api_key': self._generate_api_key()
            }
            return self.rotate_secret(path, new_secret, 'auto_rotation')
        
        elif secret_type == SecretType.ENCRYPTION_KEY:
            # Generate new encryption key
            new_secret = {
                'key': Fernet.generate_key().decode()
            }
            return self.rotate_secret(path, new_secret, 'auto_rotation')
        
        return {'status': 'rotation_not_configured'}
    
    def _encrypt_secret(self, data: Dict) -> str:
        """Encrypt secret data"""
        json_data = json.dumps(data)
        encrypted = self.cipher.encrypt(json_data.encode())
        return base64.b64encode(encrypted).decode()
    
    def _decrypt_secret(self, encrypted_data: str) -> Dict:
        """Decrypt secret data"""
        encrypted_bytes = base64.b64decode(encrypted_data)
        decrypted = self.cipher.decrypt(encrypted_bytes)
        return json.loads(decrypted.decode())
    
    def _generate_secure_password(self, length: int = 32) -> str:
        """Generate cryptographically secure password"""
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def _generate_api_key(self) -> str:
        """Generate secure API key"""
        import secrets
        return secrets.token_urlsafe(32)
    
    def _schedule_rotation(self, path: str, rotation_days: int):
        """Schedule automatic rotation"""
        next_rotation = datetime.utcnow() + timedelta(days=rotation_days)
        self.rotation_schedule[path] = next_rotation
    
    def _check_rotation_needed(self, path: str):
        """Check if secret needs rotation soon"""
        if path not in self.secrets:
            return
        
        secret = self.secrets[path]
        next_rotation = datetime.fromisoformat(secret['next_rotation'])
        days_until_rotation = (next_rotation - datetime.utcnow()).days
        
        if days_until_rotation <= 7:
            # Alert that rotation is needed soon
            self._send_rotation_alert(path, days_until_rotation)
    
    def _send_rotation_alert(self, path: str, days_remaining: int):
        """Alert about upcoming rotation"""
        # In production: send to Slack, email, PagerDuty
        print(f"⚠️  Secret rotation needed: {path} in {days_remaining} days")
    
    def _notify_rotation(self, path: str, new_version: int):
        """Notify dependent services of rotation"""
        # In production: publish to message queue
        # Services subscribe and update their configurations
        pass
    
    def _log_access(self, operation: str, path: str, 
                   user_id: str, success: bool, reason: str = None):
        """Log all secret access for audit"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'operation': operation,
            'path': path,
            'user_id': user_id,
            'success': success,
            'reason': reason
        }
        self.access_log.append(log_entry)
        
        # Also log to main audit system
        from ..ai_governance.ai_audit_logs import audit_logger
        audit_logger.log_event(
            event_type='secret_access',
            model_id=f"user:{user_id}",
            details=log_entry
        )
    
    def get_audit_log(self, start_date: datetime = None, 
                     end_date: datetime = None) -> List[Dict]:
        """Get secret access audit log"""
        filtered_log = self.access_log
        
        if start_date:
            filtered_log = [
                log for log in filtered_log
                if datetime.fromisoformat(log['timestamp']) >= start_date
            ]
        
        if end_date:
            filtered_log = [
                log for log in filtered_log
                if datetime.fromisoformat(log['timestamp']) <= end_date
            ]
        
        return filtered_log

# Global secrets vault
secrets_vault = SecretsVault()
