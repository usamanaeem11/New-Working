/**
 * Desktop Dashboard Component
 * Electron app main dashboard
 */

import React, { useState, useEffect } from 'react';
import { desktopAPI } from '../api';
import './Dashboard.css';

const Dashboard = () => {
  const [metrics, setMetrics] = useState({
    activeEmployees: 0,
    clockedIn: 0,
    todayHours: 0,
    weekHours: 0,
  });
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isClockedIn, setIsClockedIn] = useState(false);

  useEffect(() => {
    loadDashboard();
    
    // Refresh every minute
    const interval = setInterval(loadDashboard, 60000);
    return () => clearInterval(interval);
  }, []);

  const loadDashboard = async () => {
    try {
      const [dashboardResult, employeesResult] = await Promise.all([
        desktopAPI.getDashboardData(),
        desktopAPI.getEmployees(),
      ]);

      if (dashboardResult.success) {
        setMetrics(dashboardResult.data.metrics);
        setIsClockedIn(dashboardResult.data.is_clocked_in);
      }

      if (employeesResult.success) {
        setEmployees(employeesResult.data);
      }
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClockIn = async () => {
    const result = await desktopAPI.clockIn();
    if (result.success) {
      setIsClockedIn(true);
      loadDashboard();
    }
  };

  const handleClockOut = async () => {
    const result = await desktopAPI.clockOut();
    if (result.success) {
      setIsClockedIn(false);
      loadDashboard();
    }
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Dashboard</h1>
        <p className="date">
          {new Date().toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
          })}
        </p>
      </header>

      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon">👥</div>
          <div className="metric-content">
            <h3>Active Employees</h3>
            <p className="metric-value">{metrics.activeEmployees}</p>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">⏰</div>
          <div className="metric-content">
            <h3>Clocked In</h3>
            <p className="metric-value">{metrics.clockedIn}</p>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">📊</div>
          <div className="metric-content">
            <h3>Today's Hours</h3>
            <p className="metric-value">{metrics.todayHours}h</p>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">📅</div>
          <div className="metric-content">
            <h3>Week's Hours</h3>
            <p className="metric-value">{metrics.weekHours}h</p>
          </div>
        </div>
      </div>

      <div className="time-tracking-section">
        <h2>Time Tracking</h2>
        {isClockedIn ? (
          <div className="time-card clocked-in">
            <div className="status-indicator">
              <span className="status-dot"></span>
              <span>Currently Working</span>
            </div>
            <button className="btn btn-danger" onClick={handleClockOut}>
              Clock Out
            </button>
          </div>
        ) : (
          <div className="time-card clocked-out">
            <p>You're not currently clocked in</p>
            <button className="btn btn-primary" onClick={handleClockIn}>
              Clock In
            </button>
          </div>
        )}
      </div>

      <div className="employees-section">
        <h2>Team Members ({employees.length})</h2>
        <div className="employees-grid">
          {employees.slice(0, 8).map((employee) => (
            <div key={employee.id} className="employee-card">
              <div className="employee-avatar">
                {employee.first_name[0]}{employee.last_name[0]}
              </div>
              <div className="employee-info">
                <h4>{employee.first_name} {employee.last_name}</h4>
                <p>{employee.position}</p>
                <span className={`badge badge-${employee.status}`}>
                  {employee.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
