// Prescriptions API service for FastAPI backend
import api from './api';
import type { AxiosResponse } from 'axios';

// Prescription medicine item (for creating/updating)
export interface PrescriptionMedicineCreate {
  id?: number;
  medicine_id?: number;
  medicine_name: string;
  dosage: string;
  frequency: string;
  duration_days: number;
  instructions?: string;
}

// Prescription medicine item (in response)
export interface PrescriptionMedicineResponse {
  id: number;
  prescription_id: number;
  medicine_id: number | null;
  medicine_name: string;
  dosage: string;
  frequency: string;
  duration_days: number;
  instructions: string | null;
}

// Base prescription (without medicines)
export interface Prescription {
  id: number;
  user_id: number;
  doctor_name: string;
  hospital_clinic: string | null;
  prescription_date: string;
  valid_until: string | null;
  notes: string | null;
  image_url: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Full prescription with medicines and computed fields
export interface PrescriptionWithMedicines extends Prescription {
  prescription_medicines: PrescriptionMedicineResponse[];
  is_expired: boolean;
  days_until_expiry: number;
}

// Prescription creation data
export interface PrescriptionCreate {
  doctor_name: string;
  hospital_clinic?: string;
  prescription_date: string;
  valid_until?: string;
  notes?: string;
  is_active?: boolean;
  medicines: PrescriptionMedicineCreate[];
}

// Prescription update data
export interface PrescriptionUpdate {
  doctor_name?: string;
  hospital_clinic?: string;
  prescription_date?: string;
  valid_until?: string;
  notes?: string;
  is_active?: boolean;
}

// Prescription filter
export interface PrescriptionFilter {
  is_active?: boolean;
  is_expired?: boolean;
  doctor_name?: string;
  search?: string;
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

export const prescriptionsApi = {
  // List prescriptions with pagination and filtering
  list: (params?: PrescriptionFilter): Promise<AxiosResponse<PaginatedResponse<PrescriptionWithMedicines>>> =>
    api.get<PaginatedResponse<PrescriptionWithMedicines>>('/prescriptions', { params }),

  // Get single prescription
  get: (id: number): Promise<AxiosResponse<PrescriptionWithMedicines>> =>
    api.get<PrescriptionWithMedicines>(`/prescriptions/${id}`),

  // Create prescription
  create: (data: PrescriptionCreate): Promise<AxiosResponse<PrescriptionWithMedicines>> =>
    api.post<PrescriptionWithMedicines>('/prescriptions', data),

  // Update prescription
  update: (id: number, data: PrescriptionUpdate): Promise<AxiosResponse<PrescriptionWithMedicines>> =>
    api.put<PrescriptionWithMedicines>(`/prescriptions/${id}`, data),

  // Delete prescription
  delete: (id: number): Promise<AxiosResponse<void>> =>
    api.delete<void>(`/prescriptions/${id}`),

  // Get expiring prescriptions
  getExpiring: (daysAhead?: number): Promise<AxiosResponse<PrescriptionWithMedicines[]>> =>
    api.get<PrescriptionWithMedicines[]>('/prescriptions/expiring', { params: { days_ahead: daysAhead } }),

  // Get expired prescriptions
  getExpired: (): Promise<AxiosResponse<PrescriptionWithMedicines[]>> =>
    api.get<PrescriptionWithMedicines[]>('/prescriptions/expired'),

  // Add medicine to prescription
  addMedicine: (prescriptionId: number, medicine: PrescriptionMedicineCreate): Promise<AxiosResponse<PrescriptionMedicineResponse>> =>
    api.post<PrescriptionMedicineResponse>(`/prescriptions/${prescriptionId}/medicines`, medicine),

  // Remove medicine from prescription
  removeMedicine: (prescriptionId: number, prescriptionMedicineId: number): Promise<AxiosResponse<void>> =>
    api.delete<void>(`/prescriptions/${prescriptionId}/medicines/${prescriptionMedicineId}`),
};

export default prescriptionsApi;
