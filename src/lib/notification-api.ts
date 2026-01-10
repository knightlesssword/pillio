import api from './api';
import type { Notification } from '@/types';

// API notification type (matches backend response with snake_case)
interface ApiNotification {
  id: number;
  user_id: number;
  type: string;
  title: string;
  message: string;
  is_read: boolean;
  action_url: string | null;
  reference_type: string | null;
  reference_id: number | null;
  created_at: string;
  read_at: string | null;
}

// Convert API notification to frontend notification
function toNotification(apiNotification: ApiNotification): Notification {
  return {
    id: String(apiNotification.id),
    type: apiNotification.type as Notification['type'],
    title: apiNotification.title,
    message: apiNotification.message,
    isRead: apiNotification.is_read,
    actionUrl: apiNotification.action_url || undefined,
    createdAt: apiNotification.created_at,
  };
}

// API response types (internal, uses snake_case)
interface RawNotificationListResponse {
  items: ApiNotification[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

// Transformed response type (uses camelCase)
interface NotificationListResponse {
  items: Notification[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

interface NotificationCountResponse {
  total: number;
  unread: number;
  by_type: Record<string, number>;
}

interface ActionResponse {
  message: string;
  count?: number;
}

interface NotificationFilters {
  type?: string;
  is_read?: boolean;
  reference_type?: string;
  page?: number;
  per_page?: number;
}

export const notificationApi = {
  // Get all notifications with optional filters
  async getNotifications(filters?: NotificationFilters): Promise<NotificationListResponse> {
    const params = new URLSearchParams();
    if (filters?.type) params.append('type', filters.type);
    if (filters?.is_read !== undefined) params.append('is_read', String(filters.is_read));
    if (filters?.reference_type) params.append('reference_type', filters.reference_type);
    if (filters?.page) params.append('page', String(filters.page));
    if (filters?.per_page) params.append('per_page', String(filters.per_page));

    const response = await api.get<RawNotificationListResponse>(`/notifications?${params.toString()}`);
    // Transform API response to frontend format
    return {
      total: response.data.total,
      page: response.data.page,
      per_page: response.data.per_page,
      pages: response.data.pages,
      items: response.data.items.map(toNotification),
    };
  },

  // Get notification counts
  async getNotificationCounts(): Promise<NotificationCountResponse> {
    const response = await api.get<NotificationCountResponse>('/notifications/counts');
    return response.data;
  },

  // Get single notification
  async getNotification(id: number): Promise<Notification> {
    const response = await api.get<ApiNotification>(`/notifications/${id}`);
    return toNotification(response.data);
  },

  // Mark notification as read
  async markAsRead(id: number): Promise<Notification> {
    const response = await api.put<ApiNotification>(`/notifications/${id}/read`);
    return toNotification(response.data);
  },

  // Mark all notifications as read
  async markAllAsRead(): Promise<ActionResponse> {
    const response = await api.put<ActionResponse>('/notifications/read-all');
    return response.data;
  },

  // Mark notification as taken (✓ tick action)
  async markAsTaken(id: number): Promise<Notification> {
    const response = await api.put<ApiNotification>(`/notifications/${id}/taken`);
    return toNotification(response.data);
  },

  // Mark notification as skipped (✗ cross action)
  async markAsSkipped(id: number): Promise<Notification> {
    const response = await api.put<ApiNotification>(`/notifications/${id}/skipped`);
    return toNotification(response.data);
  },

  // Delete single notification
  async deleteNotification(id: number): Promise<ActionResponse> {
    const response = await api.delete<ActionResponse>(`/notifications/${id}`);
    return response.data;
  },

  // Clear all notifications
  async clearAll(): Promise<ActionResponse> {
    const response = await api.delete<ActionResponse>('/notifications');
    return response.data;
  },

  // Cleanup old notifications
  async cleanupOldNotifications(daysOld: number = 30): Promise<ActionResponse> {
    const response = await api.delete<ActionResponse>(`/notifications/cleanup?days_old=${daysOld}`);
    return response.data;
  },
};

export default notificationApi;
