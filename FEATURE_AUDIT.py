#!/usr/bin/env python3
"""
Comprehensive Feature Audit
Check feature parity across all platforms and layers
"""

import os
from pathlib import Path
import re

print("="*80)
print("  COMPREHENSIVE FEATURE AUDIT")
print("  Cross-Platform Parity & Integration Analysis")
print("="*80)
print()

# Define all features
features = {
    'Authentication': {
        'components': ['login', 'logout', 'refresh_token', 'register', 'password_reset'],
        'category': 'Core'
    },
    'User Management': {
        'components': ['get_user', 'update_user', 'list_users', 'delete_user'],
        'category': 'Core'
    },
    'Employee Management': {
        'components': ['list_employees', 'get_employee', 'create_employee', 'update_employee', 'delete_employee'],
        'category': 'Core'
    },
    'Time Tracking': {
        'components': ['clock_in', 'clock_out', 'get_entries', 'edit_entry', 'approve_entry'],
        'category': 'Core'
    },
    'Dashboard': {
        'components': ['metrics', 'activity_feed', 'quick_actions', 'charts', 'notifications'],
        'category': 'Core'
    },
    'Payroll': {
        'components': ['run_payroll', 'view_history', 'export_data', 'pay_stubs'],
        'category': 'Core'
    },
    'Reports': {
        'components': ['attendance_report', 'hours_report', 'payroll_report', 'performance_report', 'export'],
        'category': 'Core'
    },
    'Settings': {
        'components': ['system_settings', 'user_preferences', 'company_settings', 'feature_flags'],
        'category': 'Core'
    },
    'AI Features': {
        'components': ['performance_prediction', 'turnover_prediction', 'insights', 'recommendations'],
        'category': 'AI'
    },
    'Offline Support': {
        'components': ['offline_queue', 'sync', 'local_cache', 'conflict_resolution'],
        'category': 'Platform'
    },
    'Real-time Updates': {
        'components': ['websocket', 'notifications', 'live_data', 'presence'],
        'category': 'Platform'
    },
    'Security': {
        'components': ['rbac', 'audit_log', 'rate_limiting', 'validation', 'encryption'],
        'category': 'Infrastructure'
    }
}

