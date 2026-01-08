/**
 * Register Page
 * User registration with company setup
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../utils/api-client-complete';

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: '',
    company_name: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const navigate = useNavigate();
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }
    
    setLoading(true);
    try {
      await apiClient.request('/auth/register', {
        method: 'POST',
        body: JSON.stringify(formData)
      });
      
      alert('Registration successful! Please check your email to verify your account.');
      navigate('/login');
    } catch (err) {
      setError(err.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="register-page">
      <div className="register-container">
        <div className="register-card">
          <h1>Create Account</h1>
          <p>Start managing your workforce today</p>
          
          {error && <div className="error-message">{error}</div>}
          
          <form onSubmit={handleSubmit}>
            <div className="form-row">
              <div className="form-group">
                <label>First Name</label>
                <input
                  required
                  value={formData.first_name}
                  onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                />
              </div>
              <div className="form-group">
                <label>Last Name</label>
                <input
                  required
                  value={formData.last_name}
                  onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                />
              </div>
            </div>
            
            <div className="form-group">
              <label>Company Name</label>
              <input
                required
                value={formData.company_name}
                onChange={(e) => setFormData({...formData, company_name: e.target.value})}
              />
            </div>
            
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                required
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
              />
            </div>
            
            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                required
                minLength={8}
                value={formData.password}
                onChange={(e) => setFormData({...formData, password: e.target.value})}
              />
              <small>Minimum 8 characters</small>
            </div>
            
            <div className="form-group">
              <label>Confirm Password</label>
              <input
                type="password"
                required
                value={formData.confirmPassword}
                onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
              />
            </div>
            
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Creating Account...' : 'Create Account'}
            </button>
          </form>
          
          <div className="login-link">
            Already have an account? <a href="/login">Sign In</a>
          </div>
        </div>
      </div>
      
      <style jsx>{`
        .register-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .register-container { width: 100%; max-width: 500px; padding: 20px; }
        .register-card { background: white; border-radius: 12px; padding: 40px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); }
        .register-card h1 { margin: 0 0 8px 0; font-size: 28px; }
        .register-card p { color: #666; margin: 0 0 32px 0; }
        .error-message { background: #fee2e2; color: #991b1b; padding: 12px; border-radius: 8px; margin-bottom: 20px; }
        form { display: flex; flex-direction: column; gap: 20px; }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
        .form-group { display: flex; flex-direction: column; gap: 8px; }
        .form-group label { font-weight: 600; font-size: 14px; }
        .form-group input { padding: 12px; border: 1px solid #ddd; border-radius: 8px; }
        .form-group small { color: #666; font-size: 12px; }
        .btn-primary { padding: 14px; background: #667eea; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; }
        .btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
        .login-link { text-align: center; margin-top: 20px; }
        .login-link a { color: #667eea; text-decoration: none; font-weight: 600; }
      `}</style>
    </div>
  );
};

export default Register;
