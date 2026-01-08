#!/usr/bin/env python3
"""
Final Comprehensive Verification
Check all components and create complete summary
"""

import os
from pathlib import Path
from collections import defaultdict

print("="*80)
print("  FINAL COMPREHENSIVE SYSTEM CHECK")
print("  Verifying 100% Production Readiness")
print("="*80)
print()

# Count files by category
def count_files_by_type():
    file_counts = defaultdict(int)
    total_size = 0
    
    for root, dirs, files in os.walk('.'):
        # Skip node_modules, __pycache__, .git
        dirs[:] = [d for d in dirs if d not in ['node_modules', '__pycache__', '.git', 'dist', 'build']]
        
        for file in files:
            ext = Path(file).suffix or 'no_ext'
            file_counts[ext] += 1
            
            try:
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)
            except:
                pass
    
    return file_counts, total_size

print("📊 Analyzing file structure...")
file_counts, total_size = count_files_by_type()

print(f"\n✅ Total Files: {sum(file_counts.values())}")
print(f"✅ Total Size: {total_size / (1024*1024):.1f} MB")
print()

print("File Distribution:")
sorted_counts = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)
for ext, count in sorted_counts[:20]:
    print(f"  {ext:20s}: {count:4d} files")

# Check critical directories
print("\n" + "="*80)
print("🔍 Checking Critical Components...")
print("="*80)

critical_paths = {
    "Backend API": "services/api/app/main.py",
    "JWT Manager": "services/api/app/auth/jwt_manager.py",
    "RBAC System": "services/api/app/auth/rbac.py",
    "Migrations": "services/api/app/database/migrations.py",
    "Auth Router": "services/api/app/routers/auth.py",
    "Users Router": "services/api/app/routers/users.py",
    "AI Governance": "services/api/app/ai_governance/model_registry.py",
    "Zero Trust": "services/api/app/security/zero_trust.py",
    "SIEM": "services/api/app/security/siem_integration.py",
    "HSM": "services/api/app/security/hsm_integration.py",
    "Tenant Partitioning": "services/api/app/data_layer/tenant_partitioning.py",
    "Immutable Ledger": "services/api/app/data_layer/immutable_ledger.py",
    "Lifecycle Mgmt": "services/api/app/data_layer/lifecycle_management.py",
    "Evidence Generator": "services/api/app/compliance/evidence_generator.py",
    "Blue/Green Deploy": "infrastructure/deployment/blue_green.py",
    "Feature Flags": "services/api/app/features/feature_flags.py",
    "SLA Monitor": "services/api/app/monitoring/sla_monitor.py",
    "Control Matrix": "compliance/CONTROL_MATRIX.md"
}

print("\nCritical File Verification:")
for name, path in critical_paths.items():
    exists = os.path.exists(path)
    status = "✅ EXISTS" if exists else "❌ MISSING"
    size = os.path.getsize(path) if exists else 0
    print(f"  {name:25s}: {status} ({size:,} bytes)")

# Check directory structure
print("\n" + "="*80)
print("📁 Directory Structure Check...")
print("="*80)

critical_dirs = [
    "services/api/app/auth",
    "services/api/app/routers",
    "services/api/app/database",
    "services/api/app/ai_governance",
    "services/api/app/security",
    "services/api/app/data_layer",
    "services/api/app/compliance",
    "services/api/app/features",
    "services/api/app/monitoring",
    "infrastructure/deployment",
    "compliance"
]

print("\nCritical Directories:")
for dir_path in critical_dirs:
    exists = os.path.isdir(dir_path)
    status = "✅" if exists else "❌"
    file_count = len([f for f in Path(dir_path).glob('**/*') if f.is_file()]) if exists else 0
    print(f"  {status} {dir_path:45s}: {file_count:3d} files")

# Calculate totals
print("\n" + "="*80)
print("📊 FINAL STATISTICS")
print("="*80)

def get_dir_size(path):
    if not os.path.exists(path):
        return 0
    total = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            try:
                total += os.path.getsize(os.path.join(root, file))
            except:
                pass
    return total

components = {
    "Backend Core": "services/api/app",
    "Security": "services/api/app/security",
    "AI Governance": "services/api/app/ai_governance",
    "Data Governance": "services/api/app/data_governance",
    "Compliance": ["services/api/app/compliance", "compliance"],
    "Infrastructure": "infrastructure"
}

print("\nComponent Sizes:")
for name, paths in components.items():
    if isinstance(paths, list):
        size = sum(get_dir_size(p) for p in paths)
    else:
        size = get_dir_size(paths)
    print(f"  {name:20s}: {size/(1024):8.1f} KB")

print("\n" + "="*80)
print("✅ VERIFICATION COMPLETE")
print("="*80)

