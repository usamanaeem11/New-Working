/**
 * Reports Page
 * Generate and view reports (attendance, hours, payroll, performance)
 */

import React, { useState } from 'react';
import { apiClient } from '../utils/api-client-complete';

const Reports = () => {
  const [reportType, setReportType] = useState('attendance');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [loading, setLoading] = useState(false);
  const [reportData, setReportData] = useState(null);
  
  const handleGenerateReport = async () => {
    setLoading(true);
    try {
      const response = await apiClient.request('/reports/generate', {
        method: 'POST',
        body: JSON.stringify({
          report_type: reportType,
          start_date: startDate,
          end_date: endDate,
          format: 'json'
        })
      });
      setReportData(response);
    } catch (error) {
      console.error('Failed to generate report:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleExport = (format) => {
    // Export report in specified format
    console.log(`Exporting as ${format}`);
  };
  
  return (
    <div className="reports-page">
      <div className="page-header">
        <h1>Reports & Analytics</h1>
      </div>
      
      <div className="report-generator">
        <h2>Generate Report</h2>
        <div className="form-grid">
          <div className="form-group">
            <label>Report Type</label>
            <select value={reportType} onChange={(e) => setReportType(e.target.value)}>
              <option value="attendance">Attendance Report</option>
              <option value="hours">Hours Worked</option>
              <option value="payroll">Payroll Summary</option>
              <option value="performance">Performance Report</option>
            </select>
          </div>
          
          <div className="form-group">
            <label>Start Date</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
          </div>
          
          <div className="form-group">
            <label>End Date</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />
          </div>
        </div>
        
        <button
          className="btn-primary"
          onClick={handleGenerateReport}
          disabled={loading || !startDate || !endDate}
        >
          {loading ? 'Generating...' : 'Generate Report'}
        </button>
      </div>
      
      {reportData && (
        <div className="report-results">
          <div className="results-header">
            <h2>{reportType.charAt(0).toUpperCase() + reportType.slice(1)} Report</h2>
            <div className="export-buttons">
              <button onClick={() => handleExport('pdf')}>Export PDF</button>
              <button onClick={() => handleExport('csv')}>Export CSV</button>
              <button onClick={() => handleExport('excel')}>Export Excel</button>
            </div>
          </div>
          
          <div className="report-data">
            {reportType === 'attendance' && (
              <div className="metrics-grid">
                <div className="metric">
                  <h3>Total Employees</h3>
                  <p className="big">{reportData.data?.total_employees || 0}</p>
                </div>
                <div className="metric">
                  <h3>Attendance Rate</h3>
                  <p className="big">{(reportData.data?.attendance_rate * 100).toFixed(1)}%</p>
                </div>
                <div className="metric">
                  <h3>Absences</h3>
                  <p className="big">{reportData.data?.absences || 0}</p>
                </div>
                <div className="metric">
                  <h3>Late Arrivals</h3>
                  <p className="big">{reportData.data?.late_arrivals || 0}</p>
                </div>
              </div>
            )}
            
            {reportType === 'hours' && (
              <div className="metrics-grid">
                <div className="metric">
                  <h3>Total Hours</h3>
                  <p className="big">{reportData.data?.total_hours || 0}</p>
                </div>
                <div className="metric">
                  <h3>Regular Hours</h3>
                  <p className="big">{reportData.data?.regular_hours || 0}</p>
                </div>
                <div className="metric">
                  <h3>Overtime</h3>
                  <p className="big">{reportData.data?.overtime_hours || 0}</p>
                </div>
                <div className="metric">
                  <h3>Avg per Employee</h3>
                  <p className="big">{reportData.data?.average_per_employee?.toFixed(1) || 0}</p>
                </div>
              </div>
            )}
            
            {reportType === 'payroll' && (
              <div className="metrics-grid">
                <div className="metric">
                  <h3>Total Paid</h3>
                  <p className="big">${reportData.data?.total_paid?.toLocaleString() || 0}</p>
                </div>
                <div className="metric">
                  <h3>Average Salary</h3>
                  <p className="big">${reportData.data?.average_salary?.toLocaleString() || 0}</p>
                </div>
                <div className="metric">
                  <h3>Highest Paid</h3>
                  <p className="big">${reportData.data?.highest_paid?.toLocaleString() || 0}</p>
                </div>
                <div className="metric">
                  <h3>Lowest Paid</h3>
                  <p className="big">${reportData.data?.lowest_paid?.toLocaleString() || 0}</p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
      
      <style jsx>{`
        .reports-page { padding: 24px; }
        .page-header { margin-bottom: 24px; }
        .report-generator { background: white; padding: 24px; border-radius: 8px; margin-bottom: 24px; }
        .form-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px; }
        .form-group { display: flex; flex-direction: column; gap: 8px; }
        .form-group label { font-weight: 600; }
        .form-group select, .form-group input { padding: 12px; border: 1px solid #ddd; border-radius: 8px; }
        .report-results { background: white; padding: 24px; border-radius: 8px; }
        .results-header { display: flex; justify-content: space-between; margin-bottom: 24px; }
        .export-buttons { display: flex; gap: 8px; }
        .export-buttons button { padding: 8px 16px; background: #10b981; color: white; border: none; border-radius: 6px; cursor: pointer; }
        .metrics-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
        .metric { background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }
        .metric h3 { margin: 0 0 12px 0; color: #666; font-size: 14px; }
        .metric p.big { font-size: 32px; font-weight: bold; margin: 0; }
        .btn-primary { background: #667eea; color: white; padding: 12px 32px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; }
        .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
      `}</style>
    </div>
  );
};

export default Reports;
