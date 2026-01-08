"""
Automated Compliance Evidence Generation
Continuous evidence collection for SOC 2, ISO 27001, HIPAA, GDPR
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

class EvidenceType:
    ACCESS_LOG = "access_log"
    CHANGE_LOG = "change_log"
    BACKUP_LOG = "backup_log"
    VULNERABILITY_SCAN = "vulnerability_scan"
    TRAINING_COMPLETION = "training_completion"
    POLICY_ACKNOWLEDGMENT = "policy_acknowledgment"
    INCIDENT_RECORD = "incident_record"
    RISK_ASSESSMENT = "risk_assessment"
    ACCESS_REVIEW = "access_review"
    PENETRATION_TEST = "penetration_test"

class EvidenceGenerator:
    """
    Automated Compliance Evidence Generation
    - Continuous evidence collection
    - Evidence packaging for auditors
    - Evidence integrity verification
    - Automated evidence retention
    """
    
    def __init__(self):
        self.evidence_store = {}
        self.collection_rules = {}
        self.auditor_packages = {}
    
    def collect_evidence(self, evidence_type: str, 
                        control_id: str, data: Dict) -> str:
        """
        Collect evidence for a specific control
        
        Args:
            evidence_type: Type of evidence
            control_id: Control being evidenced (e.g., 'CC6.1')
            data: Evidence data
        
        Returns:
            Evidence ID
        """
        import uuid
        import hashlib
        
        evidence_id = f"EV-{uuid.uuid4().hex[:12]}"
        
        # Calculate evidence hash for integrity
        evidence_hash = hashlib.sha256(
            json.dumps(data, sort_keys=True).encode()
        ).hexdigest()
        
        evidence_record = {
            'evidence_id': evidence_id,
            'evidence_type': evidence_type,
            'control_id': control_id,
            'collected_at': datetime.utcnow().isoformat(),
            'data': data,
            'evidence_hash': evidence_hash,
            'retention_until': (
                datetime.utcnow() + timedelta(days=2555)  # 7 years
            ).isoformat()
        }
        
        # Store evidence
        if control_id not in self.evidence_store:
            self.evidence_store[control_id] = []
        
        self.evidence_store[control_id].append(evidence_record)
        
        return evidence_id
    
    def collect_access_evidence(self, user_id: str, resource: str,
                                action: str, result: str) -> str:
        """Collect access control evidence"""
        return self.collect_evidence(
            evidence_type=EvidenceType.ACCESS_LOG,
            control_id='CC6.1',  # Logical access control
            data={
                'user_id': user_id,
                'resource': resource,
                'action': action,
                'result': result,
                'timestamp': datetime.utcnow().isoformat(),
                'ip_address': 'logged',
                'user_agent': 'logged'
            }
        )
    
    def collect_change_evidence(self, change_id: str, change_type: str,
                               approver: str, outcome: str) -> str:
        """Collect change management evidence"""
        return self.collect_evidence(
            evidence_type=EvidenceType.CHANGE_LOG,
            control_id='CC8.1',  # Change management
            data={
                'change_id': change_id,
                'change_type': change_type,
                'requested_by': 'engineer',
                'approved_by': approver,
                'implemented_at': datetime.utcnow().isoformat(),
                'outcome': outcome,
                'rollback_available': True
            }
        )
    
    def collect_backup_evidence(self, backup_id: str, 
                               backup_type: str, success: bool) -> str:
        """Collect backup evidence"""
        return self.collect_evidence(
            evidence_type=EvidenceType.BACKUP_LOG,
            control_id='CC7.4',  # Backup & recovery
            data={
                'backup_id': backup_id,
                'backup_type': backup_type,
                'started_at': (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                'completed_at': datetime.utcnow().isoformat(),
                'success': success,
                'data_size_gb': 150.5,
                'verification_status': 'passed' if success else 'failed'
            }
        )
    
    def collect_training_evidence(self, user_id: str, 
                                  course: str, passed: bool) -> str:
        """Collect security training evidence"""
        return self.collect_evidence(
            evidence_type=EvidenceType.TRAINING_COMPLETION,
            control_id='CC1.4',  # Competence
            data={
                'user_id': user_id,
                'course_name': course,
                'completed_at': datetime.utcnow().isoformat(),
                'score': 95 if passed else 65,
                'passed': passed,
                'certificate_id': f"CERT-{user_id}-{course}"
            }
        )
    
    def collect_vulnerability_evidence(self, scan_id: str,
                                      vulnerabilities: List[Dict]) -> str:
        """Collect vulnerability scan evidence"""
        return self.collect_evidence(
            evidence_type=EvidenceType.VULNERABILITY_SCAN,
            control_id='CC7.1',  # Vulnerability management
            data={
                'scan_id': scan_id,
                'scan_date': datetime.utcnow().isoformat(),
                'vulnerabilities_found': len(vulnerabilities),
                'critical': sum(1 for v in vulnerabilities if v['severity'] == 'critical'),
                'high': sum(1 for v in vulnerabilities if v['severity'] == 'high'),
                'medium': sum(1 for v in vulnerabilities if v['severity'] == 'medium'),
                'low': sum(1 for v in vulnerabilities if v['severity'] == 'low'),
                'remediation_status': 'in_progress'
            }
        )
    
    def generate_auditor_package(self, control_ids: List[str],
                                start_date: datetime,
                                end_date: datetime) -> Dict:
        """
        Generate evidence package for auditors
        
        Returns:
            Package with all evidence for specified controls and period
        """
        import uuid
        
        package_id = f"PKG-{uuid.uuid4().hex[:12]}"
        
        package = {
            'package_id': package_id,
            'generated_at': datetime.utcnow().isoformat(),
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'controls': control_ids,
            'evidence': {}
        }
        
        # Collect evidence for each control
        for control_id in control_ids:
            if control_id in self.evidence_store:
                # Filter by date range
                evidence = [
                    e for e in self.evidence_store[control_id]
                    if start_date <= datetime.fromisoformat(e['collected_at']) <= end_date
                ]
                
                package['evidence'][control_id] = {
                    'control_id': control_id,
                    'evidence_count': len(evidence),
                    'evidence_items': evidence
                }
        
        # Store package
        self.auditor_packages[package_id] = package
        
        return package
    
    def verify_evidence_integrity(self, evidence_id: str) -> Dict:
        """Verify evidence has not been tampered with"""
        import hashlib
        
        # Find evidence
        for control_id, evidence_list in self.evidence_store.items():
            for evidence in evidence_list:
                if evidence['evidence_id'] == evidence_id:
                    # Recalculate hash
                    current_hash = hashlib.sha256(
                        json.dumps(evidence['data'], sort_keys=True).encode()
                    ).hexdigest()
                    
                    original_hash = evidence['evidence_hash']
                    
                    return {
                        'evidence_id': evidence_id,
                        'integrity_verified': current_hash == original_hash,
                        'original_hash': original_hash,
                        'current_hash': current_hash
                    }
        
        return {'error': 'Evidence not found'}
    
    def get_control_evidence_summary(self, control_id: str,
                                    days: int = 90) -> Dict:
        """Get evidence summary for a control"""
        if control_id not in self.evidence_store:
            return {'control_id': control_id, 'evidence_count': 0}
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        recent_evidence = [
            e for e in self.evidence_store[control_id]
            if datetime.fromisoformat(e['collected_at']) > cutoff
        ]
        
        return {
            'control_id': control_id,
            'evidence_count': len(recent_evidence),
            'oldest_evidence': min(
                (e['collected_at'] for e in recent_evidence),
                default=None
            ),
            'newest_evidence': max(
                (e['collected_at'] for e in recent_evidence),
                default=None
            ),
            'evidence_types': list(set(e['evidence_type'] for e in recent_evidence))
        }

# Global evidence generator
evidence_generator = EvidenceGenerator()
