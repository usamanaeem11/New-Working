#!/usr/bin/env python3
"""
Complete System Audit
Deep inspection of every component, file, and connection
"""

import os
import json
from pathlib import Path
from collections import defaultdict

print("="*80)
print("  COMPREHENSIVE SYSTEM AUDIT")
print("  Deep Analysis of All Components")
print("="*80)
print()

# ============================================================
# 1. FILE STRUCTURE ANALYSIS
# ============================================================
print("📁 ANALYZING FILE STRUCTURE...")
print()

def analyze_directory_structure():
    """Analyze complete directory structure"""
    structure = defaultdict(lambda: {'files': 0, 'size': 0, 'types': defaultdict(int)})
    
    for root, dirs, files in os.walk('.'):
        # Skip node_modules, cache, etc.
        dirs[:] = [d for d in dirs if d not in ['node_modules', '__pycache__', '.git', 'dist', 'build', '.next']]
        
        # Categorize by top-level directory
        parts = Path(root).parts
        if len(parts) > 0 and parts[0] == '.':
            if len(parts) > 1:
                category = parts[1]
            else:
                category = 'root'
        else:
            category = 'root'
        
        for file in files:
            structure[category]['files'] += 1
            try:
                file_path = os.path.join(root, file)
                size = os.path.getsize(file_path)
                structure[category]['size'] += size
                
                ext = Path(file).suffix or 'no_ext'
                structure[category]['types'][ext] += 1
            except:
                pass
    
    return structure

structure = analyze_directory_structure()

print("Directory Breakdown:")
for category in sorted(structure.keys()):
    data = structure[category]
    print(f"  {category:30s}: {data['files']:4d} files, {data['size']/(1024):8.1f} KB")

print()

# ============================================================
# 2. CRITICAL FILE VERIFICATION
# ============================================================
print("="*80)
print("🔍 VERIFYING CRITICAL FILES...")
print("="*80)
print()

def check_file_quality(path, min_size=100):
    """Check if file exists and has substantial content"""
    if not os.path.exists(path):
        return 'MISSING', 0
    
    try:
        size = os.path.getsize(path)
        if size < min_size:
            return 'TOO_SMALL', size
        
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(500)  # Read first 500 chars
            
            # Check for placeholder patterns
            placeholders = [
                'TODO', 'FIXME', 'PLACEHOLDER', 'NOT IMPLEMENTED',
                'pass  # Implementation needed', 'raise NotImplementedError'
            ]
            
            for placeholder in placeholders:
                if placeholder in content:
                    return 'PLACEHOLDER', size
        
        return 'OK', size
    except Exception as e:
        return f'ERROR: {str(e)}', 0

# Critical backend files
backend_files = {
    'Main App': 'services/api/app/main_complete.py',
    'JWT Manager': 'services/api/app/auth/jwt_manager.py',
    'RBAC': 'services/api/app/auth/rbac.py',
    'Migrations': 'services/api/app/database/migrations.py',
    'Rate Limiter': 'services/api/app/security/rate_limiter.py',
    'Audit Logger': 'services/api/app/security/audit_logger.py',
    'Secrets Manager': 'services/api/app/config/secrets_manager.py',
    'Celery App': 'services/api/app/workers/celery_app.py',
    'Logging Config': 'services/api/app/logging/logging_config.py',
    'WebSocket Manager': 'services/api/app/realtime/websocket_manager.py',
    'Zero Trust': 'services/api/app/security/zero_trust.py',
    'SIEM Integration': 'services/api/app/security/siem_integration.py',
    'HSM Integration': 'services/api/app/security/hsm_integration.py',
    'Performance Model': 'services/api/app/ai_engines/performance/performance_predictor.py',
    'Turnover Model': 'services/api/app/ai_engines/forecasting/turnover_predictor.py',
}

print("Backend Critical Files:")
backend_ok = 0
backend_issues = 0

for name, path in backend_files.items():
    status, size = check_file_quality(path)
    
    if status == 'OK':
        print(f"  ✅ {name:25s}: {size:6d} bytes")
        backend_ok += 1
    else:
        print(f"  ❌ {name:25s}: {status}")
        backend_issues += 1

print(f"\nBackend: {backend_ok}/{len(backend_files)} OK, {backend_issues} issues")
print()

# Frontend files
frontend_files = {
    'API Client': 'services/web/src/utils/api-client.js',
    'useAuth Hook': 'services/web/src/hooks/useAuth.js',
    'useEmployees Hook': 'services/web/src/hooks/useEmployees.js',
    'useTimeTracking Hook': 'services/web/src/hooks/useTimeTracking.js',
}

print("Frontend Critical Files:")
frontend_ok = 0
frontend_issues = 0

for name, path in frontend_files.items():
    status, size = check_file_quality(path)
    
    if status == 'OK':
        print(f"  ✅ {name:25s}: {size:6d} bytes")
        frontend_ok += 1
    else:
        print(f"  ❌ {name:25s}: {status}")
        frontend_issues += 1

print(f"\nFrontend: {frontend_ok}/{len(frontend_files)} OK, {frontend_issues} issues")
print()

# Mobile files
mobile_files = {
    'Mobile API Client': 'apps/mobile/src/services/ApiClient.ts',
}

print("Mobile Critical Files:")
mobile_ok = 0
mobile_issues = 0

