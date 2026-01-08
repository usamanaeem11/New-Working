"""
Data Ownership Model - Define and enforce data ownership
"""
from typing import Dict, List

class DataOwnership:
    """Data ownership and access control"""
    
    def __init__(self):
        self.ownership_records = {}
    
    def assign_ownership(self, resource_id: str, owner_type: str,
                        owner_id: str, permissions: Dict) -> bool:
        """Assign resource ownership"""
        self.ownership_records[resource_id] = {
            'owner_type': owner_type,
            'owner_id': owner_id,
            'permissions': permissions
        }
        return True
    
    def get_data_inventory(self, owner_id: str) -> List[Dict]:
        """Get all data owned by entity"""
        return [
            {'resource_id': rid, **info}
            for rid, info in self.ownership_records.items()
            if info['owner_id'] == owner_id
        ]

data_ownership = DataOwnership()
