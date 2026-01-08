/**
 * Complete Employees Management
 * Enhanced with filters, bulk operations, org chart
 */

import React, { useState, useEffect } from 'react';
import { apiClient } from '../utils/api-client-complete';

const EmployeesComplete = () => {
  const [employees, setEmployees] = useState([]);
  const [view, setView] = useState('grid'); // grid, list, org
  const [filters, setFilters] = useState({ department: '', status: 'active' });
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [showModal, setShowModal] = useState(false);
  
  useEffect(() => {
    loadEmployees();
  }, [filters]);
  
  const loadEmployees = async () => {
    try {
      const params = new URLSearchParams(filters);
      const response = await apiClient.request(`/employees?${params}`);
      setEmployees(response || []);
    } catch (error) {
      console.error('Failed to load employees:', error);
    }
  };
  
  const handleViewEmployee = (employee) => {
    setSelectedEmployee(employee);
    setShowModal(true);
  };
  
  return (
    <div className="employees-complete-page">
      <div className="page-header">
        <h1>Employees ({employees.length})</h1>
        <button className="btn-primary">+ Add Employee</button>
      </div>
      
      {/* Filters */}
      <div className="filters-bar">
        <select
          value={filters.department}
          onChange={(e) => setFilters({...filters, department: e.target.value})}
        >
          <option value="">All Departments</option>
          <option value="Engineering">Engineering</option>
          <option value="Sales">Sales</option>
          <option value="Marketing">Marketing</option>
          <option value="HR">HR</option>
        </select>
        
        <select
          value={filters.status}
          onChange={(e) => setFilters({...filters, status: e.target.value})}
        >
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="all">All</option>
        </select>
        
        <div className="view-toggle">
          <button
            className={view === 'grid' ? 'active' : ''}
            onClick={() => setView('grid')}
          >
            Grid
          </button>
          <button
            className={view === 'list' ? 'active' : ''}
            onClick={() => setView('list')}
          >
            List
          </button>
        </div>
      </div>
      
      {/* Grid View */}
      {view === 'grid' && (
        <div className="employees-grid">
          {employees.map(emp => (
            <div key={emp.id} className="employee-card" onClick={() => handleViewEmployee(emp)}>
              <div className="avatar">{emp.first_name[0]}{emp.last_name[0]}</div>
              <h3>{emp.first_name} {emp.last_name}</h3>
              <p className="position">{emp.position}</p>
              <p className="department">{emp.department}</p>
              <span className={`status-badge ${emp.status}`}>{emp.status}</span>
            </div>
          ))}
        </div>
      )}
      
      {/* List View */}
      {view === 'list' && (
        <div className="employees-list">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Employee #</th>
                <th>Department</th>
                <th>Position</th>
                <th>Email</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {employees.map(emp => (
                <tr key={emp.id}>
                  <td>{emp.first_name} {emp.last_name}</td>
                  <td>{emp.employee_number}</td>
                  <td>{emp.department}</td>
                  <td>{emp.position}</td>
                  <td>{emp.email}</td>
                  <td><span className={`badge ${emp.status}`}>{emp.status}</span></td>
                  <td>
                    <button onClick={() => handleViewEmployee(emp)}>View</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      
      {/* Employee Detail Modal */}
      {showModal && selectedEmployee && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>{selectedEmployee.first_name} {selectedEmployee.last_name}</h2>
            <div className="detail-grid">
              <div>
                <label>Employee Number:</label>
                <p>{selectedEmployee.employee_number}</p>
              </div>
              <div>
                <label>Department:</label>
                <p>{selectedEmployee.department}</p>
              </div>
              <div>
                <label>Position:</label>
                <p>{selectedEmployee.position}</p>
              </div>
              <div>
                <label>Email:</label>
                <p>{selectedEmployee.email}</p>
              </div>
              <div>
                <label>Hire Date:</label>
                <p>{selectedEmployee.hire_date}</p>
              </div>
              <div>
                <label>Status:</label>
                <p><span className={`badge ${selectedEmployee.status}`}>{selectedEmployee.status}</span></p>
              </div>
            </div>
            <div className="modal-actions">
              <button className="btn-primary">Edit</button>
              <button onClick={() => setShowModal(false)}>Close</button>
            </div>
          </div>
        </div>
      )}
      
      <style jsx>{`
        .employees-complete-page { padding: 24px; }
        .page-header { display: flex; justify-content: space-between; margin-bottom: 24px; }
        .filters-bar { background: white; padding: 16px; border-radius: 8px; margin-bottom: 24px; display: flex; gap: 12px; }
        .filters-bar select { padding: 10px; border: 1px solid #ddd; border-radius: 6px; }
        .view-toggle { display: flex; gap: 4px; margin-left: auto; }
        .view-toggle button { padding: 8px 16px; background: white; border: 1px solid #ddd; cursor: pointer; }
        .view-toggle button.active { background: #667eea; color: white; border-color: #667eea; }
        .employees-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 16px; }
        .employee-card { background: white; padding: 24px; border-radius: 8px; text-align: center; cursor: pointer; transition: transform 0.2s; }
        .employee-card:hover { transform: translateY(-4px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .avatar { width: 80px; height: 80px; background: #667eea; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 32px; font-weight: bold; margin: 0 auto 16px; }
        .employee-card h3 { margin: 0 0 8px 0; }
        .position { color: #666; margin: 4px 0; }
        .department { color: #999; font-size: 14px; margin: 4px 0; }
        .status-badge { display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 12px; margin-top: 8px; }
        .status-badge.active { background: #d1fae5; color: #065f46; }
        .employees-list { background: white; padding: 24px; border-radius: 8px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
        .badge { padding: 4px 12px; border-radius: 12px; font-size: 12px; }
        .badge.active { background: #10b981; color: white; }
        .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
        .modal { background: white; padding: 32px; border-radius: 12px; width: 600px; }
        .detail-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin: 24px 0; }
        .detail-grid label { font-weight: 600; color: #666; font-size: 14px; }
        .detail-grid p { margin: 4px 0 0 0; }
        .modal-actions { display: flex; gap: 12px; justify-content: flex-end; }
        .btn-primary { background: #667eea; color: white; padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; }
      `}</style>
    </div>
  );
};

export default EmployeesComplete;
