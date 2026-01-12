// API Client wrapper using Axios for FastAPI backend
import axios, { AxiosError, type AxiosRequestConfig } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Helper functions for token storage
const getToken = (storageType: 'local' | 'session') => 
  (storageType === 'local' ? localStorage : sessionStorage).getItem('auth_token');

const getRefreshToken = (storageType: 'local' | 'session') => 
  (storageType === 'local' ? localStorage : sessionStorage).getItem('refresh_token');

const setTokens = (storageType: 'local' | 'session', accessToken: string, refreshToken: string) => {
  const storage = storageType === 'local' ? localStorage : sessionStorage;
  storage.setItem('auth_token', accessToken);
  storage.setItem('refresh_token', refreshToken);
};

const clearTokens = (storageType: 'local' | 'session') => {
  const storage = storageType === 'local' ? localStorage : sessionStorage;
  storage.removeItem('auth_token');
  storage.removeItem('refresh_token');
  storage.removeItem('user');
};

// Check which storage has valid auth data
const getAuthStorageType = (): 'local' | 'session' | null => {
  if (localStorage.getItem('auth_token')) return 'local';
  if (sessionStorage.getItem('auth_token')) return 'session';
  return null;
};

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const storageType = getAuthStorageType();
    const token = storageType ? getToken(storageType) : null;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling and token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

    // Handle 401 Unauthorized - try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const storageType = getAuthStorageType();
      const refreshToken = storageType ? getRefreshToken(storageType) : null;
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token } = response.data;
          if (storageType) {
            setTokens(storageType, access_token, refresh_token);
          }

          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
          }
          return api(originalRequest);
        } catch (refreshError) {
          // Refresh failed - clear tokens and redirect to login
          if (storageType) {
            clearTokens(storageType);
          }
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      }
    }

    return Promise.reject(error);
  }
);

// Helper to get error message
export const getErrorMessage = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    return (error.response?.data as { detail?: string })?.detail || error.message || 'An error occurred';
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'An unknown error occurred';
};

export default api;
