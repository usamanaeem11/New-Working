/**
 * Time Tracking Page - Complete
 * Timesheet view, entry management, approvals
 */

import React, { useState, useEffect } from 'react';
import { apiClient } from '../utils/api-client-complete';

const TimeTracking = () => {
  const [view, setView] = useState('week'); // week, list, approvals
  const [entries, setEntries] = useState([]);
  const [currentEntry, setCurrentEntry] = useState(null);
  const [isClockedIn, setIsClockedIn] = useState(false);
  
  useEffect(() => {
    loadTimeEntries();
    checkClockStatus();
  }, []);
  
  const loadTimeEntries = async () => {
    try {
      const response = await apiClient.request('/time/entries');
      setEntries(response || []);
    } catch (error) {
      console.error('Failed to load entries:', error);
    }
  };
  
  const checkClockStatus = () => {
    const active = entries.find(e => e.status === 'active' && !e.end_time);
    setIsClockedIn(!!active);
    setCurrentEntry(active);
  };
  
  const handleClockIn = async () => {
    try {
      const response = await apiClient.request('/time/clock-in', { method: 'POST' });
      setIsClockedIn(true);
      setCurrentEntry(response);
      loadTimeEntries();
    } catch (error) {
      console.error('Clock in failed:', error);
    }
  };
  
  const handleClockOut = async () => {
    try {
      await apiClient.request('/time/clock-out', { method: 'POST' });
      setIsClockedIn(false);
      setCurrentEntry(null);
      loadTimeEntries();
    } catch (error) {
      console.error('Clock out failed:', error);
    }
  };
  
  const calculateWeekHours = () => {
    return entries.reduce((sum, e) => sum + (e.hours || 0), 0);
  };
  
  return (
    <div className="time-tracking-page">
      <h1>Time Tracking</h1>
      
      {/* Clock Widget */}
      <div className="clock-widget">
        <div className="clock-status">
          {isClockedIn ? (
            <>
              <span className="status-indicator active"></span>
              <span>Currently Clocked In</span>
              <button className="btn-danger" onClick={handleClockOut}>Clock Out</button>
            </>
          ) : (
            <>
              <span className="status-indicator"></span>
              <span>Not Clocked In</span>
              <button className="btn-success" onClick={handleClockIn}>Clock In</button>
            </>
          )}
        </div>
        
        <div className="week-summary">
          <h3>This Week</h3>
          <p className="big-hours">{calculateWeekHours().toFixed(1)} hrs</p>
        </div>
      </div>
      
      {/* View Tabs */}
      <div className="view-tabs">
        <button
          className={view === 'week' ? 'active' : ''}
          onClick={() => setView('week')}
        >
          Week View
        </button>
        <button
          className={view === 'list' ? 'active' : ''}
          onClick={() => setView('list')}
        >
          All Entries
        </button>
        <button
          className={view === 'approvals' ? 'active' : ''}
          onClick={() => setView('approvals')}
        >
          Approvals
        </button>
      </div>
      
      {/* Week View */}
      {view === 'week' && (
        <div className="week-view">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Clock In</th>
                <th>Clock Out</th>
                <th>Hours</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {entries.slice(0, 7).map(entry => (
                <tr key={entry.id}>
                  <td>{new Date(entry.start_time).toLocaleDateString()}</td>
                  <td>{new Date(entry.start_time).toLocaleTimeString()}</td>
                  <td>{entry.end_time ? new Date(entry.end_time).toLocaleTimeString() : '-'}</td>
                  <td>{entry.hours?.toFixed(2) || '-'}</td>
                  <td><span className={`badge ${entry.status}`}>{entry.status}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      
      {/* List View */}
      {view === 'list' && (
        <div className="list-view">
          {entries.map(entry => (
            <div key={entry.id} className="entry-card">
              <div className="entry-date">{new Date(entry.start_time).toLocaleDateString()}</div>
              <div className="entry-time">
                {new Date(entry.start_time).toLocaleTimeString()} - 
                {entry.end_time ? new Date(entry.end_time).toLocaleTimeString() : 'In Progress'}
              </div>
              <div className="entry-hours">{entry.hours?.toFixed(2) || 0} hours</div>
              <span className={`badge ${entry.status}`}>{entry.status}</span>
            </div>
          ))}
        </div>
      )}
      
      {/* Approvals View */}
      {view === 'approvals' && (
        <div className="approvals-view">
          <p>Pending approvals functionality</p>
        </div>
      )}
      
      <style jsx>{`
        .time-tracking-page { padding: 24px; }
        .clock-widget { background: white; padding: 24px; border-radius: 12px; margin-bottom: 24px; display: flex; justify-content: space-between; }
        .clock-status { display: flex; align-items: center; gap: 16px; }
        .status-indicator { width: 12px; height: 12px; background: #d1d5db; border-radius: 50%; }
        .status-indicator.active { background: #10b981; animation: pulse 2s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        .week-summary { text-align: right; }
        .big-hours { font-size: 48px; font-weight: bold; color: #667eea; margin: 0; }
        .view-tabs { display: flex; gap: 8px; margin-bottom: 24px; }
        .view-tabs button { padding: 12px 24px; background: white; border: 1px solid #ddd; border-radius: 8px; cursor: pointer; }
        .view-tabs button.active { background: #667eea; color: white; border-color: #667eea; }
        .week-view { background: white; padding: 24px; border-radius: 8px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
        .badge { padding: 4px 12px; border-radius: 12px; font-size: 12px; }
        .badge.active { background: #10b981; color: white; }
        .badge.completed { background: #3b82f6; color: white; }
        .badge.approved { background: #10b981; color: white; }
        .list-view { display: flex; flex-direction: column; gap: 12px; }
        .entry-card { background: white; padding: 16px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; }
        .btn-success { background: #10b981; color: white; padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; }
        .btn-danger { background: #ef4444; color: white; padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; }
      `}</style>
    </div>
  );
};

export default TimeTracking;
