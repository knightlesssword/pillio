import React from 'react';
import { Link } from 'react-router-dom';
import { Bell, Check, X, Trash2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { useNotifications } from '@/contexts/NotificationContext';
import { cn, getRelativeDate } from '@/lib/utils';
import { Notification } from '@/types';

const notificationIcons: Record<string, string> = {
  reminder: '💊',
  low_stock: '📦',
  prescription_expiry: '📋',
  refill: '🔄',
  system: '⚙️',
};

function NotificationItem({
  notification,
  onMarkAsRead,
  onRemove,
}: {
  notification: Notification;
  onMarkAsRead: (id: string) => void;
  onRemove: (id: string) => void;
}) {
  const content = (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, x: 20 }}
      className={cn(
        'flex items-start gap-3 p-3 rounded-lg transition-colors',
        !notification.isRead ? 'bg-primary/5' : 'hover:bg-muted/50'
      )}
    >
      <span className="text-xl">{notificationIcons[notification.type] || '📌'}</span>
      <div className="flex-1 min-w-0">
        <p className={cn('text-sm', !notification.isRead && 'font-medium')}>
          {notification.title}
        </p>
        <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">
          {notification.message}
        </p>
        <p className="text-xs text-muted-foreground mt-1">
          {getRelativeDate(notification.createdAt)}
        </p>
      </div>
      <div className="flex items-center gap-1">
        {!notification.isRead && (
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6"
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              onMarkAsRead(notification.id);
            }}
          >
            <Check className="h-3 w-3" />
          </Button>
        )}
        <Button
          variant="ghost"
          size="icon"
          className="h-6 w-6 text-muted-foreground hover:text-destructive"
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            onRemove(notification.id);
          }}
        >
          <X className="h-3 w-3" />
        </Button>
      </div>
    </motion.div>
  );

  if (notification.actionUrl) {
    return (
      <Link to={notification.actionUrl} className="block">
        {content}
      </Link>
    );
  }

  return content;
}

export default function NotificationBell() {
  const { notifications, unreadCount, markAsRead, markAllAsRead, removeNotification, clearAll } =
    useNotifications();

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <Badge
              variant="destructive"
              className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 text-xs"
            >
              {unreadCount > 9 ? '9+' : unreadCount}
            </Badge>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80 p-0" align="end">
        <div className="flex items-center justify-between p-4 border-b">
          <h3 className="font-semibold">Notifications</h3>
          {notifications.length > 0 && (
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                className="text-xs h-7"
                onClick={markAllAsRead}
              >
                Mark all read
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7 text-muted-foreground hover:text-destructive"
                onClick={clearAll}
              >
                <Trash2 className="h-3.5 w-3.5" />
              </Button>
            </div>
          )}
        </div>
        <ScrollArea className="h-[300px]">
          {notifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full py-8 text-center">
              <Bell className="h-10 w-10 text-muted-foreground/50 mb-3" />
              <p className="text-sm text-muted-foreground">No notifications</p>
            </div>
          ) : (
            <div className="p-2 space-y-1">
              <AnimatePresence>
                {notifications.map((notification) => (
                  <NotificationItem
                    key={notification.id}
                    notification={notification}
                    onMarkAsRead={markAsRead}
                    onRemove={removeNotification}
                  />
                ))}
              </AnimatePresence>
            </div>
          )}
        </ScrollArea>
      </PopoverContent>
    </Popover>
  );
}
