"""
Model Versioning - Semantic versioning for AI models
"""
from typing import Dict, List
import re

class ModelVersioning:
    """Semantic versioning for AI models"""
    
    def __init__(self):
        self.version_history = {}
    
    def create_version(self, model_name: str, version: str,
                      changes: List[str], breaking: bool = False) -> bool:
        """Create new model version"""
        
        if not self._validate_semver(version):
            return False
        
        if model_name not in self.version_history:
            self.version_history[model_name] = []
        
        version_info = {
            'version': version,
            'changes': changes,
            'breaking': breaking,
            'created_at': datetime.utcnow().isoformat()
        }
        
        self.version_history[model_name].append(version_info)
        return True
    
    def _validate_semver(self, version: str) -> bool:
        """Validate semantic version format"""
        pattern = r'^\d+\.\d+\.\d+$'
        return bool(re.match(pattern, version))

model_versioning = ModelVersioning()
