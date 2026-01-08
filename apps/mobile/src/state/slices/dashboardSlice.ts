/**
 * Dashboard State Slice
 */

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { apiClient } from '../../services/ApiClient-complete';

interface DashboardState {
  metrics: any | null;
  employees: any[];
  activity: any[];
  loading: boolean;
  error: string | null;
  lastUpdated: number | null;
}

const initialState: DashboardState = {
  metrics: null,
  employees: [],
  activity: [],
  loading: false,
  error: null,
  lastUpdated: null,
};

export const fetchDashboard = createAsyncThunk(
  'dashboard/fetch',
  async () => {
    const response = await apiClient.getDashboardData();
    return response.data;
  }
);

const dashboardSlice = createSlice({
  name: 'dashboard',
  initialState,
  reducers: {
    clearDashboard: (state) => {
      state.metrics = null;
      state.employees = [];
      state.activity = [];
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchDashboard.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDashboard.fulfilled, (state, action) => {
        state.loading = false;
        state.metrics = action.payload.metrics;
        state.employees = action.payload.employees || [];
        state.activity = action.payload.activity || [];
        state.lastUpdated = Date.now();
      })
      .addCase(fetchDashboard.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch dashboard';
      });
  },
});

export const { clearDashboard } = dashboardSlice.actions;
export default dashboardSlice.reducer;
