// User types
export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  phone?: string;
  createdAt: string;
  updatedAt: string;
}

// API-specific User type (matches backend response)
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

// Convert API user to frontend user
export function toUser(apiUser: ApiUser): User {
  return {
    id: String(apiUser.id),
    email: apiUser.email,
    name: [apiUser.first_name, apiUser.last_name]
      .filter(Boolean)
      .join(' ') || apiUser.email.split('@')[0],
    phone: apiUser.phone || undefined,
    createdAt: apiUser.created_at,
    updatedAt: apiUser.updated_at,
  };
}

// Medicine types
export interface Medicine {
  id: string;
  name: string;
  genericName?: string;
  category: string; // Maps to backend 'form'
  dosage: string;
  unit: string;
  description?: string;
  sideEffects?: string;
  instructions?: string;
  manufacturer?: string;
  currentStock: number;
  minimumStock: number;
  expiryDate?: string;
  imageUrl?: string;
  createdAt: string;
  updatedAt: string;
  isLowStock?: boolean;
}

// API-specific Medicine type (matches backend response)
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

// Convert API medicine to frontend medicine
export function toMedicine(apiMedicine: ApiMedicine): Medicine {
  return {
    id: String(apiMedicine.id),
    name: apiMedicine.name,
    genericName: apiMedicine.generic_name || undefined,
    category: apiMedicine.form,
    dosage: apiMedicine.dosage,
    unit: apiMedicine.unit,
    currentStock: apiMedicine.current_stock,
    minimumStock: apiMedicine.min_stock_alert,
    createdAt: apiMedicine.created_at,
    updatedAt: apiMedicine.updated_at,
  };
}

// Reminder types
export interface Reminder {
  id: string;
  medicineId: string;
  medicine?: Medicine;
  time: string;
  frequency: string;
  daysOfWeek?: string[];
  dosage: number;
  notes?: string;
  isActive: boolean;
  startDate: string;
  endDate?: string;
  createdAt: string;
  updatedAt: string;
}

// Reminder Log types
export interface ReminderLog {
  id: string;
  reminderId: string;
  reminder?: Reminder;
  scheduledTime: string;
  status: 'pending' | 'taken' | 'missed' | 'skipped' | 'snoozed';
  takenAt?: string;
  notes?: string;
  createdAt: string;
}

// Prescription types
export interface Prescription {
  id: string;
  doctorName: string;
  hospitalName?: string;
  prescriptionDate: string;
  expiryDate?: string;
  diagnosis?: string;
  notes?: string;
  images: string[];
  medicines: PrescriptionMedicine[];
  createdAt: string;
  updatedAt: string;
}

export interface PrescriptionMedicine {
  medicineId?: string;
  medicine?: Medicine;
  name: string;
  dosage: string;
  frequency: string;
  duration: string;
  instructions?: string;
}

// Inventory types
export interface InventoryAdjustment {
  id: string;
  medicineId: string;
  medicine?: Medicine;
  type: 'add' | 'remove' | 'adjust';
  quantity: number;
  previousStock: number;
  newStock: number;
  reason?: string;
  createdAt: string;
}

// API-specific InventoryHistory type
export interface ApiInventoryHistory {
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

// Convert API inventory history to frontend
export function toInventoryAdjustment(apiHistory: ApiInventoryHistory): InventoryAdjustment {
  const typeMap: Record<string, 'add' | 'remove' | 'adjust'> = {
    added: 'add',
    consumed: 'remove',
    adjusted: 'adjust',
    expired: 'remove',
  };

  return {
    id: String(apiHistory.id),
    medicineId: String(apiHistory.medicine_id),
    type: typeMap[apiHistory.change_type] || 'adjust',
    quantity: apiHistory.quantity,
    previousStock: apiHistory.previous_stock,
    newStock: apiHistory.new_stock,
    reason: apiHistory.reason || undefined,
    createdAt: apiHistory.created_at,
  };
}

// Notification types
export interface Notification {
  id: string;
  type: 'reminder' | 'low_stock' | 'prescription_expiry' | 'refill' | 'adherence' | 'system';
  title: string;
  message: string;
  isRead: boolean;
  actionUrl?: string;
  createdAt: string;
}

// Stats types
export interface DashboardStats {
  totalMedicines: number;
  todayReminders: number;
  completedToday: number;
  lowStockCount: number;
  adherenceRate: number;
  upcomingReminders: Reminder[];
  lowStockMedicines: Medicine[];
}

// API-specific DashboardStats type
export interface ApiDashboardStats {
  total_medicines: number;
  today_reminders: number;
  completed_today: number;
  low_stock_count: number;
  adherence_rate: number;
}

// Convert API stats to frontend
export function toDashboardStats(apiStats: ApiDashboardStats): DashboardStats {
  return {
    totalMedicines: apiStats.total_medicines,
    todayReminders: apiStats.today_reminders,
    completedToday: apiStats.completed_today,
    lowStockCount: apiStats.low_stock_count,
    adherenceRate: apiStats.adherence_rate,
    upcomingReminders: [],
    lowStockMedicines: [],
  };
}

// Report types
export interface AdherenceReport {
  period: string;
  totalScheduled: number;
  taken: number;
  missed: number;
  skipped: number;
  adherenceRate: number;
}

export interface ConsumptionReport {
  medicineId: string;
  medicineName: string;
  period: string;
  totalConsumed: number;
  unit: string;
}

// Form types
export interface LoginForm {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface RegisterForm {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export interface MedicineForm {
  name: string;
  genericName?: string;
  category: string;
  dosage: string;
  unit: string;
  description?: string;
  sideEffects?: string;
  instructions?: string;
  manufacturer?: string;
  currentStock: number;
  minimumStock: number;
  expiryDate?: string;
}

export interface ReminderForm {
  medicineId: string;
  time: string;
  frequency: string;
  daysOfWeek?: string[];
  dosage: number;
  notes?: string;
  isActive: boolean;
  startDate: string;
  endDate?: string;
}

export interface PrescriptionForm {
  doctorName: string;
  hospitalName?: string;
  prescriptionDate: string;
  expiryDate?: string;
  diagnosis?: string;
  notes?: string;
  images: File[];
  medicines: PrescriptionMedicine[];
}
