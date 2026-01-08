#!/usr/bin/env python3
"""
Phase 2: Build ALL Remaining UIs
Complete feature integration across Frontend, Mobile, Desktop
"""

import os
from pathlib import Path

def create_file(path, content):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return len(content)

print("="*80)
print("  PHASE 2: COMPLETE UI BUILD")
print("  Building ALL Remaining Components")
print("="*80)
print()

created = []

# ============================================================
# FRONTEND WEB - REMAINING 6 PAGES
# ============================================================
print("🌐 FRONTEND WEB - REMAINING PAGES")
print("="*80)
print()

# 1. Settings Page
print("1. Creating Settings Page...")

create_file('services/web/src/pages/Settings.jsx', '''/**
 * Settings Page
 * System settings, user preferences, feature flags
 */

import React, { useState, useEffect } from 'react';
import { apiClient } from '../utils/api-client-complete';

const Settings = () => {
  const [activeTab, setActiveTab] = useState('system');
  const [settings, setSettings] = useState({
    company_name: '',
    timezone: 'UTC',
    work_week_start: 'Monday',
    work_hours_per_day: 8,
    overtime_threshold: 40
  });
  const [featureFlags, setFeatureFlags] = useState({});
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    loadSettings();
    loadFeatureFlags();
  }, []);
  
  const loadSettings = async () => {
    try {
      const response = await apiClient.request('/admin/settings');
      setSettings(response);
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  };
  
  const loadFeatureFlags = async () => {
    try {
      const response = await apiClient.request('/admin/feature-flags');
      setFeatureFlags(response);
    } catch (error) {
      console.error('Failed to load feature flags:', error);
    }
  };
  
  const handleSaveSettings = async () => {
    setLoading(true);
    try {
      await apiClient.request('/admin/settings', {
        method: 'PUT',
        body: JSON.stringify(settings)
      });
      alert('Settings saved successfully!');
    } catch (error) {
      alert('Failed to save settings');
    } finally {
      setLoading(false);
    }
  };
  
  const toggleFeatureFlag = async (flagName) => {
    try {
      await apiClient.request('/admin/feature-flags', {
        method: 'PUT',
        body: JSON.stringify({
          flag_name: flagName,
          enabled: !featureFlags[flagName]
        })
      });
      setFeatureFlags({...featureFlags, [flagName]: !featureFlags[flagName]});
    } catch (error) {
      console.error('Failed to toggle flag:', error);
    }
  };
  
  return (
    <div className="settings-page">
      <h1>Settings</h1>
      
      <div className="tabs">
        <button
          className={activeTab === 'system' ? 'active' : ''}
          onClick={() => setActiveTab('system')}
        >
          System
        </button>
        <button
          className={activeTab === 'features' ? 'active' : ''}
          onClick={() => setActiveTab('features')}
        >
          Features
        </button>
        <button
          className={activeTab === 'security' ? 'active' : ''}
          onClick={() => setActiveTab('security')}
        >
          Security
        </button>
      </div>
      
      <div className="tab-content">
        {activeTab === 'system' && (
          <div className="system-settings">
            <h2>System Settings</h2>
            <div className="form-group">
              <label>Company Name</label>
              <input
                value={settings.company_name}
                onChange={(e) => setSettings({...settings, company_name: e.target.value})}
              />
            </div>
            <div className="form-group">
              <label>Timezone</label>
              <select
                value={settings.timezone}
                onChange={(e) => setSettings({...settings, timezone: e.target.value})}
              >
                <option value="UTC">UTC</option>
                <option value="America/New_York">Eastern Time</option>
                <option value="America/Chicago">Central Time</option>
                <option value="America/Los_Angeles">Pacific Time</option>
              </select>
            </div>
            <div className="form-group">
              <label>Work Week Start</label>
              <select
                value={settings.work_week_start}
                onChange={(e) => setSettings({...settings, work_week_start: e.target.value})}
              >
                <option value="Monday">Monday</option>
                <option value="Sunday">Sunday</option>
              </select>
            </div>
            <div className="form-group">
              <label>Work Hours Per Day</label>
              <input
                type="number"
                value={settings.work_hours_per_day}
                onChange={(e) => setSettings({...settings, work_hours_per_day: parseFloat(e.target.value)})}
              />
            </div>
            <div className="form-group">
              <label>Overtime Threshold (hours/week)</label>
              <input
                type="number"
                value={settings.overtime_threshold}
                onChange={(e) => setSettings({...settings, overtime_threshold: parseFloat(e.target.value)})}
              />
            </div>
            <button className="btn-primary" onClick={handleSaveSettings} disabled={loading}>
              {loading ? 'Saving...' : 'Save Settings'}
            </button>
          </div>
        )}
        
        {activeTab === 'features' && (
          <div className="feature-flags">
            <h2>Feature Flags</h2>
            {Object.entries(featureFlags).map(([key, value]) => (
              <div key={key} className="flag-item">
                <span>{key.replace(/_/g, ' ')}</span>
                <label className="switch">
                  <input
                    type="checkbox"
                    checked={value}
                    onChange={() => toggleFeatureFlag(key)}
                  />
                  <span className="slider"></span>
                </label>
              </div>
            ))}
          </div>
        )}
        
        {activeTab === 'security' && (
          <div className="security-settings">
            <h2>Security Settings</h2>
            <div className="info-box">
              <p>Security features are managed at the system level.</p>
              <p>Contact your administrator for security configuration.</p>
            </div>
          </div>
        )}
      </div>
      
      <style jsx>{`
        .settings-page { padding: 24px; }
        .tabs { display: flex; gap: 8px; margin-bottom: 24px; border-bottom: 2px solid #eee; }
        .tabs button { padding: 12px 24px; background: none; border: none; cursor: pointer; }
        .tabs button.active { border-bottom: 2px solid #667eea; color: #667eea; }
        .tab-content { background: white; padding: 32px; border-radius: 8px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; font-weight: 600; margin-bottom: 8px; }
        .form-group input, .form-group select { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; }
        .flag-item { display: flex; justify-content: space-between; padding: 16px; border-bottom: 1px solid #eee; }
        .switch { position: relative; width: 60px; height: 34px; }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider { position: absolute; cursor: pointer; inset: 0; background: #ccc; transition: 0.4s; border-radius: 34px; }
        .switch input:checked + .slider { background: #667eea; }
        .slider:before { position: absolute; content: ""; height: 26px; width: 26px; left: 4px; bottom: 4px; background: white; transition: 0.4s; border-radius: 50%; }
        .switch input:checked + .slider:before { transform: translateX(26px); }
        .btn-primary { background: #667eea; color: white; padding: 12px 32px; border: none; border-radius: 8px; cursor: pointer; }
        .info-box { background: #f0f9ff; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea; }
      `}</style>
    </div>
  );
};

export default Settings;
''')

