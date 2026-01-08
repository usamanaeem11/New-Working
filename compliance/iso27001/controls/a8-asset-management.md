# ISO 27001 Annex A.8 - Asset Management

## A.8.1 Responsibility for Assets

### A.8.1.1 Inventory of Assets
**Status:** ✅ Implemented

**Implementation:**
- CMDB maintains complete asset inventory
- All hardware, software, and data assets catalogued
- Asset ownership assigned
- Regular inventory audits (quarterly)

**Evidence:**
- Asset register: `compliance/iso27001/evidence/asset-register.csv`
- Last audit: 2026-01-01

### A.8.1.2 Ownership of Assets
**Status:** ✅ Implemented

**Process:**
- Each asset assigned to owner upon creation
- Owner responsible for:
  - Asset security
  - Access approvals
  - Disposal decisions

**Code:** `services/api/app/data_governance/data_ownership.py`

### A.8.1.3 Acceptable Use of Assets
**Status:** ✅ Implemented

**Policy:**
- Acceptable Use Policy v2.0
- All employees acknowledge upon hire
- Annual re-acknowledgment required
- Violations result in disciplinary action

## A.8.2 Information Classification

### A.8.2.1 Classification of Information
**Status:** ✅ Implemented

**Classification Levels:**
1. **Public** - No restrictions
2. **Internal** - Employees only
3. **Confidential** - Need-to-know basis
4. **Restricted** - Highly sensitive, executive approval

**Implementation:**
- Automated classification based on data type
- Manual override available
- Classification displayed in all systems

**Code:** `services/api/app/data_governance/data_classification.py`

### A.8.2.2 Labeling of Information
**Status:** ✅ Implemented

**Labeling Methods:**
- Electronic: Metadata tags
- Physical: Color-coded labels
- Email: Subject line prefixes

### A.8.2.3 Handling of Assets
**Status:** ✅ Implemented

**Handling Procedures:**
- Public: No special handling
- Internal: Encrypted in transit
- Confidential: Encrypted at rest and in transit
- Restricted: Hardware-encrypted devices only

## A.8.3 Media Handling

### A.8.3.1 Management of Removable Media
**Status:** ✅ Implemented

**Policy:**
- USB drives must be encrypted and approved
- External hard drives tracked in asset register
- Media sanitization before disposal

### A.8.3.2 Disposal of Media
**Status:** ✅ Implemented

**Process:**
1. Identify media for disposal
2. Remove all data (3-pass wipe minimum)
3. Physical destruction if highly sensitive
4. Certificate of destruction retained

### A.8.3.3 Physical Media Transfer
**Status:** ✅ Implemented

**Requirements:**
- Encrypted media for confidential data
- Chain of custody documentation
- Approved courier services only

## Compliance Status
**Assessment Date:** 2026-01-07  
**Status:** ✅ Compliant  
**Auditor:** Internal  
**Next Review:** 2026-07-07
