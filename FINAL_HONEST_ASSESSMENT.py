#!/usr/bin/env python3
"""
Final Honest Assessment
Check what's REAL vs what's scaffolding
"""

import os
from pathlib import Path

print("="*80)
print("  FINAL HONEST ASSESSMENT")
print("  Checking Every Component Against Your Audit")
print("="*80)
print()

def check_file_content(path, required_content):
    """Check if file exists and has required content"""
    if not os.path.exists(path):
        return False, "File missing"
    
    try:
        with open(path, 'r') as f:
            content = f.read()
            if len(content) < 100:
                return False, f"Too small ({len(content)} bytes)"
            
            missing = []
            for item in required_content:
                if item not in content:
                    missing.append(item)
            
            if missing:
                return False, f"Missing: {', '.join(missing[:3])}"
            
            return True, "REAL implementation"
    except:
        return False, "Read error"

# Check critical files
checks = {
    "main.py": {
        "path": "services/api/app/main_complete.py",
        "required": [
            "include_router",
            "SessionLocal",
            "lifespan",
            "CORSMiddleware",
            "get_current_user"
        ]
    },
    "JWT Manager": {
        "path": "services/api/app/auth/jwt_manager.py",
        "required": [
            "bcrypt",
            "create_access_token",
            "create_refresh_token",
            "verify_access_token"
        ]
    },
    "RBAC": {
        "path": "services/api/app/auth/rbac.py",
        "required": [
            "Permission",
            "Role",
            "has_permission",
            "require_permission"
        ]
    },
    "Rate Limiter": {
        "path": "services/api/app/security/rate_limiter.py",
        "required": [
            "is_rate_limited",
            "buckets",
            "token_bucket"
        ]
    },
    "Audit Logger": {
        "path": "services/api/app/security/audit_logger.py",
        "required": [
            "log_request",
            "log_auth_event",
            "log_data_access"
        ]
    },
    "PCI-DSS Controls": {
        "path": "compliance/pci-dss/controls/requirement-01-firewall.md",
        "required": [
            "Firewall Rules",
            "Network Security",
            "Implementation"
        ]
    },
    "Frontend API Client": {
        "path": "services/web/src/utils/api-client.js",
        "required": [
            "apiClient",
            "login",
            "getEmployees",
            "clockIn"
        ]
    },
    "Frontend Auth Hook": {
        "path": "services/web/src/hooks/useAuth.js",
        "required": [
            "useAuth",
            "AuthProvider",
            "login",
            "logout"
        ]
    },
    "Mobile API Client": {
        "path": "apps/mobile/src/services/ApiClient.ts",
        "required": [
            "ApiClient",
            "login",
            "clockIn",
            "AsyncStorage"
        ]
    },
    "Desktop IPC": {
        "path": "apps/desktop/src/main/ipc-handlers.js",
        "required": [
            "IPCBridge",
            "ipcMain",
            "setupHandlers",
            "auth:login"
        ]
    },
    "Browser Extension": {
        "path": "apps/browser-extension/chrome/background.js",
        "required": [
            "handleClockIn",
            "handleClockOut",
            "apiRequest",
            "chrome.runtime"
        ]
    },
    "AI Performance Model": {
        "path": "services/api/app/ai_engines/performance/performance_predictor.py",
        "required": [
            "PerformancePredictor",
            "RandomForestRegressor",
            "train",
            "predict"
        ]
    },
}

print("Checking Critical Components:")
print()

real_count = 0
issue_count = 0

for name, config in checks.items():
    status, message = check_file_content(config["path"], config["required"])
    
    if status:
        print(f"  ✅ {name:30s}: {message}")
        real_count += 1
    else:
        print(f"  ❌ {name:30s}: {message}")
        issue_count += 1

print()
print(f"Summary: {real_count} REAL, {issue_count} issues")
print()

# Check empty directories
print("Checking Previously Empty Directories:")
print()

dirs_to_check = [
    "compliance/pci-dss/controls",
    "compliance/pci-dss/audits",
    "compliance/pci-dss/evidence",
    "compliance/hipaa/controls",
    "compliance/hipaa/evidence",
    "compliance/iso27001/controls",
    "compliance/iso27001/evidence",
]

for dir_path in dirs_to_check:
    if os.path.exists(dir_path):
        files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
        if files:
            print(f"  ✅ {dir_path:50s}: {len(files)} files")
        else:
            print(f"  ❌ {dir_path:50s}: STILL EMPTY")
    else:
        print(f"  ❌ {dir_path:50s}: MISSING")

print()

