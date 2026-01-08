/**
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
