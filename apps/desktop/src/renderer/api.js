/**
 * Desktop Renderer API
 * API wrapper for renderer process
 */
const { ipcRenderer } = window.require('electron');

class DesktopAPI {
  // Authentication
  async login(email, password) {
    return ipcRenderer.invoke('auth:login', { email, password });
  }

  async logout() {
    return ipcRenderer.invoke('auth:logout');
  }

  // Employees
  async getEmployees() {
    return ipcRenderer.invoke('employees:getAll');
  }

  async getEmployee(id) {
    return ipcRenderer.invoke('employees:getOne', id);
  }

  async createEmployee(data) {
    return ipcRenderer.invoke('employees:create', data);
  }

  // Time Tracking
  async clockIn() {
    return ipcRenderer.invoke('time:clockIn');
  }

  async clockOut() {
    return ipcRenderer.invoke('time:clockOut');
  }

  async getTimeEntries(params) {
    return ipcRenderer.invoke('time:getEntries', params);
  }

  // Dashboard
  async getDashboardData() {
    return ipcRenderer.invoke('dashboard:getData');
  }

  // Settings
  async getSettings() {
    return ipcRenderer.invoke('settings:get');
  }

  async setSettings(settings) {
    return ipcRenderer.invoke('settings:set', settings);
  }
}

export const desktopAPI = new DesktopAPI();
export default desktopAPI;
