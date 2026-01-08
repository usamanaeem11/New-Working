/**
 * Time Tracking Hook
 * React hook for time tracking features
 */
import { useState } from 'react';
import { apiClient } from '../utils/api-client';

export const useTimeTracking = () => {
  const [activeEntry, setActiveEntry] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const clockIn = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const entry = await apiClient.clockIn();
      setActiveEntry(entry);
      return entry;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const clockOut = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const entry = await apiClient.clockOut();
      setActiveEntry(null);
      return entry;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const getTimeEntries = async (params) => {
    setLoading(true);
    try {
      return await apiClient.getTimeEntries(params);
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    activeEntry,
    loading,
    error,
    clockIn,
    clockOut,
    getTimeEntries,
  };
};
