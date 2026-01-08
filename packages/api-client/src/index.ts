import axios, { AxiosInstance } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 
                process.env.EXPO_PUBLIC_API_URL || 
                process.env.ELECTRON_API_URL || 
                'http://localhost:8000';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth token to requests
    this.client.interceptors.request.use((config) => {
      const token = this.getToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
  }

  private getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('token');
    }
    return null;
  }

  // Auth endpoints
  async login(email: string, password: string) {
    const response = await this.client.post('/api/auth/login', { email, password });
    if (response.data.token) {
      this.setToken(response.data.token);
    }
    return response.data;
  }

  async register(data: any) {
    return this.client.post('/api/auth/register', data);
  }

  async logout() {
    this.setToken(null);
    return this.client.post('/api/auth/logout');
  }

  private setToken(token: string | null) {
    if (typeof window !== 'undefined') {
      if (token) {
        localStorage.setItem('token', token);
      } else {
        localStorage.removeItem('token');
      }
    }
  }

  // Employee endpoints
  employees = {
    list: () => this.client.get('/api/employees'),
    get: (id: string) => this.client.get(`/api/employees/${id}`),
    create: (data: any) => this.client.post('/api/employees', data),
    update: (id: string, data: any) => this.client.put(`/api/employees/${id}`, data),
    delete: (id: string) => this.client.delete(`/api/employees/${id}`),
  };

  // Time entries endpoints
  timeEntries = {
    list: () => this.client.get('/api/time-entries'),
    create: (data: any) => this.client.post('/api/time-entries', data),
    clockIn: () => this.client.post('/api/time-entries/clock-in'),
    clockOut: (id: string) => this.client.post(`/api/time-entries/${id}/clock-out`),
  };

  // Projects endpoints
  projects = {
    list: () => this.client.get('/api/projects'),
    get: (id: string) => this.client.get(`/api/projects/${id}`),
    create: (data: any) => this.client.post('/api/projects', data),
  };

  // Analytics endpoints
  analytics = {
    dashboard: () => this.client.get('/api/analytics/dashboard'),
    reports: () => this.client.get('/api/analytics/reports'),
  };
}

export const api = new APIClient();
export default api;
