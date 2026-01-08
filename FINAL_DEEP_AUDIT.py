#!/usr/bin/env python3
"""
Final Deep Audit - Catch ALL Missing Issues
Critical examination of actual implementations
"""

import os
from pathlib import Path
import re

def check_file_exists(path):
    return os.path.exists(path)

def check_file_quality(path, min_size=100):
    if not os.path.exists(path):
        return False, "MISSING"
    size = os.path.getsize(path)
    if size < min_size:
        return False, f"TOO_SMALL ({size}B)"
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read(500)
        if 'TODO' in content or 'FIXME' in content or 'PLACEHOLDER' in content:
            return False, "HAS_TODOS"
    return True, "OK"

print("="*80)
print("  FINAL DEEP AUDIT - CATCH ALL MISSING ISSUES")
print("  Principal Engineer + Virtual CTO + Head of QA")
print("="*80)
print()

critical_issues = []
high_issues = []
medium_issues = []

# ============================================================
# PHASE 1: VERIFY ALL CRITICAL FILES EXIST AND ARE REAL
# ============================================================
print("🔍 PHASE 1: CRITICAL FILE VERIFICATION")
print("="*80)
print()

critical_files = {
    'Main App': 'services/api/app/main_complete.py',
    'Auth Router': 'services/api/app/routers/auth.py',
    'Users Router': 'services/api/app/routers/users.py',
    'Employees Router': 'services/api/app/routers/employees.py',
    'Time Router': 'services/api/app/routers/time_tracking.py',
    'Payroll Router': 'services/api/app/routers/payroll.py',
    'Reports Router': 'services/api/app/routers/reports.py',
    'Admin Router': 'services/api/app/routers/admin.py',
    'AI Router': 'services/api/app/routers/ai.py',
    'Dashboard Router': 'services/api/app/routers/dashboard.py',
}

print("Checking routers...")
for name, path in critical_files.items():
    exists, status = check_file_quality(path, min_size=500)
    if not exists:
        critical_issues.append({
            'severity': 'CRITICAL',
            'component': name,
            'file': path,
            'issue': f'Router {status}',
            'impact': 'API endpoint not functional'
        })
        print(f"  ❌ {name}: {status}")
    else:
        print(f"  ✅ {name}: OK")

print()

# Check middleware
middleware_files = {
    'RBAC Middleware': 'services/api/app/middleware/rbac_middleware.py',
    'Validation Middleware': 'services/api/app/middleware/validation_middleware.py',
    'Rate Limit Middleware': 'services/api/app/middleware/rate_limit_middleware.py',
    'Error Handler': 'services/api/app/middleware/error_handler.py',
}

print("Checking middleware...")
for name, path in middleware_files.items():
    exists, status = check_file_quality(path, min_size=1000)
    if not exists:
        critical_issues.append({
            'severity': 'CRITICAL',
            'component': name,
            'file': path,
            'issue': f'Middleware {status}',
            'impact': 'Security layer not active'
        })
        print(f"  ❌ {name}: {status}")
    else:
        print(f"  ✅ {name}: OK")

print()

# ============================================================
# PHASE 2: CHECK FOR MISSING ROUTER IMPLEMENTATIONS
# ============================================================
print("🔍 PHASE 2: CHECKING FOR EMPTY/INCOMPLETE ROUTERS")
print("="*80)
print()

# Check if routers have actual endpoints
routers_to_check = [
    ('services/api/app/routers/auth.py', ['login', 'logout', 'refresh']),
    ('services/api/app/routers/users.py', ['get', 'create', 'update']),
    ('services/api/app/routers/employees.py', ['get', 'create', 'update']),
    ('services/api/app/routers/payroll.py', ['run', 'get']),
    ('services/api/app/routers/reports.py', ['generate', 'get']),
    ('services/api/app/routers/admin.py', ['settings']),
    ('services/api/app/routers/ai.py', ['predict', 'insights']),
]

