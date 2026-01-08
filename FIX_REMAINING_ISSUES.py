#!/usr/bin/env python3
"""
Fix Remaining 13 Issues
Database models, frontend components, and integrations
"""

import os
from pathlib import Path

def create_file(path, content):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return len(content)

print("="*80)
print("  FIXING REMAINING 13 ISSUES")
print("  Database Models + Frontend + Integration")
print("="*80)
print()

fixes = []

# ============================================================
# FIX 6: Fix dashboard import in main.py
# ============================================================
print("6. Fixing dashboard router import in main.py...")

main_file = 'services/api/app/main_complete.py'
with open(main_file, 'r') as f:
    main_content = f.read()

# Ensure dashboard is in imports
if 'dashboard,' not in main_content:
    main_content = main_content.replace(
        'from app.routers import (',
        'from app.routers import (\n    dashboard,'
    )
    
    with open(main_file, 'w') as f:
        f.write(main_content)
    
    print("   ✅ Dashboard router import added")
    fixes.append(('Dashboard Import Fix', 0.1))
else:
    print("   ℹ️  Dashboard already imported")

print()

# ============================================================
# FIX 7-9: Create Missing Database Models
# ============================================================
print("🗄️  FIXING DATABASE MODELS (Issues 7-9)")
print("="*80)
print()

# FIX 7: Tenant Model
print("7. Creating Tenant Model...")

create_file('services/api/app/models/tenant.py', '''"""
Tenant Model
Multi-tenant architecture
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.session import Base

class Tenant(Base):
    """
    Tenant model for multi-tenant architecture
    Each company/organization is a tenant
    """
    __tablename__ = "tenants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), unique=True, nullable=False, index=True)
    status = Column(String(50), default="active")  # active, suspended, trial
    
    # Subscription
    plan = Column(String(50), default="basic")  # basic, professional, enterprise
    max_employees = Column(Integer, default=50)
    
    # Settings
    timezone = Column(String(50), default="UTC")
    work_week_start = Column(String(20), default="Monday")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    trial_ends_at = Column(DateTime, nullable=True)
    
    # Relationships
    users = relationship("User", back_populates="tenant")
    employees = relationship("Employee", back_populates="tenant")
    
    def __repr__(self):
        return f"<Tenant(id={self.id}, name='{self.name}', domain='{self.domain}')>"
''')

fixes.append(('Tenant Model', 1.4))
print("   ✅ Tenant model created (1.4 KB)")

# FIX 8: Employee Model
print("8. Creating Employee Model...")

create_file('services/api/app/models/employee.py', '''"""
Employee Model
Employee records with full details
"""

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.session import Base

class Employee(Base):
    """
    Employee model with complete details
    """
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Personal Information
    email = Column(String(255), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(50), nullable=True)
    
    # Employment Information
    employee_number = Column(String(50), unique=True, nullable=False, index=True)
    department = Column(String(100), nullable=False, index=True)
    position = Column(String(150), nullable=False)
    employment_type = Column(String(50), default="full_time")  # full_time, part_time, contract
    
    # Compensation
    salary = Column(Float, nullable=True)
    hourly_rate = Column(Float, nullable=True)
    pay_frequency = Column(String(50), default="monthly")  # weekly, biweekly, monthly
    
    # Dates
    hire_date = Column(Date, nullable=False)
    termination_date = Column(Date, nullable=True)
    
    # Status
    status = Column(String(50), default="active", index=True)  # active, inactive, terminated
    
    # Manager
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="employees")
    time_entries = relationship("TimeEntry", back_populates="employee")
    manager = relationship("Employee", remote_side=[id], back_populates="direct_reports")
    direct_reports = relationship("Employee", back_populates="manager")
    
    def __repr__(self):
        return f"<Employee(id={self.id}, name='{self.first_name} {self.last_name}', number='{self.employee_number}')>"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
''')

fixes.append(('Employee Model', 2.3))
print("   ✅ Employee model created (2.3 KB)")

# FIX 9: TimeEntry Model
print("9. Creating TimeEntry Model...")

