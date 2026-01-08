/**
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
