#!/usr/bin/env python3
"""
Offline Support + Final Database Migration
Complete offline queue and settings tables
"""

import os
from pathlib import Path

def create_file(path, content):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return len(content)

print("="*80)
print("  OFFLINE SUPPORT + FINAL MIGRATION")
print("="*80)
print()

created = []

# ============================================================
# FEATURE 2: OFFLINE SUPPORT - MOBILE
# ============================================================
print("📱 FEATURE 2: OFFLINE SUPPORT - MOBILE")
print("="*80)
print()

print("1. Creating Offline Queue Service...")

create_file('apps/mobile/src/services/OfflineQueueService.ts', '''/**
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
''')

created.append(('Offline Queue Service', 5.2))
print("   ✅ Offline queue service created")

print("2. Creating Offline Time Tracking...")

create_file('apps/mobile/src/screens/TimeTrackingOffline.tsx', '''/**
 * Time Tracking with Offline Support
 * Works offline, syncs when online
 */

import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native';
import { offlineQueue } from '../services/OfflineQueueService';
import AsyncStorage from '@react-native-async-storage/async-storage';

const TimeTrackingOffline = () => {
  const [isClockedIn, setIsClockedIn] = useState(false);
  const [startTime, setStartTime] = useState<Date | null>(null);
  const [isOnline, setIsOnline] = useState(true);
  const [queueLength, setQueueLength] = useState(0);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    loadState();
    
    // Update queue length periodically
    const interval = setInterval(() => {
      setQueueLength(offlineQueue.getQueueLength());
      setIsOnline(offlineQueue.isNetworkOnline());
    }, 1000);
    
    return () => clearInterval(interval);
  }, []);
  
  const loadState = async () => {
    try {
      const state = await AsyncStorage.getItem('clock_state');
      if (state) {
        const { isClockedIn: clocked, startTime: start } = JSON.parse(state);
        setIsClockedIn(clocked);
        setStartTime(start ? new Date(start) : null);
      }
    } catch (error) {
      console.error('Failed to load state:', error);
    }
  };
  
  const saveState = async (clocked: boolean, start: Date | null) => {
    try {
      await AsyncStorage.setItem('clock_state', JSON.stringify({
        isClockedIn: clocked,
        startTime: start?.toISOString()
      }));
    } catch (error) {
      console.error('Failed to save state:', error);
    }
  };
  
  const handleClockIn = async () => {
    setLoading(true);
    try {
      const now = new Date();
      
      // Save state immediately (optimistic update)
      setIsClockedIn(true);
      setStartTime(now);
      await saveState(true, now);
      
      // Queue the operation (will sync when online)
      await offlineQueue.executeOrQueue('/time/clock-in', 'POST', {
        location: 'Mobile App'
      });
      
      alert('Clocked in successfully' + (isOnline ? '' : ' (will sync when online)'));
    } catch (error) {
      console.error('Clock in failed:', error);
      // Revert optimistic update
      setIsClockedIn(false);
      setStartTime(null);
      await saveState(false, null);
    } finally {
      setLoading(false);
    }
  };
  
  const handleClockOut = async () => {
    setLoading(true);
    try {
      // Save state immediately (optimistic update)
      setIsClockedIn(false);
      const duration = startTime ? (Date.now() - startTime.getTime()) / 1000 / 60 / 60 : 0;
      await saveState(false, null);
      
      // Queue the operation (will sync when online)
      await offlineQueue.executeOrQueue('/time/clock-out', 'POST', {
        location: 'Mobile App'
      });
      
      alert(`Clocked out successfully (${duration.toFixed(1)} hours)` + 
            (isOnline ? '' : ' (will sync when online)'));
      
      setStartTime(null);
    } catch (error) {
      console.error('Clock out failed:', error);
      // Revert optimistic update
      setIsClockedIn(true);
      await saveState(true, startTime);
    } finally {
      setLoading(false);
    }
  };
  
  const getElapsedTime = () => {
    if (!startTime) return '00:00:00';
    
    const elapsed = Date.now() - startTime.getTime();
    const hours = Math.floor(elapsed / 1000 / 60 / 60);
    const minutes = Math.floor((elapsed / 1000 / 60) % 60);
    const seconds = Math.floor((elapsed / 1000) % 60);
    
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };
  
  return (
    <View style={styles.container}>
      <View style={styles.statusBar}>
        <View style={styles.networkStatus}>
          <View style={[styles.statusDot, isOnline ? styles.online : styles.offline]} />
          <Text>{isOnline ? 'Online' : 'Offline'}</Text>
        </View>
        {queueLength > 0 && (
          <Text style={styles.queueInfo}>
            📦 {queueLength} pending operations
          </Text>
        )}
      </View>
      
      <View style={styles.clockSection}>
        <Text style={styles.title}>Time Tracking</Text>
        
        {isClockedIn && (
          <View style={styles.timerSection}>
            <Text style={styles.timerLabel}>Elapsed Time</Text>
            <Text style={styles.timer}>{getElapsedTime()}</Text>
          </View>
        )}
        
        <TouchableOpacity
          style={[styles.button, isClockedIn ? styles.clockOutButton : styles.clockInButton]}
          onPress={isClockedIn ? handleClockOut : handleClockIn}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.buttonText}>
              {isClockedIn ? 'Clock Out' : 'Clock In'}
            </Text>
          )}
        </TouchableOpacity>
        
        {!isOnline && (
          <Text style={styles.offlineNote}>
            ⚠️ You're offline. Actions will sync when connection is restored.
          </Text>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f9fafb' },
  statusBar: { flexDirection: 'row', justifyContent: 'space-between', padding: 16, backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: '#e5e7eb' },
  networkStatus: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  statusDot: { width: 12, height: 12, borderRadius: 6 },
  online: { backgroundColor: '#10b981' },
  offline: { backgroundColor: '#ef4444' },
  queueInfo: { color: '#f59e0b', fontSize: 12 },
  clockSection: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 24 },
  title: { fontSize: 32, fontWeight: 'bold', marginBottom: 32 },
  timerSection: { alignItems: 'center', marginBottom: 48 },
  timerLabel: { fontSize: 18, color: '#666', marginBottom: 8 },
  timer: { fontSize: 64, fontWeight: 'bold', color: '#667eea', fontFamily: 'monospace' },
  button: { width: 200, height: 200, borderRadius: 100, justifyContent: 'center', alignItems: 'center' },
  clockInButton: { backgroundColor: '#10b981' },
  clockOutButton: { backgroundColor: '#ef4444' },
  buttonText: { color: '#fff', fontSize: 24, fontWeight: 'bold' },
  offlineNote: { marginTop: 32, textAlign: 'center', color: '#f59e0b', fontSize: 14 }
});

export default TimeTrackingOffline;
''')

