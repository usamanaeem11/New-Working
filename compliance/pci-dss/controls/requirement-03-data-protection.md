# PCI-DSS Requirement 3: Protect Stored Account Data

## 3.1 Data Protection Implementation

### 3.1.1 Data Encryption
**Status:** ✅ Implemented

**Implementation:**
- AES-256 encryption for data at rest
- TLS 1.3 for data in transit
- HSM for key storage (FIPS 140-2 Level 3)
- Per-tenant encryption keys

**Code Reference:**
- `services/api/app/security/hsm_integration.py`
- `services/api/app/data_layer/tenant_partitioning.py`

### 3.2 Cardholder Data Handling

**Scope:** Limited to payment processing only

**Controls:**
- ✅ PAN truncation (only last 4 digits displayed)
- ✅ CVV never stored
- ✅ Encryption keys rotated every 90 days
- ✅ Access logged and audited

### 3.3 Data Retention

**Policy:**
- Cardholder data retained only as long as needed for business/legal
- Automatic purge after 13 months
- Documented retention justification

**Implementation:** `services/api/app/data_layer/lifecycle_management.py`

## Compliance Status
**Assessment Date:** 2026-01-07  
**Status:** ✅ Compliant  
**Next Review:** 2026-04-07
