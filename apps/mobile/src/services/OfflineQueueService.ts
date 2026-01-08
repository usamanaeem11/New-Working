/**
 * Offline Queue Service - REAL IMPLEMENTATION
 * Queues operations when offline, syncs when online
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';
import { apiClient } from './ApiClient-complete';

interface QueuedOperation {
  id: string;
  endpoint: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  body?: any;
  timestamp: number;
  retries: number;
}

class OfflineQueueService {
  private queue: QueuedOperation[] = [];
  private isOnline: boolean = true;
  private isSyncing: boolean = false;
  private readonly QUEUE_KEY = 'offline_queue';
  private readonly MAX_RETRIES = 3;
  
  constructor() {
    this.initialize();
  }
  
  private async initialize() {
    // Load queue from storage
    await this.loadQueue();
    
    // Monitor network status
    NetInfo.addEventListener(state => {
      const wasOnline = this.isOnline;
      this.isOnline = state.isConnected || false;
      
      // If we just came online, sync
      if (!wasOnline && this.isOnline) {
        console.log('📡 Network reconnected, syncing offline queue...');
        this.syncQueue();
      }
    });
    
    // Initial network check
    const state = await NetInfo.fetch();
    this.isOnline = state.isConnected || false;
    
    if (this.isOnline) {
      this.syncQueue();
    }
  }
  
  private async loadQueue() {
    try {
      const queueJson = await AsyncStorage.getItem(this.QUEUE_KEY);
      if (queueJson) {
        this.queue = JSON.parse(queueJson);
        console.log(`📦 Loaded ${this.queue.length} operations from offline queue`);
      }
    } catch (error) {
      console.error('Failed to load offline queue:', error);
    }
  }
  
  private async saveQueue() {
    try {
      await AsyncStorage.setItem(this.QUEUE_KEY, JSON.stringify(this.queue));
    } catch (error) {
      console.error('Failed to save offline queue:', error);
    }
  }
  
  async addToQueue(
    endpoint: string,
    method: 'GET' | 'POST' | 'PUT' | 'DELETE',
    body?: any
  ): Promise<string> {
    const operation: QueuedOperation = {
      id: Date.now().toString() + Math.random().toString(36),
      endpoint,
      method,
      body,
      timestamp: Date.now(),
      retries: 0
    };
    
    this.queue.push(operation);
    await this.saveQueue();
    
    console.log(`➕ Added to offline queue: ${method} ${endpoint}`);
    
    // Try to sync immediately if online
    if (this.isOnline) {
      this.syncQueue();
    }
    
    return operation.id;
  }
  
  async syncQueue(): Promise<void> {
    if (this.isSyncing || !this.isOnline || this.queue.length === 0) {
      return;
    }
    
    this.isSyncing = true;
    console.log(`🔄 Syncing ${this.queue.length} queued operations...`);
    
    const failedOperations: QueuedOperation[] = [];
    
    for (const operation of this.queue) {
      try {
        // Execute the queued operation
        await apiClient.request(operation.endpoint, {
          method: operation.method,
          body: operation.body ? JSON.stringify(operation.body) : undefined
        });
        
        console.log(`✅ Synced: ${operation.method} ${operation.endpoint}`);
      } catch (error) {
        console.error(`❌ Failed to sync: ${operation.method} ${operation.endpoint}`, error);
        
        // Retry logic
        operation.retries++;
        if (operation.retries < this.MAX_RETRIES) {
          failedOperations.push(operation);
        } else {
          console.log(`⚠️ Dropping operation after ${this.MAX_RETRIES} retries`);
        }
      }
    }
    
    // Update queue with failed operations
    this.queue = failedOperations;
    await this.saveQueue();
    
    this.isSyncing = false;
    
    if (this.queue.length === 0) {
      console.log('✨ Offline queue is empty');
    } else {
      console.log(`⏳ ${this.queue.length} operations still pending`);
    }
  }
  
  async executeOrQueue(
    endpoint: string,
    method: 'GET' | 'POST' | 'PUT' | 'DELETE',
    body?: any
  ): Promise<any> {
    if (this.isOnline) {
      // Try to execute immediately
      try {
        return await apiClient.request(endpoint, {
          method,
          body: body ? JSON.stringify(body) : undefined
        });
      } catch (error) {
        // If failed, queue it
        console.log('Request failed, adding to queue');
        await this.addToQueue(endpoint, method, body);
        throw error;
      }
    } else {
      // Offline, queue it
      const id = await this.addToQueue(endpoint, method, body);
      return { queued: true, queueId: id };
    }
  }
  
  getQueueLength(): number {
    return this.queue.length;
  }
  
  isNetworkOnline(): boolean {
    return this.isOnline;
  }
  
  async clearQueue(): Promise<void> {
    this.queue = [];
    await this.saveQueue();
  }
}

export const offlineQueue = new OfflineQueueService();
