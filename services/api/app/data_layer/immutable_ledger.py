"""
Immutable Audit Ledger
Tamper-proof audit trail using blockchain concepts
"""
from typing import Dict, Optional
import hashlib
import json
from datetime import datetime

class AuditBlock:
    """Single block in the immutable audit chain"""
    
    def __init__(self, index: int, timestamp: str, data: Dict,
                 previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of block"""
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'data': self.data,
            'previous_hash': self.previous_hash
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

class ImmutableAuditLedger:
    """
    Blockchain-inspired Immutable Audit Trail
    - Tamper-proof logging
    - Chain integrity verification
    - Cryptographic proof of audit trail
    - Suitable for compliance audits
    """
    
    def __init__(self):
        self.chain = []
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """Create the first block in the chain"""
        genesis_block = AuditBlock(
            index=0,
            timestamp=datetime.utcnow().isoformat(),
            data={'event': 'genesis', 'description': 'Audit ledger initialized'},
            previous_hash='0'
        )
        self.chain.append(genesis_block)
    
    def add_audit_entry(self, event_type: str, user_id: str,
                       resource: str, action: str, result: str,
                       details: Dict) -> str:
        """
        Add audit entry to immutable ledger
        
        Once added, cannot be modified or deleted
        """
        previous_block = self.chain[-1]
        
        audit_data = {
            'event_type': event_type,
            'user_id': user_id,
            'resource': resource,
            'action': action,
            'result': result,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        new_block = AuditBlock(
            index=len(self.chain),
            timestamp=datetime.utcnow().isoformat(),
            data=audit_data,
            previous_hash=previous_block.hash
        )
        
        self.chain.append(new_block)
        
        return new_block.hash
    
    def verify_chain_integrity(self) -> Dict:
        """
        Verify entire audit chain hasn't been tampered with
        
        Returns verification status and any integrity issues
        """
        integrity_issues = []
        
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Verify hash is correct
            if current_block.hash != current_block.calculate_hash():
                integrity_issues.append({
                    'block_index': i,
                    'issue': 'hash_mismatch',
                    'expected': current_block.calculate_hash(),
                    'actual': current_block.hash
                })
            
            # Verify chain linkage
            if current_block.previous_hash != previous_block.hash:
                integrity_issues.append({
                    'block_index': i,
                    'issue': 'chain_broken',
                    'expected_previous': previous_block.hash,
                    'actual_previous': current_block.previous_hash
                })
        
        return {
            'verified': len(integrity_issues) == 0,
            'total_blocks': len(self.chain),
            'issues': integrity_issues
        }
    
    def get_audit_trail(self, user_id: Optional[str] = None,
                       resource: Optional[str] = None,
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None) -> List[Dict]:
        """Retrieve audit trail with filters"""
        results = []
        
        for block in self.chain[1:]:  # Skip genesis
            data = block.data
            
            # Apply filters
            if user_id and data.get('user_id') != user_id:
                continue
            if resource and data.get('resource') != resource:
                continue
            
            timestamp = datetime.fromisoformat(data['timestamp'])
            if start_date and timestamp < start_date:
                continue
            if end_date and timestamp > end_date:
                continue
            
            results.append({
                'block_index': block.index,
                'block_hash': block.hash,
                **data
            })
        
        return results
    
    def export_audit_package(self, start_date: datetime,
                            end_date: datetime) -> Dict:
        """Export audit package for regulators/auditors"""
        trail = self.get_audit_trail(start_date=start_date, end_date=end_date)
        integrity = self.verify_chain_integrity()
        
        return {
            'export_date': datetime.utcnow().isoformat(),
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'audit_entries': trail,
            'integrity_verified': integrity['verified'],
            'chain_length': len(self.chain),
            'genesis_hash': self.chain[0].hash,
            'latest_hash': self.chain[-1].hash
        }

immutable_ledger = ImmutableAuditLedger()
