// Users API service for FastAPI backend
import api from './api';
import type { AxiosResponse } from 'axios';
import { toUser, type ApiUser } from '@/types';
import { toDashboardStats, type DashboardStats, type ApiDashboardStats } from '@/types';

export interface UserStatsResponse extends ApiDashboardStats {
  upcoming_reminders: unknown[];
  low_stock_medicines: unknown[];
}

export const usersApi = {
  // Get current user profile
  getProfile: (): Promise<AxiosResponse<ApiUser>> =>
    api.get<ApiUser>('/users/profile'),

  // Update current user profile
  updateProfile: (data: Partial<{
    email: string;
    first_name: string;
    last_name: string;
    phone: string;
    date_of_birth: string;
  }>): Promise<AxiosResponse<ApiUser>> =>
    api.put<ApiUser>('/users/profile', data),

  // Delete current user account
  deleteAccount: (): Promise<AxiosResponse<void>> =>
    api.delete<void>('/users/account'),

  // Get user statistics
  getStats: (): Promise<AxiosResponse<UserStatsResponse>> =>
    api.get<UserStatsResponse>('/users/stats'),
};

// Helper function to get user stats and convert to frontend format
export async function fetchUserStats(): Promise<DashboardStats> {
  const response = await usersApi.getStats();
  return toDashboardStats(response.data);
}

// Helper function to get user profile and convert to frontend format
export async function fetchUserProfile() {
  const response = await usersApi.getProfile();
  return toUser(response.data);
}

export default usersApi;
