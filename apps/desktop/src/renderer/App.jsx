/**
 * Desktop App Root
 * Navigation and routing
 */

import React from 'react';
import { HashRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

// Import all components
import Login from './components/Login';
import Dashboard from './components/Dashboard-complete';
import EmployeesList from './components/EmployeesList';
import TimeTracking from './components/TimeTracking';
import PayrollManager from './components/PayrollManager';
import ReportsManager from './components/ReportsManager';
import SettingsPanel from './components/SettingsPanel';
import AIDashboard from './components/AIDashboard';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/employees" element={<EmployeesList />} />
        <Route path="/time" element={<TimeTracking />} />
        <Route path="/payroll" element={<PayrollManager />} />
        <Route path="/reports" element={<ReportsManager />} />
        <Route path="/settings" element={<SettingsPanel />} />
        <Route path="/ai" element={<AIDashboard />} />
        <Route path="/" element={<Navigate to="/login" />} />
      </Routes>
    </Router>
  );
};

export default App;
