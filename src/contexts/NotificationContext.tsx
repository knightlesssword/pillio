import React, { useContext, useState, ReactNode, useCallback, useEffect } from 'react';
import { NotificationContext, type NotificationContextType } from './notification-context';
import { Notification } from '@/types';
import { notificationApi } from '@/lib/notification-api';
import { useAuth } from '@/contexts/AuthContext';

// eslint-disable-next-line react-refresh/only-export-components
export function useNotifications(): NotificationContextType {
  const context = useContext(NotificationContext);
  if (context === undefined) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
}

export function NotificationProvider({ children }: { children: ReactNode }) {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const unreadCount = notifications.filter(n => !n.isRead).length;

  // Fetch notifications from API
  const refresh = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await notificationApi.getNotifications({ per_page: 100 });
      setNotifications(response.items);
    } catch (err) {
      console.error('Failed to fetch notifications:', err);
      // Keep notifications empty on error - no fallback data
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Load notifications on mount (only if authenticated)
  useEffect(() => {
    // Only fetch notifications when user is authenticated and auth check is complete
    if (isAuthenticated && !authLoading) {
      refresh();
    }
  }, [refresh, isAuthenticated, authLoading]);

  const addNotification = useCallback((notification: Omit<Notification, 'id' | 'createdAt' | 'isRead'>) => {
    // Optimistically add to local state
    const newNotification: Notification = {
      ...notification,
      id: String(Date.now()),
      isRead: false,
      createdAt: new Date().toISOString(),
    };
    setNotifications(prev => [newNotification, ...prev]);
  }, []);

  const markAsRead = useCallback(async (id: string) => {
    // Optimistically update local state
    setNotifications(prev =>
      prev.map(n => (n.id === id ? { ...n, isRead: true } : n))
    );
    
    // Sync with API
    try {
      await notificationApi.markAsRead(Number(id));
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  }, []);

  const markAllAsRead = useCallback(async () => {
    // Optimistically update local state
    setNotifications(prev => prev.map(n => ({ ...n, isRead: true })));
    
    // Sync with API
    try {
      await notificationApi.markAllAsRead();
    } catch (error) {
      console.error('Failed to mark all notifications as read:', error);
    }
  }, []);

  const removeNotification = useCallback(async (id: string) => {
    // Optimistically remove from local state
    setNotifications(prev => prev.filter(n => n.id !== id));
    
    // Sync with API
    try {
      await notificationApi.deleteNotification(Number(id));
    } catch (error) {
      console.error('Failed to delete notification:', error);
    }
  }, []);

  const clearAll = useCallback(async () => {
    // Optimistically clear local state
    setNotifications([]);
    
    // Sync with API
    try {
      await notificationApi.clearAll();
    } catch (error) {
      console.error('Failed to clear all notifications:', error);
    }
  }, []);

  const markAsTaken = useCallback(async (id: string) => {
    // Optimistically update local state
    setNotifications(prev =>
      prev.map(n => (n.id === id ? { ...n, isRead: true } : n))
    );
    
    // Sync with API
    try {
      await notificationApi.markAsTaken(Number(id));
    } catch (error) {
      console.error('Failed to mark notification as taken:', error);
    }
  }, []);

  const markAsSkipped = useCallback(async (id: string) => {
    // Optimistically update local state
    setNotifications(prev =>
      prev.map(n => (n.id === id ? { ...n, isRead: true } : n))
    );
    
    // Sync with API
    try {
      await notificationApi.markAsSkipped(Number(id));
    } catch (error) {
      console.error('Failed to mark notification as skipped:', error);
    }
  }, []);

  return (
    <NotificationContext.Provider
      value={{
        notifications,
        unreadCount,
        isLoading,
        addNotification,
        markAsRead,
        markAllAsRead,
        removeNotification,
        clearAll,
        refresh,
        markAsTaken,
        markAsSkipped,
      }}
    >
      {children}
    </NotificationContext.Provider>
  );
}