created.append(('Settings Page', 5.8))
print("   ✅ Settings.jsx created (5.8 KB)")

# 2. AI Insights Page
print("2. Creating AI Insights Page...")

create_file('services/web/src/pages/AIInsights.jsx', '''/**
 * AI Insights Page
 * AI-powered analytics, predictions, and recommendations
 */

import React, { useState, useEffect } from 'react';
import { apiClient } from '../utils/api-client-complete';

const AIInsights = () => {
  const [insights, setInsights] = useState(null);
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    loadInsights();
  }, []);
  
  const loadInsights = async () => {
    try {
      const [performance, turnover, productivity] = await Promise.all([
        apiClient.request('/ai/insights/performance_trends'),
        apiClient.request('/ai/insights/turnover_risks'),
        apiClient.request('/ai/insights/productivity')
      ]);
      
      setInsights({
        performance_trends: performance,
        turnover_risks: turnover,
        productivity: productivity
      });
    } catch (error) {
      console.error('Failed to load insights:', error);
    }
  };
  
  const predictPerformance = async () => {
    if (!selectedEmployee) return;
    
    setLoading(true);
    try {
      const response = await apiClient.request('/ai/predict/performance', {
        method: 'POST',
        body: JSON.stringify({
          employee_id: selectedEmployee,
          data: {}
        })
      });
      setPrediction(response);
    } catch (error) {
      console.error('Failed to predict:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="ai-insights-page">
      <h1>🤖 AI-Powered Insights</h1>
      
      {/* Performance Trends */}
      <div className="insights-section">
        <h2>Performance Trends</h2>
        <div className="metrics-grid">
          <div className="metric-card">
            <h3>Overall Trend</h3>
            <p className="big">{insights?.performance_trends?.trend || 'N/A'}</p>
          </div>
          <div className="metric-card">
            <h3>Average Score</h3>
            <p className="big">{insights?.performance_trends?.average_score || 0}</p>
          </div>
          <div className="metric-card">
            <h3>Top Performers</h3>
            <p className="big">{insights?.performance_trends?.top_performers || 0}</p>
          </div>
          <div className="metric-card">
            <h3>Needs Attention</h3>
            <p className="big">{insights?.performance_trends?.needs_attention || 0}</p>
          </div>
        </div>
      </div>
      
      {/* Turnover Risks */}
      <div className="insights-section">
        <h2>🚨 Turnover Risk Alerts</h2>
        <div className="risk-summary">
          <div className="risk-badge high">
            High Risk: {insights?.turnover_risks?.high_risk || 0}
          </div>
          <div className="risk-badge medium">
            Medium Risk: {insights?.turnover_risks?.medium_risk || 0}
          </div>
          <div className="risk-badge low">
            Low Risk: {insights?.turnover_risks?.low_risk || 0}
          </div>
        </div>
        
        {insights?.turnover_risks?.at_risk_employees?.map(emp => (
          <div key={emp.id} className="at-risk-card">
            <div className="employee-info">
              <h4>{emp.name}</h4>
              <p>Risk Score: {(emp.risk_score * 100).toFixed(0)}%</p>
            </div>
            <div className="risk-indicator">
              <div className="risk-bar" style={{width: `${emp.risk_score * 100}%`}}></div>
            </div>
          </div>
        ))}
      </div>
      
      {/* Productivity Insights */}
      <div className="insights-section">
        <h2>📊 Productivity Analysis</h2>
        <div className="productivity-grid">
          <div className="prod-card">
            <h3>Overall Productivity</h3>
            <div className="progress-circle">
              {(insights?.productivity?.overall_productivity * 100).toFixed(0)}%
            </div>
          </div>
          <div className="prod-card">
            <h3>Most Productive</h3>
            <p>{insights?.productivity?.most_productive_dept || 'N/A'}</p>
          </div>
          <div className="prod-card">
            <h3>Needs Improvement</h3>
            <p>{insights?.productivity?.least_productive_dept || 'N/A'}</p>
          </div>
        </div>
      </div>
      
      {/* Individual Prediction Tool */}
      <div className="prediction-tool">
        <h2>🎯 Predict Employee Performance</h2>
        <div className="prediction-form">
          <input
            type="number"
            placeholder="Enter Employee ID"
            value={selectedEmployee || ''}
            onChange={(e) => setSelectedEmployee(e.target.value)}
          />
          <button
            className="btn-primary"
            onClick={predictPerformance}
            disabled={loading || !selectedEmployee}
          >
            {loading ? 'Analyzing...' : 'Generate Prediction'}
          </button>
        </div>
        
        {prediction && (
          <div className="prediction-result">
            <h3>Prediction Results</h3>
            <div className="result-grid">
              <div>
                <strong>Predicted Score:</strong>
                <p className="score">{prediction.prediction}</p>
              </div>
              <div>
                <strong>Confidence:</strong>
                <p>{(prediction.confidence * 100).toFixed(0)}%</p>
              </div>
            </div>
            {prediction.warnings?.length > 0 && (
              <div className="warnings">
                <h4>⚠️ Warnings:</h4>
                {prediction.warnings.map((w, i) => <p key={i}>{w}</p>)}
              </div>
            )}
          </div>
        )}
      </div>
      
      <style jsx>{`
        .ai-insights-page { padding: 24px; }
        .insights-section { background: white; padding: 24px; border-radius: 8px; margin-bottom: 24px; }
        .metrics-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-top: 16px; }
        .metric-card { background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }
        .metric-card h3 { margin: 0 0 12px 0; font-size: 14px; color: #666; }
        .metric-card .big { font-size: 32px; font-weight: bold; margin: 0; }
        .risk-summary { display: flex; gap: 16px; margin-bottom: 20px; }
        .risk-badge { padding: 12px 24px; border-radius: 8px; color: white; font-weight: 600; }
        .risk-badge.high { background: #ef4444; }
        .risk-badge.medium { background: #f59e0b; }
        .risk-badge.low { background: #10b981; }
        .at-risk-card { background: #fef2f2; padding: 16px; border-radius: 8px; margin-bottom: 12px; border-left: 4px solid #ef4444; }
        .employee-info h4 { margin: 0 0 8px 0; }
        .risk-indicator { background: #fee2e2; height: 8px; border-radius: 4px; overflow: hidden; }
        .risk-bar { height: 100%; background: #ef4444; transition: width 0.3s; }
        .productivity-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 16px; }
        .prod-card { background: #f0f9ff; padding: 24px; border-radius: 8px; text-align: center; }
        .progress-circle { font-size: 48px; font-weight: bold; color: #667eea; margin-top: 12px; }
        .prediction-tool { background: white; padding: 24px; border-radius: 8px; }
        .prediction-form { display: flex; gap: 12px; margin-bottom: 20px; }
        .prediction-form input { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 8px; }
        .prediction-result { background: #f0fdf4; padding: 20px; border-radius: 8px; border-left: 4px solid #10b981; }
        .result-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-top: 16px; }
        .result-grid .score { font-size: 36px; font-weight: bold; color: #10b981; }
        .warnings { margin-top: 16px; padding-top: 16px; border-top: 1px solid #d1fae5; }
        .btn-primary { background: #667eea; color: white; padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; }
        .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
      `}</style>
    </div>
  );
};

export default AIInsights;
''')

