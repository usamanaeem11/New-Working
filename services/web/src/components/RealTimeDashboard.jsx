/**
 * Real-time Dashboard Component
 * Shows live updates via WebSocket
 */

import React, { useEffect, useState } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { apiClient } from '../utils/api-client-complete';

const RealTimeDashboard = ({ token }) => {
  const { isConnected, onlineUsers, notifications } = useWebSocket(token);
  const [liveMetrics, setLiveMetrics] = useState({
    clocked_in_now: 0,
    total_hours_today: 0
  });
  
  useEffect(() => {
    loadMetrics();
    
    // Refresh metrics every minute
    const interval = setInterval(loadMetrics, 60000);
    return () => clearInterval(interval);
  }, []);
  
  // Update metrics when notifications come in
  useEffect(() => {
    const timeNotifications = notifications.filter(n => n.type === 'time_entry');
    if (timeNotifications.length > 0) {
      loadMetrics();
    }
  }, [notifications]);
  
  const loadMetrics = async () => {
    try {
      const response = await apiClient.request('/dashboard/metrics');
      setLiveMetrics(response);
    } catch (error) {
      console.error('Failed to load metrics:', error);
    }
  };
  
  return (
    <div className="realtime-dashboard">
      <div className="connection-status">
        <span className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`}></span>
        <span>{isConnected ? 'Live' : 'Connecting...'}</span>
        <span className="online-count">{onlineUsers.length} online</span>
      </div>
      
      <div className="live-metrics">
        <div className="metric-card">
          <h3>Clocked In Now</h3>
          <p className="big-number">{liveMetrics.clocked_in_now}</p>
          <span className="live-badge">🔴 LIVE</span>
        </div>
        
        <div className="metric-card">
          <h3>Hours Today</h3>
          <p className="big-number">{liveMetrics.total_hours_today.toFixed(1)}</p>
          <span className="live-badge">🔴 LIVE</span>
        </div>
      </div>
      
      <div className="live-activity">
        <h3>Live Activity</h3>
        <div className="activity-feed">
          {notifications.slice(0, 10).map((notif, index) => (
            <div key={index} className="activity-item">
              {notif.type === 'time_entry' && (
                <>
                  <span className="activity-icon">⏰</span>
                  <span>
                    Employee {notif.employee_id} {notif.action === 'clock_in' ? 'clocked in' : 'clocked out'}
                  </span>
                  <span className="time-ago">{getTimeAgo(notif.timestamp)}</span>
                </>
              )}
              {notif.type === 'payroll' && (
                <>
                  <span className="activity-icon">💰</span>
                  <span>Payroll run completed</span>
                  <span className="time-ago">{getTimeAgo(notif.timestamp)}</span>
                </>
              )}
              {notif.type === 'employee' && (
                <>
                  <span className="activity-icon">👤</span>
                  <span>Employee {notif.action}</span>
                  <span className="time-ago">{getTimeAgo(notif.timestamp)}</span>
                </>
              )}
            </div>
          ))}
          {notifications.length === 0 && (
            <p className="no-activity">No recent activity</p>
          )}
        </div>
      </div>
      
      <style jsx>{`
        .realtime-dashboard { padding: 24px; }
        .connection-status { display: flex; align-items: center; gap: 12px; margin-bottom: 24px; padding: 12px; background: #f0f9ff; border-radius: 8px; }
        .status-dot { width: 12px; height: 12px; border-radius: 50%; }
        .status-dot.connected { background: #10b981; animation: pulse 2s infinite; }
        .status-dot.disconnected { background: #ef4444; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        .online-count { margin-left: auto; color: #666; font-size: 14px; }
        .live-metrics { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-bottom: 24px; }
        .metric-card { background: white; padding: 24px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); position: relative; }
        .metric-card h3 { margin: 0 0 12px 0; font-size: 14px; color: #666; }
        .big-number { font-size: 48px; font-weight: bold; margin: 0; color: #667eea; }
        .live-badge { position: absolute; top: 12px; right: 12px; background: #fef2f2; color: #ef4444; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }
        .live-activity { background: white; padding: 24px; border-radius: 8px; }
        .activity-feed { display: flex; flex-direction: column; gap: 12px; }
        .activity-item { display: flex; align-items: center; gap: 12px; padding: 12px; background: #f9fafb; border-radius: 6px; }
        .activity-icon { font-size: 20px; }
        .time-ago { margin-left: auto; font-size: 12px; color: #999; }
        .no-activity { text-align: center; color: #999; padding: 24px; }
      `}</style>
    </div>
  );
};

const getTimeAgo = (timestamp) => {
  const seconds = Math.floor((new Date() - new Date(timestamp)) / 1000);
  if (seconds < 60) return 'just now';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  return `${hours}h ago`;
};

export default RealTimeDashboard;
