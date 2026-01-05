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

// Medicine types
export interface Medicine {
  id: string;
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
  imageUrl?: string;
  createdAt: string;
  updatedAt: string;
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

// Notification types
export interface Notification {
  id: string;
  type: 'reminder' | 'low_stock' | 'prescription_expiry' | 'refill' | 'system';
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
