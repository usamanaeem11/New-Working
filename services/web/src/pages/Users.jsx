/**
 * User Management Page
 * List, create, update users with role management
 */

import React, { useState, useEffect } from 'react';
import { apiClient } from '../utils/api-client-complete';

const Users = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  
  useEffect(() => {
    loadUsers();
  }, []);
  
  const loadUsers = async () => {
    setLoading(true);
    try {
      const response = await apiClient.request('/users');
      setUsers(response.data || []);
    } catch (error) {
      console.error('Failed to load users:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleCreateUser = () => {
    setEditingUser({ email: '', first_name: '', last_name: '', role: 'employee' });
    setShowModal(true);
  };
  
  const handleSaveUser = async () => {
    try {
      if (editingUser.id) {
        await apiClient.request(`/users/${editingUser.id}`, {
          method: 'PUT',
          body: JSON.stringify(editingUser)
        });
      } else {
        await apiClient.request('/users', {
          method: 'POST',
          body: JSON.stringify(editingUser)
        });
      }
      setShowModal(false);
      loadUsers();
    } catch (error) {
      console.error('Failed to save user:', error);
    }
  };
  
  return (
    <div className="users-page">
      <div className="page-header">
        <h1>User Management</h1>
        <button className="btn-primary" onClick={handleCreateUser}>
          + Add User
        </button>
      </div>
      
      {loading ? (
        <div className="loading">Loading users...</div>
      ) : (
        <div className="users-grid">
          {users.map(user => (
            <div key={user.id} className="user-card">
              <div className="user-info">
                <h3>{user.first_name} {user.last_name}</h3>
                <p>{user.email}</p>
                <span className="badge">{user.role}</span>
              </div>
              <div className="user-actions">
                <button onClick={() => { setEditingUser(user); setShowModal(true); }}>
                  Edit
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
      
      {showModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h2>{editingUser.id ? 'Edit User' : 'Create User'}</h2>
            <form onSubmit={(e) => { e.preventDefault(); handleSaveUser(); }}>
              <input
                placeholder="First Name"
                value={editingUser.first_name}
                onChange={(e) => setEditingUser({...editingUser, first_name: e.target.value})}
                required
              />
              <input
                placeholder="Last Name"
                value={editingUser.last_name}
                onChange={(e) => setEditingUser({...editingUser, last_name: e.target.value})}
                required
              />
              <input
                type="email"
                placeholder="Email"
                value={editingUser.email}
                onChange={(e) => setEditingUser({...editingUser, email: e.target.value})}
                required
              />
              <select
                value={editingUser.role}
                onChange={(e) => setEditingUser({...editingUser, role: e.target.value})}
              >
                <option value="employee">Employee</option>
                <option value="manager">Manager</option>
                <option value="admin">Admin</option>
              </select>
              <div className="modal-actions">
                <button type="submit" className="btn-primary">Save</button>
                <button type="button" onClick={() => setShowModal(false)}>Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}
      
      <style jsx>{`
        .users-page { padding: 24px; }
        .page-header { display: flex; justify-content: space-between; margin-bottom: 24px; }
        .users-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }
        .user-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .user-info h3 { margin: 0 0 8px 0; }
        .user-info p { color: #666; margin: 0 0 8px 0; }
        .badge { background: #667eea; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; }
        .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; }
        .modal { background: white; padding: 32px; border-radius: 12px; width: 500px; }
        .modal form { display: flex; flex-direction: column; gap: 16px; }
        .modal input, .modal select { padding: 12px; border: 1px solid #ddd; border-radius: 8px; }
        .modal-actions { display: flex; gap: 12px; }
        .btn-primary { background: #667eea; color: white; padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; }
      `}</style>
    </div>
  );
};

export default Users;
