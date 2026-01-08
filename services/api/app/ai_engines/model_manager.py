"""
Model Lifecycle Manager
Handles versioning, rollback, and kill switches
"""

import os
import shutil
import json
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ModelManager:
    """
    Manages AI model lifecycle
    - Versioning
    - Rollback
    - Kill switches
    - Model metadata
    """
    
    def __init__(self, models_dir: str = 'models'):
        self.models_dir = models_dir
        self.metadata_file = os.path.join(models_dir, 'metadata.json')
        self.active_models = {}
        self.load_metadata()
    
    def load_metadata(self):
        """Load model metadata"""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {'models': {}, 'active': {}}
    
    def save_metadata(self):
        """Save model metadata"""
        os.makedirs(self.models_dir, exist_ok=True)
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def register_model(
        self,
        model_name: str,
        version: str,
        model_path: str,
        metrics: Dict[str, float],
        dataset_hash: str
    ):
        """
        Register a new model version
        
        Args:
            model_name: Name of model (e.g., 'performance', 'turnover')
            version: Version string (e.g., 'v1.2.0')
            model_path: Path to model file
            metrics: Training metrics
            dataset_hash: Hash of training data
        """
        
        if model_name not in self.metadata['models']:
            self.metadata['models'][model_name] = []
        
        model_info = {
            'version': version,
            'path': model_path,
            'metrics': metrics,
            'dataset_hash': dataset_hash,
            'registered_at': datetime.utcnow().isoformat(),
            'status': 'registered'
        }
        
        self.metadata['models'][model_name].append(model_info)
        self.save_metadata()
        
        logger.info(f"Registered model: {model_name} {version}")
    
    def promote_to_production(self, model_name: str, version: str) -> bool:
        """
        Promote model to production
        This is the ONLY way models go live
        """
        
        # Find model
        model_versions = self.metadata['models'].get(model_name, [])
        model = next((m for m in model_versions if m['version'] == version), None)
        
        if not model:
            logger.error(f"Model not found: {model_name} {version}")
            return False
        
        # Backup current production model
        if model_name in self.metadata['active']:
            current = self.metadata['active'][model_name]
            backup_path = f"{current['path']}.backup"
            shutil.copy2(current['path'], backup_path)
            logger.info(f"Backed up current model: {backup_path}")
        
        # Promote new model
        self.metadata['active'][model_name] = {
            'version': version,
            'path': model['path'],
            'promoted_at': datetime.utcnow().isoformat(),
            'previous_version': self.metadata['active'].get(model_name, {}).get('version')
        }
        
        model['status'] = 'production'
        self.save_metadata()
        
        logger.info(f"Promoted to production: {model_name} {version}")
        return True
    
    def rollback(self, model_name: str) -> bool:
        """
        ONE-CLICK ROLLBACK
        Returns to previous version
        """
        
        current = self.metadata['active'].get(model_name)
        if not current:
            logger.error(f"No active model to rollback: {model_name}")
            return False
        
        previous_version = current.get('previous_version')
        if not previous_version:
            logger.error(f"No previous version available: {model_name}")
            return False
        
        # Rollback to previous
        logger.warning(f"ROLLBACK: {model_name} from {current['version']} to {previous_version}")
        
        model_versions = self.metadata['models'][model_name]
        previous_model = next((m for m in model_versions if m['version'] == previous_version), None)
        
        if previous_model:
            self.metadata['active'][model_name] = {
                'version': previous_version,
                'path': previous_model['path'],
                'promoted_at': datetime.utcnow().isoformat(),
                'is_rollback': True
            }
            
            self.save_metadata()
            return True
        
        return False
    
    def disable_model(self, model_name: str):
        """
        KILL SWITCH
        Immediately disable model
        """
        
        if model_name in self.metadata['active']:
            logger.critical(f"KILL SWITCH ACTIVATED: Disabling {model_name}")
            
            self.metadata['active'][model_name]['status'] = 'disabled'
            self.metadata['active'][model_name]['disabled_at'] = datetime.utcnow().isoformat()
            self.save_metadata()
    
    def is_enabled(self, model_name: str) -> bool:
        """Check if model is enabled"""
        model = self.metadata['active'].get(model_name, {})
        return model.get('status') != 'disabled'
    
    def get_active_version(self, model_name: str) -> Optional[str]:
        """Get currently active model version"""
        return self.metadata['active'].get(model_name, {}).get('version')
    
    def list_versions(self, model_name: str) -> list:
        """List all versions of a model"""
        return self.metadata['models'].get(model_name, [])

# Global instance
model_manager = ModelManager()
