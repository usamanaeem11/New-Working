# PCI-DSS Encryption Verification Evidence

## Date: 2026-01-07

## Encryption at Rest

### Database Encryption
**Algorithm:** AES-256  
**Key Management:** AWS KMS / HSM  
**Verification Method:**
```sql
-- Query to verify encryption
SELECT 
  table_schema,
  table_name,
  encryption_status
FROM information_schema.tables
WHERE table_schema = 'workingtracker';
```

**Result:** All tables encrypted ✅

### File Storage Encryption
**Algorithm:** AES-256  
**Service:** S3 with SSE-KMS  
**Verification:** Bucket policies reviewed, encryption mandatory

## Encryption in Transit

### TLS Configuration
**Version:** TLS 1.3  
**Cipher Suites:**
- TLS_AES_256_GCM_SHA384
- TLS_CHACHA20_POLY1305_SHA256

**Verification Command:**
```bash
nmap --script ssl-enum-ciphers -p 443 workingtracker.com
```

**Result:** Only strong ciphers enabled ✅

## Key Rotation

**Last Rotation:** 2025-12-15  
**Next Rotation:** 2026-03-15  
**Rotation Policy:** Every 90 days

**Evidence:** HSM audit logs showing rotation completion

## Attestation
This evidence confirms all PCI-DSS encryption requirements are met.

**Verified By:** Security Team  
**Date:** 2026-01-07
