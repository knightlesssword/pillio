import { createContext } from 'react';
import { Notification } from '@/types';

export interface NotificationContextType {
  notifications: Notification[];
  unreadCount: number;
  isLoading: boolean;
  // Basic operations
  addNotification: (notification: Omit<Notification, 'id' | 'createdAt' | 'isRead'>) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  removeNotification: (id: string) => void;
  clearAll: () => void;
  refresh: () => Promise<void>;
  // Tick/Cross action methods
  markAsTaken: (id: string) => Promise<void>;
  markAsSkipped: (id: string) => Promise<void>;
}

export const NotificationContext = createContext<NotificationContextType | undefined>(undefined);
