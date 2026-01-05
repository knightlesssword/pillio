import React, { createContext, useContext, useState, ReactNode, useCallback } from 'react';
import { Notification } from '@/types';
import { generateId } from '@/lib/utils';

interface NotificationContextType {
  notifications: Notification[];
  unreadCount: number;
  addNotification: (notification: Omit<Notification, 'id' | 'createdAt' | 'isRead'>) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  removeNotification: (id: string) => void;
  clearAll: () => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

// Mock initial notifications for demo
const mockNotifications: Notification[] = [
  {
    id: '1',
    type: 'reminder',
    title: 'Time to take your medicine',
    message: 'Aspirin 100mg - 1 tablet',
    isRead: false,
    createdAt: new Date().toISOString(),
  },
  {
    id: '2',
    type: 'low_stock',
    title: 'Low stock alert',
    message: 'Vitamin D is running low (5 tablets left)',
    isRead: false,
    actionUrl: '/inventory',
    createdAt: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    id: '3',
    type: 'prescription_expiry',
    title: 'Prescription expiring soon',
    message: 'Your prescription from Dr. Smith expires in 7 days',
    isRead: true,
    actionUrl: '/prescriptions',
    createdAt: new Date(Date.now() - 86400000).toISOString(),
  },
];

export function NotificationProvider({ children }: { children: ReactNode }) {
  const [notifications, setNotifications] = useState<Notification[]>(mockNotifications);

  const unreadCount = notifications.filter(n => !n.isRead).length;

  const addNotification = useCallback((notification: Omit<Notification, 'id' | 'createdAt' | 'isRead'>) => {
    const newNotification: Notification = {
      ...notification,
      id: generateId(),
      isRead: false,
      createdAt: new Date().toISOString(),
    };
    setNotifications(prev => [newNotification, ...prev]);
  }, []);

  const markAsRead = useCallback((id: string) => {
    setNotifications(prev =>
      prev.map(n => (n.id === id ? { ...n, isRead: true } : n))
    );
  }, []);

  const markAllAsRead = useCallback(() => {
    setNotifications(prev => prev.map(n => ({ ...n, isRead: true })));
  }, []);

  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  }, []);

  const clearAll = useCallback(() => {
    setNotifications([]);
  }, []);

  return (
    <NotificationContext.Provider
      value={{
        notifications,
        unreadCount,
        addNotification,
        markAsRead,
        markAllAsRead,
        removeNotification,
        clearAll,
      }}
    >
      {children}
    </NotificationContext.Provider>
  );
}

export function useNotifications() {
  const context = useContext(NotificationContext);
  if (context === undefined) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
}
