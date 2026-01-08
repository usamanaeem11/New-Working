/**
 * Electron IPC Handlers
 * Bridge between renderer and main process
 */
const { ipcMain } = require('electron');
const Store = require('electron-store');
const fetch = require('node-fetch');

const store = new Store();
const API_BASE_URL = 'https://api.workingtracker.com/api';

class IPCBridge {
  constructor() {
    this.token = store.get('auth_token', null);
  }

  setupHandlers() {
    // Authentication
    ipcMain.handle('auth:login', async (event, { email, password }) => {
      try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password }),
        });

        const data = await response.json();
        
        if (response.ok) {
          this.token = data.access_token;
          store.set('auth_token', data.access_token);
          store.set('refresh_token', data.refresh_token);
          return { success: true, data };
        } else {
          throw new Error(data.detail || 'Login failed');
        }
      } catch (error) {
        return { success: false, error: error.message };
      }
    });

    ipcMain.handle('auth:logout', async () => {
      try {
        await this.request('/auth/logout', { method: 'POST' });
        this.token = null;
        store.delete('auth_token');
        store.delete('refresh_token');
        return { success: true };
      } catch (error) {
        return { success: false, error: error.message };
      }
    });

    // Employees
    ipcMain.handle('employees:getAll', async () => {
      return this.request('/employees');
    });

    ipcMain.handle('employees:getOne', async (event, id) => {
      return this.request(`/employees/${id}`);
    });

    ipcMain.handle('employees:create', async (event, data) => {
      return this.request('/employees', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    });

    // Time Tracking
    ipcMain.handle('time:clockIn', async () => {
      return this.request('/time/clock-in', { method: 'POST' });
    });

    ipcMain.handle('time:clockOut', async () => {
      return this.request('/time/clock-out', { method: 'POST' });
    });

    ipcMain.handle('time:getEntries', async (event, params) => {
      const query = new URLSearchParams(params).toString();
      return this.request(`/time/entries?${query}`);
    });

    // Dashboard
    ipcMain.handle('dashboard:getData', async () => {
      return this.request('/reports/dashboard');
    });

    // Settings
    ipcMain.handle('settings:get', () => {
      return store.get('settings', {});
    });

    ipcMain.handle('settings:set', (event, settings) => {
      store.set('settings', settings);
      return { success: true };
    });
  }

  async request(endpoint, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
      });

      if (response.status === 401) {
        // Try to refresh token
        await this.refreshToken();
        // Retry request
        return this.request(endpoint, options);
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Request failed');
      }

      return { success: true, data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async refreshToken() {
    const refreshToken = store.get('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token');
    }

    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    const data = await response.json();
    
    if (response.ok) {
      this.token = data.access_token;
      store.set('auth_token', data.access_token);
    } else {
      throw new Error('Token refresh failed');
    }
  }
}

module.exports = IPCBridge;
