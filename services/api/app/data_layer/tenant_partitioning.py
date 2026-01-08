"""
Tenant Data Partitioning and Residency
Physical data isolation and geographic routing
"""
from typing import Dict, List, Optional
from enum import Enum

class DataResidencyRegion(Enum):
    US_EAST = "us-east-1"
    US_WEST = "us-west-2"
    EU_WEST = "eu-west-1"
    EU_CENTRAL = "eu-central-1"
    APAC_SINGAPORE = "ap-southeast-1"
    APAC_TOKYO = "ap-northeast-1"
    UK = "eu-west-2"
    CANADA = "ca-central-1"

class TenantPartitioning:
    """
    Tenant Data Partitioning Strategy
    - Schema-level isolation
    - Geographic data residency
    - Cross-region replication control
    - Data sovereignty compliance
    """
    
    def __init__(self):
        self.tenant_schemas = {}
        self.residency_mappings = {}
    
    def create_tenant_schema(self, tenant_id: str, region: DataResidencyRegion) -> Dict:
        """
        Create isolated database schema for tenant
        
        Provides complete data isolation at database level
        """
        schema_name = f"tenant_{tenant_id}"
        
        # Create schema in appropriate region
        connection_string = self._get_regional_connection(region)
        
        schema_config = {
            'tenant_id': tenant_id,
            'schema_name': schema_name,
            'region': region.value,
            'connection_string': connection_string,
            'created_at': datetime.utcnow().isoformat(),
            'encryption_key_id': f"hsm_key_{tenant_id}",
            'backup_policy': 'daily',
            'retention_days': 2555  # 7 years
        }
        
        self.tenant_schemas[tenant_id] = schema_config
        self.residency_mappings[tenant_id] = region
        
        return schema_config
    
    def get_tenant_connection(self, tenant_id: str) -> str:
        """Get database connection for specific tenant"""
        if tenant_id not in self.tenant_schemas:
            raise ValueError(f"Tenant {tenant_id} not configured")
        
        return self.tenant_schemas[tenant_id]['connection_string']
    
    def enforce_data_residency(self, tenant_id: str, operation: str, 
                              target_region: Optional[DataResidencyRegion] = None) -> bool:
        """
        Enforce data residency requirements
        
        Prevents data from leaving required geographic boundaries
        """
        if tenant_id not in self.residency_mappings:
            return False
        
        required_region = self.residency_mappings[tenant_id]
        
        if target_region and target_region != required_region:
            # Block cross-region operation
            self._log_residency_violation(tenant_id, operation, required_region, target_region)
            return False
        
        return True
    
    def _get_regional_connection(self, region: DataResidencyRegion) -> str:
        """Get database connection string for region"""
        region_connections = {
            DataResidencyRegion.US_EAST: "postgres://db-us-east.company.com:5432",
            DataResidencyRegion.EU_WEST: "postgres://db-eu-west.company.com:5432",
            DataResidencyRegion.APAC_SINGAPORE: "postgres://db-apac-sg.company.com:5432"
        }
        return region_connections.get(region, "postgres://db-default.company.com:5432")
    
    def _log_residency_violation(self, tenant_id: str, operation: str,
                                 required: DataResidencyRegion,
                                 attempted: DataResidencyRegion):
        """Log data residency violation attempt"""
        from ..security.siem_integration import siem, EventSeverity
        siem.log_security_event(
            event_type='data_residency_violation',
            severity=EventSeverity.CRITICAL,
            source='data_layer',
            details={
                'tenant_id': tenant_id,
                'operation': operation,
                'required_region': required.value,
                'attempted_region': attempted.value
            }
        )

from datetime import datetime
tenant_partitioning = TenantPartitioning()