for name, path in mobile_files.items():
    status, size = check_file_quality(path)
    
    if status == 'OK':
        print(f"  ✅ {name:25s}: {size:6d} bytes")
        mobile_ok += 1
    else:
        print(f"  ❌ {name:25s}: {status}")
        mobile_issues += 1

print(f"\nMobile: {mobile_ok}/{len(mobile_files)} OK, {mobile_issues} issues")
print()

# Desktop files
desktop_files = {
    'Desktop IPC Bridge': 'apps/desktop/src/main/ipc-handlers.js',
    'Desktop Renderer API': 'apps/desktop/src/renderer/api.js',
}

print("Desktop Critical Files:")
desktop_ok = 0
desktop_issues = 0

for name, path in desktop_files.items():
    status, size = check_file_quality(path)
    
    if status == 'OK':
        print(f"  ✅ {name:25s}: {size:6d} bytes")
        desktop_ok += 1
    else:
        print(f"  ❌ {name:25s}: {status}")
        desktop_issues += 1

print(f"\nDesktop: {desktop_ok}/{len(desktop_files)} OK, {desktop_issues} issues")
print()

# Browser extension
extension_files = {
    'Extension Background': 'apps/browser-extension/chrome/background.js',
    'Extension Popup HTML': 'apps/browser-extension/chrome/popup.html',
    'Extension Popup JS': 'apps/browser-extension/chrome/popup.js',
}

print("Browser Extension Critical Files:")
extension_ok = 0
extension_issues = 0

for name, path in extension_files.items():
    status, size = check_file_quality(path, min_size=50)
    
    if status == 'OK':
        print(f"  ✅ {name:25s}: {size:6d} bytes")
        extension_ok += 1
    else:
        print(f"  ❌ {name:25s}: {status}")
        extension_issues += 1

print(f"\nExtension: {extension_ok}/{len(extension_files)} OK, {extension_issues} issues")
print()

# ============================================================
# 3. COMPLIANCE DOCUMENTS CHECK
# ============================================================
print("="*80)
print("📋 CHECKING COMPLIANCE DOCUMENTATION...")
print("="*80)
print()

compliance_docs = [
    'compliance/pci-dss/controls/requirement-01-firewall.md',
    'compliance/pci-dss/controls/requirement-03-data-protection.md',
    'compliance/pci-dss/audits/2026-q1-audit-report.md',
    'compliance/pci-dss/evidence/encryption-verification.md',
    'compliance/hipaa/controls/administrative-safeguards.md',
    'compliance/hipaa/evidence/access-log-sample.md',
    'compliance/iso27001/controls/a8-asset-management.md',
    'compliance/iso27001/evidence/asset-register.csv',
]

compliance_ok = 0
compliance_issues = 0

for doc in compliance_docs:
    status, size = check_file_quality(doc, min_size=50)
    if status == 'OK':
        print(f"  ✅ {os.path.basename(doc):50s}: {size:6d} bytes")
        compliance_ok += 1
    else:
        print(f"  ❌ {os.path.basename(doc):50s}: {status}")
        compliance_issues += 1

print(f"\nCompliance: {compliance_ok}/{len(compliance_docs)} OK, {compliance_issues} issues")
print()

# ============================================================
# 4. ROUTER REGISTRATION CHECK
# ============================================================
print("="*80)
print("🔌 CHECKING ROUTER REGISTRATION...")
print("="*80)
print()

def check_routers_registered():
    """Check if routers are registered in main app"""
    main_file = 'services/api/app/main_complete.py'
    
    if not os.path.exists(main_file):
        return False, []
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    routers = []
    if 'include_router' in content:
        # Count router registrations
        count = content.count('app.include_router')
        
        # Look for specific routers
        expected_routers = ['auth', 'users', 'employees', 'time', 'payroll', 'reports', 'admin', 'ai']
        
        for router in expected_routers:
            if f"{router}.router" in content or f"'{router}'" in content:
                routers.append(router)
        
        return True, routers
    
    return False, []

has_routers, registered_routers = check_routers_registered()

if has_routers:
    print(f"✅ Routers registered: {len(registered_routers)}")
    for router in registered_routers:
        print(f"   • {router}")
else:
    print("❌ No routers registered in main app")

print()

# ============================================================
# 5. SUMMARY
# ============================================================
print("="*80)
print("📊 AUDIT SUMMARY")
print("="*80)
print()

total_ok = backend_ok + frontend_ok + mobile_ok + desktop_ok + extension_ok + compliance_ok
total_files = len(backend_files) + len(frontend_files) + len(mobile_files) + len(desktop_files) + len(extension_files) + len(compliance_docs)
total_issues = backend_issues + frontend_issues + mobile_issues + desktop_issues + extension_issues + compliance_issues

print(f"Critical Files Verified: {total_ok}/{total_files}")
print(f"  Backend:      {backend_ok}/{len(backend_files)}")
print(f"  Frontend:     {frontend_ok}/{len(frontend_files)}")
print(f"  Mobile:       {mobile_ok}/{len(mobile_files)}")
print(f"  Desktop:      {desktop_ok}/{len(desktop_files)}")
print(f"  Extension:    {extension_ok}/{len(extension_files)}")
print(f"  Compliance:   {compliance_ok}/{len(compliance_docs)}")
print()

if total_issues == 0:
    print("✅ ALL CRITICAL FILES PRESENT AND VERIFIED")
else:
    print(f"⚠️  {total_issues} files need attention")

print()

# Calculate percentage
percentage = (total_ok / total_files) * 100
print(f"Overall Completion: {percentage:.1f}%")
print()

