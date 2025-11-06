/**
 * GP4U API Client Service
 * Handles all HTTP requests to FastAPI backend with JWT authentication
 */

import axios from 'axios';

// Base configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_VERSION = '/api/v1';

// Create axios instance
const apiClient = axios.create({
  baseURL: `${API_BASE_URL}${API_VERSION}`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add JWT token to all requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle 401 errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============================================
// AUTHENTICATION API
// ============================================

export const authAPI = {
  signup: async (email, password) => {
    const response = await apiClient.post('/auth/signup', { email, password });
    return response.data;
  },

  login: async (email, password) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response = await axios.post(
      `${API_BASE_URL}${API_VERSION}/auth/login`,
      formData,
      { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
    );

    // Store token and user info
    localStorage.setItem('access_token', response.data.access_token);
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await apiClient.get('/auth/me');
    localStorage.setItem('user', JSON.stringify(response.data));
    return response.data;
  },

  updateProfile: async (updates) => {
    const response = await apiClient.patch('/auth/me', updates);
    localStorage.setItem('user', JSON.stringify(response.data));
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  },

  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  },

  getStoredUser: () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }
};

// ============================================
// GPU API
// ============================================

export const gpuAPI = {
  search: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.model) params.append('model', filters.model);
    if (filters.min_vram) params.append('min_vram', filters.min_vram);
    if (filters.max_price) params.append('max_price', filters.max_price);
    if (filters.provider) params.append('provider', filters.provider);
    if (filters.location) params.append('location', filters.location);

    const response = await apiClient.get(`/gpus/search?${params.toString()}`);
    return response.data;
  },

  getById: async (gpuId) => {
    const response = await apiClient.get(`/gpus/${gpuId}`);
    return response.data;
  },

  compare: async (gpuIds) => {
    const response = await apiClient.post('/gpus/compare', { gpu_ids: gpuIds });
    return response.data;
  },

  getAvailableModels: async () => {
    const response = await apiClient.get('/gpus/models/available');
    return response.data;
  }
};

// ============================================
// ARBITRAGE API
// ============================================

export const arbitrageAPI = {
  getOpportunities: async (minSpread = null, gpuModel = null) => {
    const params = new URLSearchParams();
    if (minSpread) params.append('min_spread_pct', minSpread);
    if (gpuModel) params.append('gpu_model', gpuModel);

    const response = await apiClient.get(`/arbitrage/opportunities?${params.toString()}`);
    return response.data;
  },

  getBestDeal: async (gpuModel) => {
    const response = await apiClient.get(`/arbitrage/best-deal/${gpuModel}`);
    return response.data;
  },

  compare: async (gpuModel) => {
    const response = await apiClient.get(`/arbitrage/compare/${gpuModel}`);
    return response.data;
  },

  calculateSavings: async (gpuModel, hoursPerDay = 24) => {
    const response = await apiClient.get(
      `/arbitrage/savings/${gpuModel}?hours_per_day=${hoursPerDay}`
    );
    return response.data;
  }
};

// ============================================
// RESERVATION API
// ============================================

export const reservationAPI = {
  create: async (gpuId, startTime, endTime) => {
    const response = await apiClient.post('/reservations/', {
      gpu_id: gpuId,
      start_time: startTime,
      end_time: endTime
    });
    return response.data;
  },

  getMyBookings: async (statusFilter = null) => {
    const params = statusFilter ? `?status=${statusFilter}` : '';
    const response = await apiClient.get(`/reservations/my-bookings${params}`);
    return response.data;
  },

  getById: async (reservationId) => {
    const response = await apiClient.get(`/reservations/${reservationId}`);
    return response.data;
  },

  cancel: async (reservationId) => {
    const response = await apiClient.delete(`/reservations/${reservationId}/cancel`);
    return response.data;
  },

  extend: async (reservationId, newEndTime) => {
    const response = await apiClient.post(`/reservations/${reservationId}/extend`, {
      new_end_time: newEndTime
    });
    return response.data;
  },

  getAvailableSlots: async (gpuId, date) => {
    const response = await apiClient.get(
      `/reservations/gpu/${gpuId}/available-slots?date=${date}`
    );
    return response.data;
  },

  getCalendar: async (gpuId, days = 7) => {
    const response = await apiClient.get(
      `/reservations/gpu/${gpuId}/calendar?days=${days}`
    );
    return response.data;
  }
};