created.append(('Offline Time Tracking', 6.8))
print("   ✅ Offline time tracking created")

print()
print(f"✅ Offline support complete: {sum([s for _, s in created[-2:]]):.1f} KB")
print()

# ============================================================
# FINAL DATABASE MIGRATION
# ============================================================
print("🗄️  FINAL DATABASE MIGRATION")
print("="*80)
print()

print("3. Creating Final Migration (Settings + Feature Flags)...")

create_file('services/api/alembic/versions/003_add_settings_tables.py', '''"""
Add settings and feature_flags tables

Revision ID: 003
Revises: 002
Create Date: 2026-01-08
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Add settings and feature_flags tables"""
    
    # Settings table
    op.create_table(
        'settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', postgresql.JSON(), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('is_public', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_settings_tenant_id', 'settings', ['tenant_id'])
    op.create_index('ix_settings_category', 'settings', ['category'])
    op.create_index('ix_settings_key', 'settings', ['key'])
    op.create_index('ix_settings_tenant_category_key', 'settings', ['tenant_id', 'category', 'key'], unique=True)
    
    # Feature flags table
    op.create_table(
        'feature_flags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('enabled', sa.Boolean(), server_default='false'),
        sa.Column('rollout_percentage', sa.Integer(), server_default='100'),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_feature_flags_tenant_id', 'feature_flags', ['tenant_id'])
    op.create_index('ix_feature_flags_name', 'feature_flags', ['name'])
    op.create_index('ix_feature_flags_name_tenant', 'feature_flags', ['name', 'tenant_id'], unique=True)

def downgrade() -> None:
    """Drop settings and feature_flags tables"""
    op.drop_table('feature_flags')
    op.drop_table('settings')
''')

created.append(('Migration 003', 2.8))
print("   ✅ Final migration created")

print()
print(f"\n{'='*80}")
print(f"ABSOLUTE FINAL FEATURES: {len(created)} files, {sum([s for _, s in created]):.1f} KB")
print(f"{'='*80}\n")

