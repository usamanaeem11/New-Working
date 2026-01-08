#!/usr/bin/env python3
"""
Final Complete Audit
Find all missing functions, incomplete features, and gaps
"""

import os
from pathlib import Path
import re

print("="*80)
print("  FINAL COMPLETE AUDIT")
print("  Finding ALL Missing Functions and Gaps")
print("="*80)
print()

# Check for missing CRUD operations
print("🔍 AUDITING CRUD OPERATIONS...")
print("="*80)
print()

crud_dir = 'services/api/app/crud'
expected_cruds = {
    'employee': ['get_employee', 'get_employees', 'create_employee', 'update_employee', 'delete_employee'],
    'time_entry': ['get_time_entry', 'clock_in', 'clock_out', 'get_time_entries', 'approve_time_entry'],
    'payroll': ['create_payroll_run', 'get_payroll_runs', 'get_payroll_run', 'get_pay_stubs'],
    'report': ['generate_attendance_report', 'generate_hours_report', 'create_report', 'get_report'],
    'user': ['get_user', 'get_users', 'create_user', 'update_user', 'delete_user'],
    'setting': ['get_setting', 'get_all_settings', 'update_setting', 'get_feature_flag']
}

missing_functions = []

for file, functions in expected_cruds.items():
    filepath = f'{crud_dir}/{file}.py'
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()
            for func in functions:
                if f'def {func}(' not in content:
                    missing_functions.append((file, func))
                    print(f"   ⚠️ Missing: {file}.py -> {func}()")
    else:
        print(f"   ❌ Missing file: {file}.py")
        missing_functions.extend([(file, f) for f in functions])

if not missing_functions:
    print("   ✅ All CRUD operations present")

print()

# Check routers
print("🔍 AUDITING API ROUTERS...")
print("="*80)
print()

router_dir = 'services/api/app/routers'
expected_routers = {
    'employees': ['get_employees', 'get_employee', 'create_employee', 'update_employee', 'delete_employee'],
    'time_tracking': ['clock_in', 'clock_out', 'get_time_entries'],
    'payroll': ['run_payroll', 'get_payroll_runs', 'get_payroll_run'],
    'reports': ['generate_report', 'get_report', 'get_reports'],
    'users': ['get_users', 'get_user', 'create_user', 'update_user'],
    'settings': ['get_settings', 'update_settings'],
    'ai_real': ['predict_performance', 'predict_turnover'],
    'websocket': ['websocket_endpoint']
}

missing_routes = []

for file, routes in expected_routers.items():
    filepath = f'{router_dir}/{file}.py'
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()
            for route in routes:
                if f'def {route}(' not in content and f'async def {route}(' not in content:
                    missing_routes.append((file, route))
                    print(f"   ⚠️ Missing: {file}.py -> {route}()")
    else:
        print(f"   ❌ Missing file: {file}.py")

if not missing_routes:
    print("   ✅ All API routes present")

print()

# Platform completeness
print("🔍 AUDITING PLATFORM COMPLETENESS...")
print("="*80)
print()

platforms = {
    'Web': 'services/web/src/pages',
    'Mobile': 'apps/mobile/src/screens',
    'Desktop': 'apps/desktop/src/renderer/components',
    'Extension': 'apps/browser-extension/chrome'
}

for platform, path in platforms.items():
    if os.path.exists(path):
        files = len([f for f in os.listdir(path) if f.endswith(('.jsx', '.tsx', '.js', '.ts'))])
        print(f"   {platform}: {files} components")
    else:
        print(f"   ❌ {platform}: Directory missing")

print()
print("="*80)
print("AUDIT COMPLETE")
print("="*80)