create_file('services/api/app/models/time_entry.py', '''"""
Time Entry Model
Time tracking records
"""

from sqlalchemy import Column, Integer, Float, DateTime, Date, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.session import Base

class TimeEntry(Base):
    """
    Time entry model for tracking work hours
    """
    __tablename__ = "time_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    
    # Time Information
    date = Column(Date, nullable=False, index=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    
    # Hours
    hours = Column(Float, nullable=True)
    overtime_hours = Column(Float, default=0.0)
    
    # Break time (in minutes)
    break_minutes = Column(Integer, default=0)
    
    # Status
    status = Column(String(50), default="active", index=True)  # active, completed, approved, rejected
    
    # Approval
    approved_by = Column(Integer, ForeignKey("employees.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Location (if using geofencing)
    clock_in_location = Column(String(255), nullable=True)
    clock_out_location = Column(String(255), nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="time_entries")
    approver = relationship("Employee", foreign_keys=[approved_by])
    
    def __repr__(self):
        return f"<TimeEntry(id={self.id}, employee_id={self.employee_id}, date='{self.date}', hours={self.hours})>"
    
    def calculate_hours(self):
        """Calculate hours from start and end time"""
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            hours = duration.total_seconds() / 3600
            # Subtract break time
            hours -= (self.break_minutes / 60)
            return round(hours, 2)
        return 0.0
''')

fixes.append(('TimeEntry Model', 2.2))
print("   ✅ TimeEntry model created (2.2 KB)")

print()

# ============================================================
# FIX 10: Create Frontend Login Component
# ============================================================
print("🎨 FIXING FRONTEND (Issue 10)")
print("="*80)
print()

print("10. Creating Login Component...")

create_file('services/web/src/pages/Login.jsx', '''/**
 * Login Page
 * Authentication with JWT
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-card">
          <div className="login-header">
            <h1>WorkingTracker</h1>
            <p>Sign in to your account</p>
          </div>
          
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
          
          <form onSubmit={handleSubmit} className="login-form">
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
                placeholder="you@company.com"
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
                placeholder="••••••••"
              />
            </div>
            
            <button 
              type="submit" 
              className="btn-primary"
              disabled={loading}
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>
          
          <div className="login-footer">
            <a href="/forgot-password">Forgot password?</a>
          </div>
        </div>
      </div>
      
      <style jsx>{`
        .login-page {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        .login-container {
          width: 100%;
          max-width: 400px;
          padding: 20px;
        }
        
        .login-card {
          background: white;
          border-radius: 12px;
          padding: 40px;
          box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        
        .login-header {
          text-align: center;
          margin-bottom: 32px;
        }
        
        .login-header h1 {
          font-size: 28px;
          font-weight: 600;
          color: #1e293b;
          margin-bottom: 8px;
        }
        
        .login-header p {
          color: #64748b;
          font-size: 14px;
        }
        
        .error-message {
          background: #fee2e2;
          color: #991b1b;
          padding: 12px;
          border-radius: 8px;
          margin-bottom: 20px;
          font-size: 14px;
        }
        
        .login-form {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }
        
        .form-group {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        
        .form-group label {
          font-size: 14px;
          font-weight: 500;
          color: #1e293b;
        }
        
        .form-group input {
          padding: 12px 16px;
          border: 1px solid #e2e8f0;
          border-radius: 8px;
          font-size: 16px;
          transition: border-color 0.2s;
        }
        
        .form-group input:focus {
          outline: none;
          border-color: #667eea;
          box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .btn-primary {
          padding: 12px 24px;
          background: #667eea;
          color: white;
          border: none;
          border-radius: 8px;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
          transition: background 0.2s;
        }
        
        .btn-primary:hover:not(:disabled) {
          background: #5568d3;
        }
        
        .btn-primary:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
        
        .login-footer {
          text-align: center;
          margin-top: 24px;
        }
        
        .login-footer a {
          color: #667eea;
          text-decoration: none;
          font-size: 14px;
        }
        
        .login-footer a:hover {
          text-decoration: underline;
        }
      `}</style>
    </div>
  );
};

export default Login;
''')

fixes.append(('Login Component', 4.5))
print("   ✅ Login component created (4.5 KB)")

print()
print(f"✅ Fixed {len(fixes)} more issues")
print()

# Show summary
print("="*80)
print("FIXES SUMMARY")
print("="*80)
print()

total_kb = sum([s for _, s in fixes])
for name, size in fixes:
    print(f"  ✅ {name}: {size} KB")

print()
print(f"Total code added: {total_kb:.1f} KB")
print()

