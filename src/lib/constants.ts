// App Constants
export const APP_NAME = 'Pillio';
export const APP_VERSION = '1.0.0';

// Medicine Categories
export const MEDICINE_CATEGORIES = [
  'Tablets',
  'Capsules',
  'Syrups',
  'Injections',
  'Drops',
  'Creams',
  'Inhalers',
  'Patches',
  'Powders',
  'Other',
] as const;

// Medicine Units
export const MEDICINE_UNITS = [
  'tablets',
  'capsules',
  'ml',
  'mg',
  'drops',
  'puffs',
  'patches',
  'sachets',
] as const;

// Frequency Options
export const FREQUENCY_OPTIONS = [
  { value: 'once_daily', label: 'Once Daily' },
  { value: 'twice_daily', label: 'Twice Daily' },
  { value: 'three_times_daily', label: 'Three Times Daily' },
  { value: 'four_times_daily', label: 'Four Times Daily' },
  { value: 'every_other_day', label: 'Every Other Day' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'as_needed', label: 'As Needed' },
  { value: 'custom', label: 'Custom' },
] as const;

// Days of Week
export const DAYS_OF_WEEK = [
  { value: 'monday', label: 'Mon', fullLabel: 'Monday' },
  { value: 'tuesday', label: 'Tue', fullLabel: 'Tuesday' },
  { value: 'wednesday', label: 'Wed', fullLabel: 'Wednesday' },
  { value: 'thursday', label: 'Thu', fullLabel: 'Thursday' },
  { value: 'friday', label: 'Fri', fullLabel: 'Friday' },
  { value: 'saturday', label: 'Sat', fullLabel: 'Saturday' },
  { value: 'sunday', label: 'Sun', fullLabel: 'Sunday' },
] as const;

// Reminder Status
export const REMINDER_STATUS = {
  PENDING: 'pending',
  TAKEN: 'taken',
  MISSED: 'missed',
  SKIPPED: 'skipped',
  SNOOZED: 'snoozed',
} as const;

// Stock Levels
export const STOCK_LEVELS = {
  CRITICAL: 5,
  LOW: 15,
  MEDIUM: 30,
  HIGH: 50,
} as const;

// Notification Types
export const NOTIFICATION_TYPES = {
  REMINDER: 'reminder',
  LOW_STOCK: 'low_stock',
  PRESCRIPTION_EXPIRY: 'prescription_expiry',
  REFILL: 'refill',
  SYSTEM: 'system',
} as const;

// Routes
export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  FORGOT_PASSWORD: '/forgot-password',
  DASHBOARD: '/dashboard',
  MEDICINES: '/medicines',
  REMINDERS: '/reminders',
  PRESCRIPTIONS: '/prescriptions',
  INVENTORY: '/inventory',
  HISTORY: '/history',
  REPORTS: '/reports',
  SETTINGS: '/settings',
} as const;

// API Endpoints
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
    FORGOT_PASSWORD: '/auth/forgot-password',
    RESET_PASSWORD: '/auth/reset-password',
  },
  MEDICINES: '/medicines',
  REMINDERS: '/reminders',
  PRESCRIPTIONS: '/prescriptions',
  INVENTORY: '/inventory',
  HISTORY: '/history',
  REPORTS: '/reports',
  NOTIFICATIONS: '/notifications',
  USERS: '/users',
} as const;

// Time Slots for Reminders
export const TIME_SLOTS = [
  { value: 'morning', label: 'Morning', icon: '🌅', defaultTime: '08:00' },
  { value: 'afternoon', label: 'Afternoon', icon: '☀️', defaultTime: '13:00' },
  { value: 'evening', label: 'Evening', icon: '🌆', defaultTime: '18:00' },
  { value: 'night', label: 'Night', icon: '🌙', defaultTime: '21:00' },
] as const;

// Chart Colors
export const CHART_COLORS = {
  primary: 'hsl(173, 58%, 39%)',
  secondary: 'hsl(200, 20%, 95%)',
  accent: 'hsl(15, 85%, 60%)',
  success: 'hsl(158, 64%, 42%)',
  warning: 'hsl(38, 92%, 50%)',
  info: 'hsl(199, 89%, 48%)',
  muted: 'hsl(200, 15%, 45%)',
} as const;
