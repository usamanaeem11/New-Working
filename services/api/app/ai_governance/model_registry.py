"""
Model Registry - Central AI Model Management
Tracks all AI models, versions, and metadata
"""
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel
import json

class ModelMetadata(BaseModel):
    model_id: str
    name: str
    version: str
    type: str  # 'classification', 'regression', 'forecasting', etc.
    framework: str  # 'sklearn', 'tensorflow', 'pytorch', etc.
    trained_date: datetime
    training_data_hash: str
    performance_metrics: Dict
    approved_for_production: bool
    approval_date: Optional[datetime]
    approved_by: Optional[str]
    scope: List[str]  # ['employee_attrition', 'performance_prediction']
    limitations: List[str]
    legal_disclaimers: List[str]
    status: str  # 'training', 'testing', 'production', 'deprecated'

class ModelRegistry:
    """Central registry for all AI models"""
    
    def __init__(self):
        self.models: Dict[str, ModelMetadata] = {}
        self.version_history: Dict[str, List[str]] = {}
    
    def register_model(self, metadata: ModelMetadata) -> bool:
        """Register a new AI model or version"""
        # Validate model before registration
        if not self._validate_model(metadata):
            return False
        
        model_key = f"{metadata.name}:{metadata.version}"
        self.models[model_key] = metadata
        
        # Track version history
        if metadata.name not in self.version_history:
            self.version_history[metadata.name] = []
        self.version_history[metadata.name].append(metadata.version)
        
        # Log registration
        self._log_registration(metadata)
        
        return True
    
    def get_model(self, name: str, version: Optional[str] = None) -> Optional[ModelMetadata]:
        """Get model metadata"""
        if version:
            key = f"{name}:{version}"
            return self.models.get(key)
        
        # Get latest production version
        versions = self.version_history.get(name, [])
        for v in reversed(versions):
            key = f"{name}:{v}"
            model = self.models.get(key)
            if model and model.status == 'production':
                return model
        return None
    
    def approve_for_production(self, model_id: str, approved_by: str) -> bool:
        """Approve model for production use"""
        model = self.models.get(model_id)
        if not model:
            return False
        
        # Enterprise approval requirements
        if not model.performance_metrics:
            return False
        
        if not model.limitations:
            return False
        
        if not model.legal_disclaimers:
            return False
        
        model.approved_for_production = True
        model.approval_date = datetime.utcnow()
        model.approved_by = approved_by
        model.status = 'production'
        
        self._log_approval(model, approved_by)
        
        return True
    
    def deprecate_model(self, model_id: str, reason: str) -> bool:
        """Deprecate a model"""
        model = self.models.get(model_id)
        if not model:
            return False
        
        model.status = 'deprecated'
        self._log_deprecation(model, reason)
        
        return True
    
    def get_production_models(self) -> List[ModelMetadata]:
        """Get all production-approved models"""
        return [m for m in self.models.values() if m.status == 'production']
    
    def _validate_model(self, metadata: ModelMetadata) -> bool:
        """Validate model meets enterprise requirements"""
        # Must have performance metrics
        if not metadata.performance_metrics:
            return False
        
        # Must declare limitations
        if not metadata.limitations:
            return False
        
        # Must have legal disclaimers for enterprise use
        if not metadata.legal_disclaimers:
            return False
        
        # Must have defined scope
        if not metadata.scope:
            return False
        
        return True
    
    def _log_registration(self, metadata: ModelMetadata):
        """Log model registration to audit trail"""
        from .ai_audit_logs import AIAuditLogger
        logger = AIAuditLogger()
        logger.log_event(
            event_type='model_registered',
            model_id=f"{metadata.name}:{metadata.version}",
            details={'metadata': metadata.dict()}
        )
    
    def _log_approval(self, metadata: ModelMetadata, approved_by: str):
        """Log production approval"""
        from .ai_audit_logs import AIAuditLogger
        logger = AIAuditLogger()
        logger.log_event(
            event_type='model_approved',
            model_id=f"{metadata.name}:{metadata.version}",
            details={'approved_by': approved_by}
        )
    
    def _log_deprecation(self, metadata: ModelMetadata, reason: str):
        """Log model deprecation"""
        from .ai_audit_logs import AIAuditLogger
        logger = AIAuditLogger()
        logger.log_event(
            event_type='model_deprecated',
            model_id=f"{metadata.name}:{metadata.version}",
            details={'reason': reason}
        )

# Global registry instance
registry = ModelRegistry()
