// Medicines API service for FastAPI backend
import api from './api';
import type { AxiosResponse } from 'axios';

// Backend API types (match backend schemas)
export interface ApiMedicine {
  id: number;
  user_id: number;
  name: string;
  generic_name: string | null;
  dosage: string;
  form: string;
  unit: string;
  current_stock: number;
  min_stock_alert: number;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface ApiMedicineWithDetails extends ApiMedicine {
  is_low_stock: boolean;
  stock_level: string;
}

export interface MedicineCreate {
  name: string;
  generic_name?: string;
  dosage: string;
  form: string;
  unit: string;
  current_stock?: number;
  min_stock_alert?: number;
  notes?: string;
}

export interface MedicineUpdate {
  name?: string;
  generic_name?: string;
  dosage?: string;
  form?: string;
  unit?: string;
  current_stock?: number;
  min_stock_alert?: number;
  notes?: string;
}

export interface MedicineFilter {
  search?: string;
  form?: string;
  is_low_stock?: boolean;
  low_stock_only?: boolean;
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

export interface StockAdjustment {
  adjustment: number;
  reason?: string;
  notes?: string;
}

export interface InventoryHistory {
  id: number;
  medicine_id: number;
  change_type: string;
  quantity: number;
  previous_stock: number;
  new_stock: number;
  reason?: string;
  notes?: string;
  created_at: string;
}

export const medicinesApi = {
  // List medicines with pagination and filtering
  list: (params?: MedicineFilter): Promise<AxiosResponse<PaginatedResponse<ApiMedicine>>> =>
    api.get<PaginatedResponse<ApiMedicine>>('/medicines', { params }),

  // Get single medicine
  get: (id: number): Promise<AxiosResponse<ApiMedicineWithDetails>> =>
    api.get<ApiMedicineWithDetails>(`/medicines/${id}`),

  // Create medicine
  create: (data: MedicineCreate): Promise<AxiosResponse<ApiMedicine>> =>
    api.post<ApiMedicine>('/medicines', data),

  // Update medicine
  update: (id: number, data: MedicineUpdate): Promise<AxiosResponse<ApiMedicine>> =>
    api.put<ApiMedicine>(`/medicines/${id}`, data),

  // Delete medicine
  delete: (id: number): Promise<AxiosResponse<void>> =>
    api.delete<void>(`/medicines/${id}`),

  // Search medicines
  search: (q: string): Promise<AxiosResponse<ApiMedicine[]>> =>
    api.get<ApiMedicine[]>('/medicines/search', { params: { q } }),

  // Get low stock medicines
  getLowStock: (): Promise<AxiosResponse<ApiMedicine[]>> =>
    api.get<ApiMedicine[]>('/medicines/low-stock'),

  // Get medicines by form
  getByForm: (form: string): Promise<AxiosResponse<ApiMedicine[]>> =>
    api.get<ApiMedicine[]>(`/medicines/by-form/${form}`),

  // Get medicine statistics
  getStatistics: (): Promise<AxiosResponse<Record<string, unknown>>> =>
    api.get<Record<string, unknown>>('/medicines/statistics'),

  // Adjust stock
  adjustStock: (id: number, data: StockAdjustment): Promise<AxiosResponse<ApiMedicine>> =>
    api.post<ApiMedicine>(`/medicines/${id}/adjust-stock`, data),

  // Get inventory history
  getHistory: (id: number): Promise<AxiosResponse<InventoryHistory[]>> =>
    api.get<InventoryHistory[]>(`/medicines/${id}/history`),
};

export default medicinesApi;
