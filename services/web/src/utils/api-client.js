/**
 * Frontend API Client
 * Real API integration replacing MOCK_DATA
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

class APIClient {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.token = localStorage.getItem('auth_token');
  }

  setToken(token) {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (response.status === 401) {
        // Token expired, try refresh
        await this.refreshToken();
        return this.request(endpoint, options);
      }

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Request failed');
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error);
      throw error;
    }
  }

  // Authentication
  async login(email, password) {
    const response = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    
    this.setToken(response.access_token);
    localStorage.setItem('refresh_token', response.refresh_token);
    
    return response;
  }

  async refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token');
    }

    const response = await this.request('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    this.setToken(response.access_token);
    return response;
  }

  async logout() {
    await this.request('/auth/logout', { method: 'POST' });
    this.clearToken();
  }

  // Users
  async getUsers() {
    return this.request('/users');
  }

  async getUser(userId) {
    return this.request(`/users/${userId}`);
  }

  async createUser(userData) {
    return this.request('/users', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  // Employees
  async getEmployees() {
    return this.request('/employees');
  }

  async getEmployee(employeeId) {
    return this.request(`/employees/${employeeId}`);
  }

  // Time Tracking
  async getTimeEntries(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/time/entries?${query}`);
  }

  async clockIn() {
    return this.request('/time/clock-in', { method: 'POST' });
  }

  async clockOut() {
    return this.request('/time/clock-out', { method: 'POST' });
  }

  // Payroll
  async getPayrollRuns() {
    return this.request('/payroll/runs');
  }

  async runPayroll(data) {
    return this.request('/payroll/run', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Reports
  async getDashboardData() {
    return this.request('/reports/dashboard');
  }

  async getReport(reportType, params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/reports/${reportType}?${query}`);
  }

  // AI & Analytics
  async getAIInsights(type) {
    return this.request(`/ai/insights/${type}`);
  }
}

// Export singleton instance
export const apiClient = new APIClient();
export default apiClient;
