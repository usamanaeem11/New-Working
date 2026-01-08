/**
 * Offline Manager
 * Handles offline data storage and sync
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';

interface QueuedRequest {
  id: string;
  method: string;
  endpoint: string;
  data: any;
  timestamp: number;
  retries: number;
}

class OfflineManager {
  private queue: QueuedRequest[] = [];
  private isOnline: boolean = true;
  private syncInProgress: boolean = false;
  
  constructor() {
    this.loadQueue();
    this.setupNetworkListener();
  }
  
  private async loadQueue() {
    try {
      const queueData = await AsyncStorage.getItem('offline_queue');
      if (queueData) {
        this.queue = JSON.parse(queueData);
      }
    } catch (error) {
      console.error('Failed to load offline queue:', error);
    }
  }
  
  private async saveQueue() {
    try {
      await AsyncStorage.setItem('offline_queue', JSON.stringify(this.queue));
    } catch (error) {
      console.error('Failed to save offline queue:', error);
    }
  }
  
  private setupNetworkListener() {
    NetInfo.addEventListener(state => {
      const wasOffline = !this.isOnline;
      this.isOnline = state.isConnected || false;
      
      // If we just came online, sync
      if (wasOffline && this.isOnline) {
        console.log('Network restored, syncing queue...');
        this.syncQueue();
      }
    });
  }
  
  async queueRequest(method: string, endpoint: string, data: any): Promise<string> {
    const request: QueuedRequest = {
      id: Date.now().toString() + Math.random(),
      method,
      endpoint,
      data,
      timestamp: Date.now(),
      retries: 0
    };
    
    this.queue.push(request);
    await this.saveQueue();
    
    console.log(`Queued ${method} ${endpoint} for offline sync`);
    return request.id;
  }
  
  async syncQueue(): Promise<void> {
    if (this.syncInProgress || !this.isOnline) {
      return;
    }
    
    if (this.queue.length === 0) {
      return;
    }
    
    this.syncInProgress = true;
    console.log(`Syncing ${this.queue.length} queued requests...`);
    
    const failedRequests: QueuedRequest[] = [];
    
    for (const request of this.queue) {
      try {
        await this.executeRequest(request);
        console.log(`Synced: ${request.method} ${request.endpoint}`);
      } catch (error) {
        console.error(`Failed to sync request:`, error);
        
        request.retries += 1;
        
        // Keep if under 5 retries
        if (request.retries < 5) {
          failedRequests.push(request);
        } else {
          console.log(`Dropping request after 5 retries: ${request.id}`);
        }
      }
    }
    
    // Update queue with only failed requests
    this.queue = failedRequests;
    await this.saveQueue();
    
    this.syncInProgress = false;
    
    if (failedRequests.length > 0) {
      console.log(`${failedRequests.length} requests still in queue`);
    } else {
      console.log('All requests synced successfully');
    }
  }
  
  private async executeRequest(request: QueuedRequest): Promise<void> {
    const { apiClient } = require('./ApiClient-complete');
    
    // Map to API client method
    if (request.method === 'POST' && request.endpoint.includes('clock-in')) {
      await apiClient.clockIn();
    } else if (request.method === 'POST' && request.endpoint.includes('clock-out')) {
      await apiClient.clockOut();
    } else if (request.method === 'POST' && request.endpoint.includes('employees')) {
      await apiClient.createEmployee(request.data);
    }
    // Add more mappings as needed
  }
  
  async cacheData(key: string, data: any): Promise<void> {
    try {
      await AsyncStorage.setItem(`cache_${key}`, JSON.stringify({
        data,
        timestamp: Date.now()
      }));
    } catch (error) {
      console.error('Failed to cache data:', error);
    }
  }
  
  async getCachedData(key: string, maxAge: number = 3600000): Promise<any> {
    try {
      const cached = await AsyncStorage.getItem(`cache_${key}`);
      if (cached) {
        const { data, timestamp } = JSON.parse(cached);
        
        // Check if cache is fresh
        if (Date.now() - timestamp < maxAge) {
          return data;
        }
      }
    } catch (error) {
      console.error('Failed to get cached data:', error);
    }
    
    return null;
  }
  
  getQueueLength(): number {
    return this.queue.length;
  }
  
  isNetworkOnline(): boolean {
    return this.isOnline;
  }
}

export const offlineManager = new OfflineManager();
export default offlineManager;
