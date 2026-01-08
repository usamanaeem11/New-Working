/**
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
