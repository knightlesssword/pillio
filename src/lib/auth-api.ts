// Auth API service for FastAPI backend
import api from './api';
import type { AxiosResponse } from 'axios';

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface ApiUser {
  id: number;
  email: string;
  first_name: string | null;
  last_name: string | null;
  phone: string | null;
  date_of_birth: string | null;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
  remember_me?: boolean;
}

export interface RegisterRequest {
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
  phone?: string;
  date_of_birth?: string;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirmRequest {
  token: string;
  new_password: string;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

export interface DeleteAccountRequest {
  password: string;
  reason?: string;
}

export const authApi = {
  login: (data: LoginRequest): Promise<AxiosResponse<LoginResponse>> =>
    api.post<LoginResponse>('/auth/login', data),

  register: (data: RegisterRequest): Promise<AxiosResponse<LoginResponse>> =>
    api.post<LoginResponse>('/auth/register', data),

  getMe: (): Promise<AxiosResponse<ApiUser>> =>
    api.get<ApiUser>('/auth/me'),

  updateProfile: (data: Partial<RegisterRequest>): Promise<AxiosResponse<ApiUser>> =>
    api.put<ApiUser>('/auth/me', data),

  changePassword: (data: ChangePasswordRequest): Promise<AxiosResponse<void>> =>
    api.post<void>('/auth/change-password', data),

  forgotPassword: (data: PasswordResetRequest): Promise<AxiosResponse<void>> =>
    api.post<void>('/auth/forgot-password', data),

  resetPassword: (data: PasswordResetConfirmRequest): Promise<AxiosResponse<void>> =>
    api.post<void>('/auth/reset-password', data),

  refreshToken: (refresh_token: string): Promise<AxiosResponse<LoginResponse>> =>
    api.post<LoginResponse>('/auth/refresh', { refresh_token }),

  logout: (): Promise<AxiosResponse<void>> =>
    api.post<void>('/auth/logout'),

  exportData: (): Promise<AxiosResponse<Blob>> =>
    api.get('/auth/export-data', { responseType: 'blob' }),

  deleteAccount: (data: DeleteAccountRequest): Promise<AxiosResponse<void>> =>
    api.post<void>('/auth/delete-account', data),
};

export default authApi;
