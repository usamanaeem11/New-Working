/**
 * Complete Mobile API Client
 * Fully wired with dashboard endpoints
 */

import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = 'https://api.workingtracker.com/api';

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
    await AsyncStorage.removeItem('refresh_token');
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
  async login(email: string, password: string) {
    const response = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    
    await this.setToken(response.access_token);
    await AsyncStorage.setItem('refresh_token', response.refresh_token);
    
    return { success: true, data: response };
  }

  async refreshToken(): Promise<void> {
    const refreshToken = await AsyncStorage.getItem('refresh_token');
    if (!refreshToken) throw new Error('No refresh token');

    const response = await this.request('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    await this.setToken(response.access_token);
  }

  async logout(): Promise<any> {
    await this.request('/auth/logout', { method: 'POST' });
    await this.clearToken();
    return { success: true };
  }

  // Dashboard - Complete Integration
  async getDashboardData(): Promise<any> {
    const data = await this.request('/dashboard/complete');
    return { success: true, data };
  }

  async getDashboardMetrics(): Promise<any> {
    const data = await this.request('/dashboard/metrics');
    return { success: true, data };
  }

  async getUserStatus(): Promise<any> {
    const data = await this.request('/dashboard/status');
    return { success: true, data };
  }

  // Time Tracking
  async clockIn(): Promise<any> {
    const data = await this.request('/time/clock-in', { method: 'POST' });
    return { success: true, data };
  }

  async clockOut(): Promise<any> {
    const data = await this.request('/time/clock-out', { method: 'POST' });
    return { success: true, data };
  }

  async getTimeEntries(params: any = {}): Promise<any> {
    const query = new URLSearchParams(params).toString();
    const data = await this.request(`/time/entries${query ? '?' + query : ''}`);
    return { success: true, data };
  }

  // Employees
  async getEmployees(): Promise<any> {
    const data = await this.request('/employees');
    return { success: true, data };
  }

  async getEmployee(employeeId: string): Promise<any> {
    const data = await this.request(`/employees/${employeeId}`);
    return { success: true, data };
  }
}

// Export singleton
export const apiClient = new ApiClient();
export default apiClient;