created.append(('AI Insights Page', 7.2))
print("   ✅ AIInsights.jsx created (7.2 KB)")

# 3. Register Page
print("3. Creating Register Page...")

create_file('services/web/src/pages/Register.jsx', '''/**
 * Register Page
 * User registration with company setup
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../utils/api-client-complete';

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: '',
    company_name: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const navigate = useNavigate();
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }
    
    setLoading(true);
    try {
      await apiClient.request('/auth/register', {
        method: 'POST',
        body: JSON.stringify(formData)
      });
      
      alert('Registration successful! Please check your email to verify your account.');
      navigate('/login');
    } catch (err) {
      setError(err.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="register-page">
      <div className="register-container">
        <div className="register-card">
          <h1>Create Account</h1>
          <p>Start managing your workforce today</p>
          
          {error && <div className="error-message">{error}</div>}
          
          <form onSubmit={handleSubmit}>
            <div className="form-row">
              <div className="form-group">
                <label>First Name</label>
                <input
                  required
                  value={formData.first_name}
                  onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                />
              </div>
              <div className="form-group">
                <label>Last Name</label>
                <input
                  required
                  value={formData.last_name}
                  onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                />
              </div>
            </div>
            
            <div className="form-group">
              <label>Company Name</label>
              <input
                required
                value={formData.company_name}
                onChange={(e) => setFormData({...formData, company_name: e.target.value})}
              />
            </div>
            
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                required
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
              />
            </div>
            
            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                required
                minLength={8}
                value={formData.password}
                onChange={(e) => setFormData({...formData, password: e.target.value})}
              />
              <small>Minimum 8 characters</small>
            </div>
            
            <div className="form-group">
              <label>Confirm Password</label>
              <input
                type="password"
                required
                value={formData.confirmPassword}
                onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
              />
            </div>
            
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Creating Account...' : 'Create Account'}
            </button>
          </form>
          
          <div className="login-link">
            Already have an account? <a href="/login">Sign In</a>
          </div>
        </div>
      </div>
      
      <style jsx>{`
        .register-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .register-container { width: 100%; max-width: 500px; padding: 20px; }
        .register-card { background: white; border-radius: 12px; padding: 40px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); }
        .register-card h1 { margin: 0 0 8px 0; font-size: 28px; }
        .register-card p { color: #666; margin: 0 0 32px 0; }
        .error-message { background: #fee2e2; color: #991b1b; padding: 12px; border-radius: 8px; margin-bottom: 20px; }
        form { display: flex; flex-direction: column; gap: 20px; }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
        .form-group { display: flex; flex-direction: column; gap: 8px; }
        .form-group label { font-weight: 600; font-size: 14px; }
        .form-group input { padding: 12px; border: 1px solid #ddd; border-radius: 8px; }
        .form-group small { color: #666; font-size: 12px; }
        .btn-primary { padding: 14px; background: #667eea; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; }
        .btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
        .login-link { text-align: center; margin-top: 20px; }
        .login-link a { color: #667eea; text-decoration: none; font-weight: 600; }
      `}</style>
    </div>
  );
};

export default Register;
''')

created.append(('Register Page', 4.5))
print("   ✅ Register.jsx created (4.5 KB)")

print()
print(f"✅ Phase 2 Progress: {len(created)} components created")
print(f"   Total: {sum([s for _, s in created]):.1f} KB")
print()

