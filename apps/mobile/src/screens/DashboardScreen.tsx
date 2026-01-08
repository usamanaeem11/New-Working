/**
 * Mobile Dashboard Screen
 * Real-time metrics and quick actions
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { apiClient } from '../services/ApiClient';

interface DashboardMetrics {
  activeEmployees: number;
  clockedIn: number;
  todayHours: number;
  weekHours: number;
}

const DashboardScreen = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics>({
    activeEmployees: 0,
    clockedIn: 0,
    todayHours: 0,
    weekHours: 0,
  });
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [isClockedIn, setIsClockedIn] = useState(false);

  const loadDashboard = async () => {
    try {
      const result = await apiClient.getDashboardData();
      if (result.success) {
        setMetrics(result.data.metrics);
        setIsClockedIn(result.data.is_clocked_in);
      }
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  const handleClockIn = async () => {
    try {
      const result = await apiClient.clockIn();
      if (result.success) {
        setIsClockedIn(true);
        loadDashboard();
      }
    } catch (error) {
      console.error('Clock in failed:', error);
    }
  };

  const handleClockOut = async () => {
    try {
      const result = await apiClient.clockOut();
      if (result.success) {
        setIsClockedIn(false);
        loadDashboard();
      }
    } catch (error) {
      console.error('Clock out failed:', error);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadDashboard();
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#2563eb" />
        <Text style={styles.loadingText}>Loading dashboard...</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Dashboard</Text>
        <Text style={styles.headerSubtitle}>
          {new Date().toLocaleDateString('en-US', { 
            weekday: 'long', 
            month: 'long', 
            day: 'numeric' 
          })}
        </Text>
      </View>

      {/* Metrics Cards */}
      <View style={styles.metricsGrid}>
        <View style={styles.metricCard}>
          <Text style={styles.metricIcon}>👥</Text>
          <Text style={styles.metricLabel}>Active</Text>
          <Text style={styles.metricValue}>{metrics.activeEmployees}</Text>
        </View>

        <View style={styles.metricCard}>
          <Text style={styles.metricIcon}>⏰</Text>
          <Text style={styles.metricLabel}>Clocked In</Text>
          <Text style={styles.metricValue}>{metrics.clockedIn}</Text>
        </View>

        <View style={styles.metricCard}>
          <Text style={styles.metricIcon}>📊</Text>
          <Text style={styles.metricLabel}>Today</Text>
          <Text style={styles.metricValue}>{metrics.todayHours}h</Text>
        </View>

        <View style={styles.metricCard}>
          <Text style={styles.metricIcon}>📅</Text>
          <Text style={styles.metricLabel}>Week</Text>
          <Text style={styles.metricValue}>{metrics.weekHours}h</Text>
        </View>
      </View>

      {/* Time Tracking */}
      <View style={styles.timeTrackingCard}>
        <Text style={styles.cardTitle}>Time Tracking</Text>
        
        {isClockedIn ? (
          <View style={styles.clockedInContainer}>
            <View style={styles.statusIndicator}>
              <View style={styles.statusDot} />
              <Text style={styles.statusText}>Currently Working</Text>
            </View>
            <TouchableOpacity
              style={[styles.button, styles.buttonDanger]}
              onPress={handleClockOut}
            >
              <Text style={styles.buttonText}>Clock Out</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <View style={styles.clockedOutContainer}>
            <Text style={styles.infoText}>
              You're not currently clocked in
            </Text>
            <TouchableOpacity
              style={[styles.button, styles.buttonPrimary]}
              onPress={handleClockIn}
            >
              <Text style={styles.buttonText}>Clock In</Text>
            </TouchableOpacity>
          </View>
        )}
      </View>

      {/* Quick Actions */}
      <View style={styles.quickActionsCard}>
        <Text style={styles.cardTitle}>Quick Actions</Text>
        <View style={styles.actionButtons}>
          <TouchableOpacity style={styles.actionButton}>
            <Text style={styles.actionIcon}>📋</Text>
            <Text style={styles.actionLabel}>View Schedule</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.actionButton}>
            <Text style={styles.actionIcon}>📊</Text>
            <Text style={styles.actionLabel}>View Reports</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.actionButton}>
            <Text style={styles.actionIcon}>👥</Text>
            <Text style={styles.actionLabel}>Team</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.actionButton}>
            <Text style={styles.actionIcon}>⚙️</Text>
            <Text style={styles.actionLabel}>Settings</Text>
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f8fafc',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#64748b',
  },
  header: {
    padding: 24,
    backgroundColor: '#ffffff',
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: '600',
    color: '#1e293b',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#64748b',
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 16,
    gap: 12,
  },
  metricCard: {
    flex: 1,
    minWidth: '45%',
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  metricIcon: {
    fontSize: 32,
    marginBottom: 8,
  },
  metricLabel: {
    fontSize: 12,
    color: '#64748b',
    marginBottom: 4,
  },
  metricValue: {
    fontSize: 24,
    fontWeight: '600',
    color: '#2563eb',
  },
  timeTrackingCard: {
    margin: 16,
    padding: 20,
    backgroundColor: '#ffffff',
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  quickActionsCard: {
    margin: 16,
    padding: 20,
    backgroundColor: '#ffffff',
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1e293b',
    marginBottom: 16,
  },
  clockedInContainer: {
    alignItems: 'center',
  },
  clockedOutContainer: {
    alignItems: 'center',
  },
  statusIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#10b981',
    marginRight: 8,
  },
  statusText: {
    fontSize: 14,
    color: '#10b981',
    fontWeight: '600',
  },
  infoText: {
    fontSize: 14,
    color: '#64748b',
    marginBottom: 16,
  },
  button: {
    paddingVertical: 12,
    paddingHorizontal: 32,
    borderRadius: 8,
    minWidth: 200,
  },
  buttonPrimary: {
    backgroundColor: '#10b981',
  },
  buttonDanger: {
    backgroundColor: '#ef4444',
  },
  buttonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
  },
  actionButtons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  actionButton: {
    flex: 1,
    minWidth: '45%',
    padding: 16,
    backgroundColor: '#f8fafc',
    borderRadius: 8,
    alignItems: 'center',
  },
  actionIcon: {
    fontSize: 32,
    marginBottom: 8,
  },
  actionLabel: {
    fontSize: 12,
    color: '#475569',
    textAlign: 'center',
  },
});

export default DashboardScreen;
