"""
Production Secrets Manager
Secure secrets handling for production environments
Supports: AWS Secrets Manager, HashiCorp Vault, Environment Variables
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)

class SecretProvider(Enum):
    """Supported secret providers"""
    ENVIRONMENT = "environment"
    AWS_SECRETS = "aws_secrets_manager"
    HASHICORP_VAULT = "hashicorp_vault"
    AZURE_KEYVAULT = "azure_keyvault"

class SecretsManager:
    """
    Centralized secrets management
    Automatically detects provider and retrieves secrets securely
    """
    
    def __init__(self, provider: SecretProvider = SecretProvider.ENVIRONMENT):
        self.provider = provider
        self._cache = {}
        self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialize the secrets provider"""
        if self.provider == SecretProvider.AWS_SECRETS:
            try:
                import boto3
                self.client = boto3.client('secretsmanager')
                logger.info("AWS Secrets Manager initialized")
            except ImportError:
                logger.warning("boto3 not installed, falling back to environment")
                self.provider = SecretProvider.ENVIRONMENT
        
        elif self.provider == SecretProvider.HASHICORP_VAULT:
            try:
                import hvac
                vault_addr = os.getenv('VAULT_ADDR', 'http://localhost:8200')
                vault_token = os.getenv('VAULT_TOKEN')
                self.client = hvac.Client(url=vault_addr, token=vault_token)
                logger.info("HashiCorp Vault initialized")
            except ImportError:
                logger.warning("hvac not installed, falling back to environment")
                self.provider = SecretProvider.ENVIRONMENT
        
        logger.info(f"Secrets provider: {self.provider.value}")
    
    def get_secret(self, secret_name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a secret by name
        
        Args:
            secret_name: Name of the secret
            default: Default value if secret not found
            
        Returns:
            Secret value or default
        """
        # Check cache first
        if secret_name in self._cache:
            return self._cache[secret_name]
        
        value = None
        
        if self.provider == SecretProvider.ENVIRONMENT:
            value = os.getenv(secret_name, default)
        
        elif self.provider == SecretProvider.AWS_SECRETS:
            try:
                response = self.client.get_secret_value(SecretId=secret_name)
                if 'SecretString' in response:
                    value = response['SecretString']
                logger.info(f"Retrieved secret from AWS: {secret_name}")
            except Exception as e:
                logger.error(f"Failed to retrieve secret from AWS: {e}")
                value = default
        
        elif self.provider == SecretProvider.HASHICORP_VAULT:
            try:
                response = self.client.secrets.kv.v2.read_secret_version(
                    path=secret_name
                )
                value = response['data']['data'].get('value', default)
                logger.info(f"Retrieved secret from Vault: {secret_name}")
            except Exception as e:
                logger.error(f"Failed to retrieve secret from Vault: {e}")
                value = default
        
        # Cache the value
        if value:
            self._cache[secret_name] = value
        
        return value
    
    def get_database_url(self) -> str:
        """Get database connection URL"""
        return self.get_secret('DATABASE_URL', 
            'postgresql://user:password@localhost:5432/workingtracker'
        )
    
    def get_jwt_secret(self) -> str:
        """Get JWT signing secret"""
        return self.get_secret('JWT_SECRET_KEY', 
            'change-this-in-production-to-random-64-char-string'
        )
    
    def get_jwt_refresh_secret(self) -> str:
        """Get JWT refresh token secret"""
        return self.get_secret('JWT_REFRESH_SECRET_KEY',
            'change-this-refresh-secret-to-different-random-string'
        )
    
    def get_api_keys(self) -> Dict[str, str]:
        """Get third-party API keys"""
        return {
            'stripe': self.get_secret('STRIPE_SECRET_KEY', ''),
            'sendgrid': self.get_secret('SENDGRID_API_KEY', ''),
            'twilio': self.get_secret('TWILIO_API_KEY', ''),
            'aws_access_key': self.get_secret('AWS_ACCESS_KEY_ID', ''),
            'aws_secret_key': self.get_secret('AWS_SECRET_ACCESS_KEY', ''),
        }
    
    def rotate_secret(self, secret_name: str, new_value: str) -> bool:
        """
        Rotate a secret (for production use)
        
        Args:
            secret_name: Name of secret to rotate
            new_value: New secret value
            
        Returns:
            Success status
        """
        try:
            if self.provider == SecretProvider.AWS_SECRETS:
                self.client.update_secret(
                    SecretId=secret_name,
                    SecretString=new_value
                )
            
            elif self.provider == SecretProvider.HASHICORP_VAULT:
                self.client.secrets.kv.v2.create_or_update_secret(
                    path=secret_name,
                    secret={'value': new_value}
                )
            
            # Clear cache
            if secret_name in self._cache:
                del self._cache[secret_name]
            
            logger.info(f"Rotated secret: {secret_name}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to rotate secret: {e}")
            return False

# Global instance
secrets_manager = SecretsManager()