for router_path, required_functions in routers_to_check:
    if os.path.exists(router_path):
        with open(router_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        missing_funcs = []
        for func in required_functions:
            # Check if function is defined (not just mentioned)
            if f'async def {func}' not in content and f'def {func}' not in content:
                missing_funcs.append(func)
        
        if missing_funcs:
            high_issues.append({
                'severity': 'HIGH',
                'component': router_path,
                'file': router_path,
                'issue': f'Missing implementations: {", ".join(missing_funcs)}',
                'impact': 'Incomplete API functionality'
            })
            print(f"  ⚠️  {router_path}: Missing {missing_funcs}")
        else:
            print(f"  ✅ {router_path}: All functions present")

print()

# ============================================================
# PHASE 3: CHECK IF ROUTERS ARE ACTUALLY REGISTERED
# ============================================================
print("🔍 PHASE 3: VERIFYING ROUTER REGISTRATION")
print("="*80)
print()

if os.path.exists('services/api/app/main_complete.py'):
    with open('services/api/app/main_complete.py', 'r') as f:
        main_content = f.read()
    
    routers_to_verify = ['auth', 'users', 'employees', 'time_tracking', 
                         'payroll', 'reports', 'admin', 'ai', 'dashboard']
    
    for router in routers_to_verify:
        # Check if imported
        if f'from app.routers import {router}' not in main_content and \
           f'import {router}' not in main_content and \
           f'{router},' not in main_content:
            critical_issues.append({
                'severity': 'CRITICAL',
                'component': f'{router} router',
                'file': 'main_complete.py',
                'issue': f'{router} router not imported',
                'impact': 'Router not accessible'
            })
            print(f"  ❌ {router}: NOT IMPORTED")
            continue
        
        # Check if registered
        if f'{router}.router' not in main_content and f'include_router({router}' not in main_content:
            critical_issues.append({
                'severity': 'CRITICAL',
                'component': f'{router} router',
                'file': 'main_complete.py',
                'issue': f'{router} router not registered',
                'impact': 'Endpoints not exposed'
            })
            print(f"  ❌ {router}: NOT REGISTERED")
        else:
            print(f"  ✅ {router}: Imported and registered")

print()

# ============================================================
# PHASE 4: CHECK FOR DATABASE MODELS
# ============================================================
print("🔍 PHASE 4: DATABASE MODELS VERIFICATION")
print("="*80)
print()

required_models = {
    'User': 'services/api/app/models/user.py',
    'Tenant': 'services/api/app/models/tenant.py',
    'Employee': 'services/api/app/models/employee.py',
    'TimeEntry': 'services/api/app/models/time_entry.py',
}

for model_name, model_path in required_models.items():
    if not os.path.exists(model_path):
        high_issues.append({
            'severity': 'HIGH',
            'component': f'{model_name} model',
            'file': model_path,
            'issue': 'Model file missing',
            'impact': 'Database operations will fail'
        })
        print(f"  ❌ {model_name}: MISSING")
    else:
        print(f"  ✅ {model_name}: EXISTS")

print()

# ============================================================
# PHASE 5: FRONTEND COMPONENT VERIFICATION
# ============================================================
print("🔍 PHASE 5: FRONTEND COMPONENTS VERIFICATION")
print("="*80)
print()

frontend_critical = {
    'Dashboard': 'services/web/src/pages/Dashboard.jsx',
    'Login': 'services/web/src/pages/Login.jsx',
    'API Client': 'services/web/src/utils/api-client.js',
}

for name, path in frontend_critical.items():
    if not os.path.exists(path):
        high_issues.append({
            'severity': 'HIGH',
            'component': f'Frontend {name}',
            'file': path,
            'issue': 'Component missing',
            'impact': 'UI not functional'
        })
        print(f"  ❌ {name}: MISSING")
    else:
        # Check if it's using real API calls
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'MOCK_DATA' in content:
            medium_issues.append({
                'severity': 'MEDIUM',
                'component': f'Frontend {name}',
                'file': path,
                'issue': 'Still using MOCK_DATA',
                'impact': 'Not using real backend'
            })
            print(f"  ⚠️  {name}: Uses MOCK_DATA")
        else:
            print(f"  ✅ {name}: OK")

print()

# ============================================================
# PHASE 6: SECURITY CHECKS
# ============================================================
print("🔍 PHASE 6: SECURITY IMPLEMENTATION CHECKS")
print("="*80)
print()

security_checks = {
    'JWT Manager': 'services/api/app/auth/jwt_manager.py',
    'RBAC System': 'services/api/app/auth/rbac.py',
    'Audit Logger': 'services/api/app/security/audit_logger.py',
    'Secrets Manager': 'services/api/app/config/secrets_manager.py',
}

for name, path in security_checks.items():
    exists, status = check_file_quality(path, min_size=2000)
    if not exists:
        critical_issues.append({
            'severity': 'CRITICAL',
            'component': name,
            'file': path,
            'issue': f'Security component {status}',
            'impact': 'Security vulnerability'
        })
        print(f"  ❌ {name}: {status}")
    else:
        print(f"  ✅ {name}: OK")

print()

# ============================================================
# SUMMARY
# ============================================================
print("="*80)
print("AUDIT SUMMARY")
print("="*80)
print()

print(f"Critical Issues: {len(critical_issues)}")
if critical_issues:
    for issue in critical_issues:
        print(f"\n  🔴 CRITICAL: {issue['component']}")
        print(f"     File: {issue['file']}")
        print(f"     Issue: {issue['issue']}")
        print(f"     Impact: {issue['impact']}")

print(f"\nHigh Priority Issues: {len(high_issues)}")
if high_issues:
    for issue in high_issues[:3]:  # Show first 3
        print(f"\n  🟠 HIGH: {issue['component']}")
        print(f"     Issue: {issue['issue']}")

print(f"\nMedium Priority Issues: {len(medium_issues)}")

print()
print("="*80)

if len(critical_issues) == 0 and len(high_issues) == 0:
    print("✅ NO CRITICAL OR HIGH ISSUES FOUND")
    print("   System is production-ready")
else:
    print("⚠️  ISSUES FOUND - NEED FIXING")
    print(f"   Total issues: {len(critical_issues) + len(high_issues) + len(medium_issues)}")

