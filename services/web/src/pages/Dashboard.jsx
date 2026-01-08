/**
 * Main Dashboard Page
 * Real-time employee metrics and time tracking
 */

import React from 'react';
import { useAuth } from '../hooks/useAuth';
import { useEmployees } from '../hooks/useEmployees';
import { useTimeTracking } from '../hooks/useTimeTracking';

const Dashboard = () => {
  const { user } = useAuth();
  const { employees, loading: employeesLoading } = useEmployees();
  const { activeEntry, clockIn, clockOut, loading: timeLoading } = useTimeTracking();

  const handleClockIn = async () => {
    try {
      await clockIn();
      alert('Clocked in successfully!');
    } catch (error) {
      alert('Failed to clock in: ' + error.message);
    }
  };

  const handleClockOut = async () => {
    try {
      await clockOut();
      alert('Clocked out successfully!');
    } catch (error) {
      alert('Failed to clock out: ' + error.message);
    }
  };

  // Calculate metrics from real data
  const activeEmployees = employees.filter(e => e.status === 'active').length;
  const clockedIn = activeEntry ? 1 : 0;
  const todayHours = activeEntry ? 
    ((Date.now() - new Date(activeEntry.start_time)) / (1000 * 60 * 60)).toFixed(1) : 
    0;

  if (employeesLoading) {
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
        <h1>Welcome back, {user?.first_name || 'User'}!</h1>
        <p>Here's what's happening today</p>
      </header>

      {/* Metrics Cards */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon">👥</div>
          <div className="metric-content">
            <h3>Active Employees</h3>
            <p className="metric-value">{activeEmployees}</p>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">⏰</div>
          <div className="metric-content">
            <h3>Clocked In</h3>
            <p className="metric-value">{clockedIn}</p>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">📊</div>
          <div className="metric-content">
            <h3>Today's Hours</h3>
            <p className="metric-value">{todayHours}h</p>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">💰</div>
          <div className="metric-content">
            <h3>Total Payroll</h3>
            <p className="metric-value">$0</p>
          </div>
        </div>
      </div>

      {/* Time Tracking Section */}
      <div className="time-tracking-section">
        <h2>Time Tracking</h2>
        
        {activeEntry ? (
          <div className="active-time-card">
            <div className="timer">
              <span className="timer-label">Currently Working</span>
              <span className="timer-value">{todayHours} hours</span>
            </div>
            <button 
              className="btn-primary btn-clock-out" 
              onClick={handleClockOut}
              disabled={timeLoading}
            >
              {timeLoading ? 'Processing...' : 'Clock Out'}
            </button>
          </div>
        ) : (
          <div className="inactive-time-card">
            <p>You're not currently clocked in</p>
            <button 
              className="btn-primary btn-clock-in" 
              onClick={handleClockIn}
              disabled={timeLoading}
            >
              {timeLoading ? 'Processing...' : 'Clock In'}
            </button>
          </div>
        )}
      </div>

      {/* Employees List */}
      <div className="employees-section">
        <h2>Team Members</h2>
        
        {employees.length === 0 ? (
          <p>No employees found</p>
        ) : (
          <div className="employees-grid">
            {employees.slice(0, 6).map(employee => (
              <div key={employee.id} className="employee-card">
                <div className="employee-avatar">
                  {employee.first_name[0]}{employee.last_name[0]}
                </div>
                <div className="employee-info">
                  <h3>{employee.first_name} {employee.last_name}</h3>
                  <p>{employee.position}</p>
                  <span className={`status-badge status-${employee.status}`}>
                    {employee.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <style jsx>{`
        .dashboard {
          padding: 24px;
          max-width: 1400px;
          margin: 0 auto;
        }

        .dashboard-header {
          margin-bottom: 32px;
        }

        .dashboard-header h1 {
          font-size: 32px;
          font-weight: 600;
          margin-bottom: 8px;
        }

        .metrics-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 20px;
          margin-bottom: 32px;
        }

        .metric-card {
          background: white;
          border-radius: 12px;
          padding: 24px;
          display: flex;
          align-items: center;
          gap: 16px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .metric-icon {
          font-size: 40px;
        }

        .metric-value {
          font-size: 32px;
          font-weight: 600;
          color: #2563eb;
        }

        .time-tracking-section,
        .employees-section {
          background: white;
          border-radius: 12px;
          padding: 24px;
          margin-bottom: 24px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .active-time-card,
        .inactive-time-card {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 24px;
          background: #f8fafc;
          border-radius: 8px;
          margin-top: 16px;
        }

        .timer-value {
          font-size: 24px;
          font-weight: 600;
          color: #10b981;
        }

        .btn-primary {
          padding: 12px 24px;
          border: none;
          border-radius: 8px;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-clock-in {
          background: #10b981;
          color: white;
        }

        .btn-clock-out {
          background: #ef4444;
          color: white;
        }

        .employees-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 16px;
          margin-top: 16px;
        }

        .employee-card {
          padding: 16px;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
        }

        .employee-avatar {
          width: 48px;
          height: 48px;
          border-radius: 50%;
          background: #2563eb;
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 600;
          margin-bottom: 12px;
        }

        .status-badge {
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: 600;
        }

        .status-active {
          background: #dcfce7;
          color: #166534;
        }

        .dashboard-loading {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 400px;
        }

        .spinner {
          width: 40px;
          height: 40px;
          border: 4px solid #f3f4f6;
          border-top-color: #2563eb;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default Dashboard;
