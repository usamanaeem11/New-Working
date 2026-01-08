/**
 * Password Reset Page
 */

import React, { useState } from 'react';
import { apiClient } from '../utils/api-client-complete';

const PasswordReset = () => {
  const [step, setStep] = useState(1);
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  
  const handleSendCode = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await apiClient.request('/auth/password-reset/request', {
        method: 'POST',
        body: JSON.stringify({ email })
      });
      setMessage('Reset code sent to your email');
      setStep(2);
    } catch (error) {
      setMessage('Failed to send reset code');
    } finally {
      setLoading(false);
    }
  };
  
  const handleResetPassword = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await apiClient.request('/auth/password-reset/confirm', {
        method: 'POST',
        body: JSON.stringify({ email, code, new_password: newPassword })
      });
      setMessage('Password reset successful! You can now login.');
      setStep(3);
    } catch (error) {
      setMessage('Failed to reset password');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="password-reset-page">
      <div className="reset-card">
        <h1>Reset Password</h1>
        
        {message && <div className={step === 3 ? 'success-message' : 'info-message'}>{message}</div>}
        
        {step === 1 && (
          <form onSubmit={handleSendCode}>
            <p>Enter your email to receive a reset code</p>
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <button type="submit" disabled={loading}>
              {loading ? 'Sending...' : 'Send Reset Code'}
            </button>
          </form>
        )}
        
        {step === 2 && (
          <form onSubmit={handleResetPassword}>
            <p>Enter the code sent to your email and your new password</p>
            <input
              placeholder="Reset Code"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              required
            />
            <input
              type="password"
              placeholder="New Password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              minLength={8}
              required
            />
            <button type="submit" disabled={loading}>
              {loading ? 'Resetting...' : 'Reset Password'}
            </button>
          </form>
        )}
        
        {step === 3 && (
          <div className="success-section">
            <p>✅ Your password has been reset successfully!</p>
            <a href="/login" className="btn-primary">Go to Login</a>
          </div>
        )}
        
        <div className="back-link">
          <a href="/login">← Back to Login</a>
        </div>
      </div>
      
      <style jsx>{`
        .password-reset-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .reset-card { background: white; padding: 40px; border-radius: 12px; width: 400px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); }
        .reset-card h1 { margin: 0 0 24px 0; text-align: center; }
        .info-message, .success-message { padding: 12px; border-radius: 8px; margin-bottom: 20px; }
        .info-message { background: #dbeafe; color: #1e40af; }
        .success-message { background: #d1fae5; color: #065f46; }
        form { display: flex; flex-direction: column; gap: 16px; }
        form p { color: #666; margin: 0 0 8px 0; }
        input { padding: 12px; border: 1px solid #ddd; border-radius: 8px; }
        button { padding: 14px; background: #667eea; color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; }
        button:disabled { opacity: 0.6; cursor: not-allowed; }
        .success-section { text-align: center; }
        .btn-primary { display: inline-block; padding: 14px 32px; background: #667eea; color: white; text-decoration: none; border-radius: 8px; margin-top: 16px; }
        .back-link { text-align: center; margin-top: 20px; }
        .back-link a { color: #667eea; text-decoration: none; }
      `}</style>
    </div>
  );
};

export default PasswordReset;