// ============================================
// CLUSTER API
// ============================================

export const clusterAPI = {
  create: async (jobName, computeIntensity, vramGb, deadlineHours, gpuCount = null) => {
    const response = await apiClient.post('/clusters/', {
      job_name: jobName,
      compute_intensity: computeIntensity,
      vram_gb: vramGb,
      deadline_hours: deadlineHours,
      gpu_count: gpuCount
    });
    return response.data;
  },

  getMyClusters: async (statusFilter = null) => {
    const params = statusFilter ? `?status=${statusFilter}` : '';
    const response = await apiClient.get(`/clusters/my-clusters${params}`);
    return response.data;
  },

  getById: async (clusterId) => {
    const response = await apiClient.get(`/clusters/${clusterId}`);
    return response.data;
  },

  start: async (clusterId) => {
    const response = await apiClient.post(`/clusters/${clusterId}/start`);
    return response.data;
  },

  stop: async (clusterId, success = true) => {
    const response = await apiClient.post(`/clusters/${clusterId}/stop`, { success });
    return response.data;
  },

  getMembers: async (clusterId) => {
    const response = await apiClient.get(`/clusters/${clusterId}/members`);
    return response.data;
  },

  simulateCost: async (computeIntensity, vramGb, deadlineHours, gpuCount = null) => {
    const response = await axios.get(
      `${API_BASE_URL}${API_VERSION}/clusters/simulate/estimate`,
      {
        params: {
          compute_intensity: computeIntensity,
          vram_gb: vramGb,
          deadline_hours: deadlineHours,
          gpu_count: gpuCount
        }
      }
    );
    return response.data;
  }
};

// ============================================
// WALLET API
// ============================================

export const walletAPI = {
  getBalance: async () => {
    const response = await apiClient.get('/wallets/balance');
    return response.data;
  },

  getTransactions: async (limit = 50, offset = 0, transactionType = null) => {
    const params = new URLSearchParams();
    params.append('limit', limit);
    params.append('offset', offset);
    if (transactionType) params.append('transaction_type', transactionType);

    const response = await apiClient.get(`/wallets/transactions?${params.toString()}`);
    return response.data;
  },

  deposit: async (amount, transactionHash = null, metadata = {}) => {
    const response = await apiClient.post('/wallets/deposit', {
      amount: String(amount),
      transaction_hash: transactionHash,
      metadata
    });
    return response.data;
  },

  withdraw: async (amount, destinationAddress = null, metadata = {}) => {
    const response = await apiClient.post('/wallets/withdraw', {
      amount: String(amount),
      destination_address: destinationAddress,
      metadata
    });
    return response.data;
  },

  getAnalytics: async (days = 30) => {
    const response = await apiClient.get(`/wallets/analytics?days=${days}`);
    return response.data;
  }
};

// ============================================
// PROVIDER API
// ============================================

export const providerAPI = {
  syncAll: async () => {
    const response = await apiClient.post('/providers/sync');
    return response.data;
  },

  syncProvider: async (providerName) => {
    const response = await apiClient.post(`/providers/sync/${providerName}`);
    return response.data;
  },

  getStatus: async () => {
    const response = await apiClient.get('/providers/status');
    return response.data;
  }
};

// ============================================
// HEALTH CHECK API
// ============================================

export const healthAPI = {
  check: async () => {
    const response = await axios.get(`${API_BASE_URL}/health`);
    return response.data;
  }
};

export default apiClient;