# Check backend
def check_backend():
    """Check backend API implementation"""
    results = {}
    
    backend_path = 'services/api/app/routers'
    
    for feature, data in features.items():
        results[feature] = {'backend': False, 'endpoints': []}
        
        # Check if router exists and has implementations
        router_map = {
            'Authentication': 'auth.py',
            'User Management': 'users.py',
            'Employee Management': 'employees.py',
            'Time Tracking': 'time_tracking.py',
            'Dashboard': 'dashboard.py',
            'Payroll': 'payroll.py',
            'Reports': 'reports.py',
            'Settings': 'admin.py',
            'AI Features': 'ai.py',
        }
        
        router_file = router_map.get(feature)
        if router_file:
            router_path = os.path.join(backend_path, router_file)
            if os.path.exists(router_path):
                with open(router_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Count endpoints
                endpoints = re.findall(r'@router\.(get|post|put|delete|patch)', content)
                if len(endpoints) >= 2:  # At least 2 endpoints
                    results[feature]['backend'] = True
                    results[feature]['endpoints'] = endpoints
    
    return results

# Check frontend
def check_frontend():
    """Check frontend implementation"""
    results = {}
    
    frontend_paths = [
        'services/web/src/pages',
        'services/web/src/components',
        'services/web/src/hooks'
    ]
    
    for feature, data in features.items():
        results[feature] = {'frontend': False, 'files': []}
        
        # Search for related files
        for base_path in frontend_paths:
            if os.path.exists(base_path):
                for root, dirs, files in os.walk(base_path):
                    for file in files:
                        if file.endswith(('.jsx', '.js', '.tsx', '.ts')):
                            file_path = os.path.join(root, file)
                            # Check if file relates to feature
                            feature_keywords = feature.lower().replace(' ', '_')
                            file_lower = file.lower()
                            
                            if any(keyword in file_lower for keyword in feature_keywords.split('_')):
                                results[feature]['files'].append(file)
                                results[feature]['frontend'] = True
    
    return results

# Check mobile
def check_mobile():
    """Check mobile implementation"""
    results = {}
    
    mobile_path = 'apps/mobile/src/screens'
    
    for feature, data in features.items():
        results[feature] = {'mobile': False, 'screens': []}
        
        if os.path.exists(mobile_path):
            for root, dirs, files in os.walk(mobile_path):
                for file in files:
                    if file.endswith(('.tsx', '.ts')):
                        feature_keywords = feature.lower().replace(' ', '_')
                        file_lower = file.lower()
                        
                        if any(keyword in file_lower for keyword in feature_keywords.split('_')):
                            results[feature]['screens'].append(file)
                            results[feature]['mobile'] = True
    
    return results

# Check desktop
def check_desktop():
    """Check desktop implementation"""
    results = {}
    
    desktop_path = 'apps/desktop/src/renderer/components'
    
    for feature, data in features.items():
        results[feature] = {'desktop': False, 'components': []}
        
        if os.path.exists(desktop_path):
            for root, dirs, files in os.walk(desktop_path):
                for file in files:
                    if file.endswith(('.jsx', '.js')):
                        feature_keywords = feature.lower().replace(' ', '_')
                        file_lower = file.lower()
                        
                        if any(keyword in file_lower for keyword in feature_keywords.split('_')):
                            results[feature]['components'].append(file)
                            results[feature]['desktop'] = True
    
    return results

# Check extension
def check_extension():
    """Check browser extension implementation"""
    results = {}
    
    extension_path = 'apps/browser-extension/chrome'
    
    for feature, data in features.items():
        results[feature] = {'extension': False}
        
        # Extension primarily supports time tracking
        if feature in ['Time Tracking', 'Authentication', 'Dashboard']:
            if os.path.exists(extension_path):
                results[feature]['extension'] = True
    
    return results

print("🔍 Auditing Backend API...")
backend_results = check_backend()

print("🔍 Auditing Frontend...")
frontend_results = check_frontend()

print("🔍 Auditing Mobile...")
mobile_results = check_mobile()

print("🔍 Auditing Desktop...")
desktop_results = check_desktop()

print("🔍 Auditing Extension...")
extension_results = check_extension()

print()
print("="*80)
print("FEATURE AUDIT RESULTS")
print("="*80)
print()

# Combine results
total_features = len(features)
features_with_backend = 0
features_with_frontend = 0
features_with_mobile = 0
features_with_desktop = 0
features_with_extension = 0
fully_integrated = 0

print(f"{'Feature':<25} {'Backend':<10} {'Frontend':<10} {'Mobile':<10} {'Desktop':<10} {'Extension':<10} {'Status':<10}")
print("-"*100)

for feature in features.keys():
    backend = '✅' if backend_results[feature]['backend'] else '❌'
    frontend = '✅' if frontend_results[feature]['frontend'] else '❌'
    mobile = '✅' if mobile_results[feature]['mobile'] else '❌'
    desktop = '✅' if desktop_results[feature]['desktop'] else '❌'
    extension = '✅' if extension_results[feature]['extension'] else '⚪'
    
    # Count
    if backend_results[feature]['backend']:
        features_with_backend += 1
    if frontend_results[feature]['frontend']:
        features_with_frontend += 1
    if mobile_results[feature]['mobile']:
        features_with_mobile += 1
    if desktop_results[feature]['desktop']:
        features_with_desktop += 1
    if extension_results[feature]['extension']:
        features_with_extension += 1
    
    # Determine status
    platforms = sum([
        backend_results[feature]['backend'],
        frontend_results[feature]['frontend'],
        mobile_results[feature]['mobile'],
        desktop_results[feature]['desktop']
    ])
    
    if platforms >= 3:
        status = '✅ Good'
        if platforms == 4:
            fully_integrated += 1
    elif platforms >= 2:
        status = '🟡 Partial'
    else:
        status = '🔴 Missing'
    
    print(f"{feature:<25} {backend:<10} {frontend:<10} {mobile:<10} {desktop:<10} {extension:<10} {status:<10}")

print("-"*100)
print(f"{'TOTALS:':<25} {features_with_backend}/{total_features:<9} {features_with_frontend}/{total_features:<9} {features_with_mobile}/{total_features:<9} {features_with_desktop}/{total_features:<9} {features_with_extension}/{total_features:<9}")

print()
print("="*80)
print("SUMMARY")
print("="*80)
print()
print(f"Total Features Defined:        {total_features}")
print(f"Fully Integrated (4 platforms): {fully_integrated}")
print(f"Partially Integrated:          {total_features - fully_integrated}")
print()
print(f"Backend Coverage:              {features_with_backend}/{total_features} ({int(features_with_backend/total_features*100)}%)")
print(f"Frontend Coverage:             {features_with_frontend}/{total_features} ({int(features_with_frontend/total_features*100)}%)")
print(f"Mobile Coverage:               {features_with_mobile}/{total_features} ({int(features_with_mobile/total_features*100)}%)")
print(f"Desktop Coverage:              {features_with_desktop}/{total_features} ({int(features_with_desktop/total_features*100)}%)")
print()

