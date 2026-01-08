/**
 * Mobile API Client
 * React Native API integration
 */

import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = 'https://api.workingtracker.com/api';

interface LoginResponse {
  access_token: string;
  refresh_token: string;
}

export class ApiClient {
  private baseURL: string;
  private token: string | null = null;

  constructor() {
    this.baseURL = API_BASE_URL;
    this.loadToken();
  }

  private async loadToken() {
    try {
      this.token = await AsyncStorage.getItem('auth_token');
    } catch (error) {
      console.error('Error loading token:', error);
    }
  }

  private async setToken(token: string) {
    this.token = token;
    await AsyncStorage.setItem('auth_token', token);
  }

  private async clearToken() {
    this.token = null;
    await AsyncStorage.removeItem('auth_token');
  }

  private async request(endpoint: string, options: RequestInit = {}): Promise<any> {
    const url = `${this.baseURL}${endpoint}`;
    
    const headers: HeadersInit = {
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
  async login(email: string, password: string): Promise<LoginResponse> {
    const response = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    
    await this.setToken(response.access_token);
    await AsyncStorage.setItem('refresh_token', response.refresh_token);
    
    return response;
  }

  async refreshToken(): Promise<void> {
    const refreshToken = await AsyncStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token');
    }

    const response = await this.request('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    await this.setToken(response.access_token);
  }

  async logout(): Promise<void> {
    await this.request('/auth/logout', { method: 'POST' });
    await this.clearToken();
  }

  // Time Tracking
  async clockIn(): Promise<any> {
    return this.request('/time/clock-in', { method: 'POST' });
  }

  async clockOut(): Promise<any> {
    return this.request('/time/clock-out', { method: 'POST' });
  }

  async getTimeEntries(params: any = {}): Promise<any> {
    const query = new URLSearchParams(params).toString();
    return this.request(`/time/entries?${query}`);
  }

  // Employees
  async getEmployees(): Promise<any> {
    return this.request('/employees');
  }

  async getEmployee(employeeId: string): Promise<any> {
    return this.request(`/employees/${employeeId}`);
  }

  // Dashboard
  async getDashboardData(): Promise<any> {
    return this.request('/reports/dashboard');
  }
}

// Export singleton
export const apiClient = new ApiClient();
export default apiClient;
