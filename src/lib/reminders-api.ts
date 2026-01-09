// Reminders API service for FastAPI backend
import api from './api';
import type { AxiosResponse } from 'axios';

// Backend API types (match backend schemas)
export interface ApiReminder {
  id: number;
  user_id: number;
  medicine_id: number;
  prescription_id: number | null;
  reminder_time: string; // Time string "HH:MM:SS"
  frequency: string; // "daily", "specific_days", "interval"
  specific_days: number[] | null;
  interval_days: number | null; // For interval frequency
  dosage_amount: string | null;
  dosage_unit: string | null;
  start_date: string; // Date string "YYYY-MM-DD"
  end_date: string | null;
  is_active: boolean;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface ApiReminderWithMedicine extends ApiReminder {
  medicine: {
    id: number;
    name: string;
    generic_name: string | null;
    dosage: string;
    form: string;
    unit: string;
  };
}

export interface ReminderWithStatus {
  id: number;
  medicineName: string;
  dosage: string;
  time: string; // ISO datetime string
  status: 'taken' | 'skipped' | 'missed' | 'upcoming' | 'pending';
  is_pending: boolean;
  reminder: ApiReminderWithMedicine;
}

export interface ReminderCreate {
  medicine_id: number;
  prescription_id?: number;
  reminder_time: string; // Time string "HH:MM:SS"
  frequency: 'daily' | 'specific_days' | 'interval';
  specific_days?: number[]; // [0-6] for days of week
  interval_days?: number; // For interval frequency
  dosage_amount?: string;
  dosage_unit?: string;
  start_date: string; // Date string "YYYY-MM-DD"
  end_date?: string;
  is_active?: boolean;
  notes?: string;
}

export interface ReminderUpdate {
  reminder_time?: string;
  frequency?: 'daily' | 'specific_days' | 'interval';
  specific_days?: number[];
  interval_days?: number; // For interval frequency
  dosage_amount?: string;
  dosage_unit?: string;
  start_date?: string;
  end_date?: string;
  is_active?: boolean;
  notes?: string;
}

export interface ReminderFilter {
  is_active?: boolean;
  medicine_id?: number;
  page?: number;
  per_page?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export interface ReminderLog {
  id: number;
  reminder_id: number;
  scheduled_time: string;
  taken_time: string | null;
  status: 'taken' | 'skipped' | 'missed';
  notes: string | null;
  created_at: string;
}

export interface AdherenceStats {
  total_scheduled: number;
  taken: number;
  skipped: number;
  missed: number;
  adherence_rate: number;
}

export interface ReminderHistoryItem {
  id: number;
  medicine_name: string;
  dosage: string;
  scheduled_time: string | null;
  taken_time: string | null;
  status: 'taken' | 'skipped' | 'missed';
  notes: string | null;
}

export interface ReminderHistoryParams {
  start_date: string;
  end_date: string;
  reminder_status?: string;
  medicine_id?: number;
  page?: number;
  per_page?: number;
}

export interface ReminderHistoryResponse {
  items: ReminderHistoryItem[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export const remindersApi = {
  // Create a new reminder
  create: (data: ReminderCreate): Promise<AxiosResponse<ApiReminder>> =>
    api.post<ApiReminder>('/reminders', data),

  // List reminders with pagination and filtering
  list: (params?: ReminderFilter): Promise<AxiosResponse<PaginatedResponse<ApiReminderWithMedicine>>> =>
    api.get<PaginatedResponse<ApiReminderWithMedicine>>('/reminders', { params }),

  // Get today's reminders
  getToday: (): Promise<AxiosResponse<ApiReminderWithMedicine[]>> =>
    api.get<ApiReminderWithMedicine[]>('/reminders/today'),

  // Get today's reminders with their status
  getTodayWithStatus: (): Promise<AxiosResponse<ReminderWithStatus[]>> =>
    api.get<ReminderWithStatus[]>('/reminders/today-with-status'),

  // Get single reminder
  get: (id: number): Promise<AxiosResponse<ApiReminderWithMedicine>> =>
    api.get<ApiReminderWithMedicine>(`/reminders/${id}`),

  // Update reminder
  update: (id: number, data: ReminderUpdate): Promise<AxiosResponse<ApiReminder>> =>
    api.put<ApiReminder>(`/reminders/${id}`, data),

  // Delete reminder
  delete: (id: number): Promise<AxiosResponse<void>> =>
    api.delete<void>(`/reminders/${id}`),

  // Mark reminder as taken
  markTaken: (id: number, notes?: string): Promise<AxiosResponse<ReminderLog>> =>
    api.post<ReminderLog>(`/reminders/${id}/take`, { notes }),

  // Mark reminder as skipped
  markSkipped: (id: number, notes?: string): Promise<AxiosResponse<ReminderLog>> =>
    api.post<ReminderLog>(`/reminders/${id}/skip`, { notes }),

  // Get adherence statistics
  getAdherenceStats: (startDate: string, endDate: string): Promise<AxiosResponse<AdherenceStats>> =>
    api.get<AdherenceStats>('/reminders/adherence/stats', { params: { start_date: startDate, end_date: endDate } }),

  // Get reminder history
  getHistory: (params: ReminderHistoryParams): Promise<AxiosResponse<ReminderHistoryResponse>> =>
    api.get<ReminderHistoryResponse>('/reminders/history', { params }),

  // Mark overdue reminders as missed
  markMissed: (): Promise<AxiosResponse<{ message: string; count: number }>> =>
    api.post<{ message: string; count: number }>('/reminders/mark-missed'),
};

export default remindersApi;
