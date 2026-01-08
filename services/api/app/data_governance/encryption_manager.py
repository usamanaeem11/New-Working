"""
Encryption Manager - Customer-managed encryption keys
"""
from typing import Dict
import base64
from cryptography.fernet import Fernet

class EncryptionManager:
    """Customer-managed encryption"""
    
    def __init__(self):
        self.tenant_keys = {}
    
    def generate_tenant_key(self, tenant_id: str) -> str:
        """Generate encryption key for tenant"""
        key = Fernet.generate_key()
        self.tenant_keys[tenant_id] = key
        return base64.b64encode(key).decode()
    
    def encrypt_field(self, data: str, tenant_id: str) -> str:
        """Encrypt sensitive field"""
        if tenant_id not in self.tenant_keys:
            self.generate_tenant_key(tenant_id)
        
        f = Fernet(self.tenant_keys[tenant_id])
        return f.encrypt(data.encode()).decode()
    
    def decrypt_field(self, encrypted_data: str, tenant_id: str) -> str:
        """Decrypt field"""
        if tenant_id not in self.tenant_keys:
            raise ValueError("No key for tenant")
        
        f = Fernet(self.tenant_keys[tenant_id])
        return f.decrypt(encrypted_data.encode()).decode()

encryption_manager = EncryptionManager()
