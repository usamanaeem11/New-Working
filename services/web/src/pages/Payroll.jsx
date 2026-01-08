/**
 * Payroll Page
 * Run payroll, view history, export data
 */

import React, { useState, useEffect } from 'react';
import { apiClient } from '../utils/api-client-complete';

const Payroll = () => {
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showRunModal, setShowRunModal] = useState(false);
  const [payrollData, setPayrollData] = useState({
    pay_period_start: '',
    pay_period_end: '',
    pay_date: ''
  });
  
  useEffect(() => {
    loadPayrollRuns();
  }, []);
  
  const loadPayrollRuns = async () => {
    setLoading(true);
    try {
      const response = await apiClient.request('/payroll/runs');
      setRuns(response.data || []);
    } catch (error) {
      console.error('Failed to load payroll runs:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleRunPayroll = async () => {
    setLoading(true);
    try {
      await apiClient.request('/payroll/run', {
        method: 'POST',
        body: JSON.stringify(payrollData)
      });
      setShowRunModal(false);
      loadPayrollRuns();
    } catch (error) {
      console.error('Failed to run payroll:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="payroll-page">
      <div className="page-header">
        <h1>Payroll Management</h1>
        <button className="btn-primary" onClick={() => setShowRunModal(true)}>
          Run Payroll
        </button>
      </div>
      
      <div className="payroll-summary">
        <div className="summary-card">
          <h3>Total Runs</h3>
          <p className="big-number">{runs.length}</p>
        </div>
        <div className="summary-card">
          <h3>Last Run</h3>
          <p>{runs[0]?.pay_date || 'N/A'}</p>
        </div>
        <div className="summary-card">
          <h3>Total Paid (Last)</h3>
          <p className="big-number">${runs[0]?.total_amount?.toLocaleString() || '0'}</p>
        </div>
      </div>
      
      <div className="payroll-history">
        <h2>Payroll History</h2>
        {loading ? (
          <div className="loading">Loading...</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Pay Period</th>
                <th>Pay Date</th>
                <th>Employees</th>
                <th>Total Amount</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {runs.map(run => (
                <tr key={run.id}>
                  <td>{run.pay_period_start} - {run.pay_period_end}</td>
                  <td>{run.pay_date}</td>
                  <td>{run.employee_count}</td>
                  <td>${run.total_amount.toLocaleString()}</td>
                  <td><span className="status-badge">{run.status}</span></td>
                  <td>
                    <button className="btn-small">View</button>
                    <button className="btn-small">Export</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
      
      {showRunModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h2>Run Payroll</h2>
            <form onSubmit={(e) => { e.preventDefault(); handleRunPayroll(); }}>
              <label>Pay Period Start</label>
              <input
                type="date"
                value={payrollData.pay_period_start}
                onChange={(e) => setPayrollData({...payrollData, pay_period_start: e.target.value})}
                required
              />
              <label>Pay Period End</label>
              <input
                type="date"
                value={payrollData.pay_period_end}
                onChange={(e) => setPayrollData({...payrollData, pay_period_end: e.target.value})}
                required
              />
              <label>Pay Date</label>
              <input
                type="date"
                value={payrollData.pay_date}
                onChange={(e) => setPayrollData({...payrollData, pay_date: e.target.value})}
                required
              />
              <div className="modal-actions">
                <button type="submit" className="btn-primary" disabled={loading}>
                  {loading ? 'Processing...' : 'Run Payroll'}
                </button>
                <button type="button" onClick={() => setShowRunModal(false)}>Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}
      
      <style jsx>{`
        .payroll-page { padding: 24px; }
        .page-header { display: flex; justify-content: space-between; margin-bottom: 24px; }
        .payroll-summary { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 32px; }
        .summary-card { background: white; padding: 24px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .big-number { font-size: 32px; font-weight: bold; margin: 8px 0 0 0; }
        .payroll-history { background: white; padding: 24px; border-radius: 8px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
        .status-badge { background: #10b981; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; }
        .btn-small { padding: 6px 12px; margin: 0 4px; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
        .modal { background: white; padding: 32px; border-radius: 12px; width: 500px; }
        .modal form { display: flex; flex-direction: column; gap: 16px; }
        .modal label { font-weight: 600; }
        .modal input { padding: 12px; border: 1px solid #ddd; border-radius: 8px; }
        .modal-actions { display: flex; gap: 12px; }
        .btn-primary { background: #667eea; color: white; padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; }
      `}</style>
    </div>
  );
};

export default Payroll;
