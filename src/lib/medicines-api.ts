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

// Medicine dropdown item for prescription form
export interface MedicineDropdownItem {
  id: number;
  name: string;
  dosage: string;
  form: string;
  unit: string;
}

// Missing medicine from prescriptions
export interface MissingMedicineItem {
  id: number;
  medicine_name: string;
  dosage: string;
  frequency: string;
  duration_days: number;
  instructions: string | null;
  prescriptions_count: number;
  prescription_id: number;
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
  change_amount: number;
  change_type: string;
  previous_stock: number;
  new_stock: number;
  reference_id?: number;
  notes?: string;
  created_at: string;
}

export interface InventoryHistoryWithMedicine extends InventoryHistory {
  medicine_name: string;
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

  // Adjust stock (uses query params as per backend API)
  adjustStock: (id: number, adjustment: number, reason?: string): Promise<AxiosResponse<ApiMedicine>> =>
    api.post<ApiMedicine>(`/medicines/${id}/adjust-stock`, null, { params: { adjustment, reason } }),

  // Get inventory history for a specific medicine
  getHistory: (id: number): Promise<AxiosResponse<InventoryHistory[]>> =>
    api.get<InventoryHistory[]>(`/medicines/${id}/history`),

  // Get all inventory history for user
  getAllInventoryHistory: (params?: {
    page?: number;
    per_page?: number;
    change_type?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<AxiosResponse<PaginatedResponse<InventoryHistoryWithMedicine>>> =>
    api.get<PaginatedResponse<InventoryHistoryWithMedicine>>('/medicines/inventory-history', { params }),

  // Get medicines for prescription dropdown
  getForPrescription: (search?: string): Promise<AxiosResponse<MedicineDropdownItem[]>> =>
    api.get<MedicineDropdownItem[]>('/medicines/for-prescription', { params: { search } }),

  // Get medicines missing from inventory (from prescriptions)
  getMissingFromInventory: (): Promise<AxiosResponse<MissingMedicineItem[]>> =>
    api.get<MissingMedicineItem[]>('/medicines/missing-from-inventory'),

  // Create medicine from prescription medicine
  addFromPrescription: (prescriptionMedicineId: number, data: MedicineCreate): Promise<AxiosResponse<ApiMedicine>> =>
    api.post<ApiMedicine>('/medicines/from-prescription', data, { params: { prescription_medicine_id: prescriptionMedicineId } }),
};

export default medicinesApi;
