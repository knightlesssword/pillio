# Notifications Implementation Plan

## Overview

This document outlines the comprehensive plan for implementing the notifications section in Pillio. The plan covers all possible notification types, their difficulty levels, and the implementation strategy.

---

## Current State Analysis

### Existing Infrastructure
- **Backend:**
  - [`pillio-backend/app/models/notification.py`](pillio-backend/app/models/notification.py) - Notification model exists
  - [`pillio-backend/app/schemas/notification.py`](pillio-backend/app/schemas/notification.py) - Notification schemas exist
  - [`pillio-backend/app/schemas/common.py`](pillio-backend/app/schemas/common.py) - NotificationType enum defined
  - **Missing:** API endpoints for notifications

- **Frontend:**
  - [`src/components/notifications/NotificationBell.tsx`](src/components/notifications/NotificationBell.tsx) - Notification bell UI exists
  - [`src/contexts/NotificationContext.tsx`](src/contexts/NotificationContext.tsx) - Uses mock data (no API integration)
  - [`src/types/index.ts`](src/types/index.ts) - Notification type defined
  - **Missing:** API integration, dedicated notifications page, tick/cross action handling

---

## Notification Types Overview

### 1. Medicine Reminder Notifications 💊
| Sub-type | Description | Difficulty |
|----------|-------------|------------|
| Time to take medicine | Remind user to take scheduled medicine | Easy |
| Missed medicine | Alert when a medicine was not taken | Medium |
| Medicine taken confirmation | Confirm successful medicine intake | Easy |

### 2. Inventory/Low Stock Notifications 📦
| Sub-type | Description | Difficulty |
|----------|-------------|------------|
| Low stock alert | Medicine running low (configurable threshold) | Easy |
| Critical stock alert | Medicine at critical level | Easy |
| Out of stock alert | Medicine completely out of stock | Easy |
| Refill suggestion | Suggest refilling based on usage rate | Medium |

### 3. Prescription Notifications 📋
| Sub-type | Description | Difficulty |
|----------|-------------|------------|
| Prescription expiring soon | Alert before prescription expires | Medium |
| Prescription expired | Alert after prescription expires | Easy |
| Prescription needs renewal | Suggest renewing expiring prescription | Medium |

### 4. System Notifications ⚙️
| Sub-type | Description | Difficulty |
|----------|-------------|------------|
| App updates | New features or maintenance notices | Easy |
| Backup completed | Data backup status | Easy |
| Security alerts | Account security notifications | Easy |

### 5. Adherence & Health Insights 📊
| Sub-type | Description | Difficulty |
|----------|-------------|------------|
| Adherence streak | Celebrate medication adherence streaks | Medium |
| Adherence drop | Alert when adherence rate drops | Medium |
| Health tips | Personalized health recommendations | Hard |

---

## Detailed Notification Implementation Plan

### Phase 1: Foundation (API & Backend) - Medium Difficulty

#### 1.1 Create Notification API Endpoints
**File:** `pillio-backend/app/api/notifications.py` (new)

```python
# Endpoints to implement:
- GET /notifications - List user notifications
- GET /notifications/{id} - Get single notification
- PUT /notifications/{id}/read - Mark as read
- PUT /notifications/read-all - Mark all as read
- DELETE /notifications/{id} - Delete notification
- DELETE /notifications - Clear all notifications
- GET /notifications/count - Get notification counts
```

**Related Files:**
- [`pillio-backend/app/main.py`](pillio-backend/app/main.py) - Add notification router

#### 1.2 Create Notification Service
**File:** `pillio-backend/app/services/notification_service.py` (new)

**Methods:**
- `create_notification()` - Create notification for user
- `get_user_notifications()` - Fetch notifications with pagination
- `mark_as_read()` - Mark single notification read
- `mark_all_as_read()` - Mark all notifications read
- `delete_notification()` - Remove notification
- `get_notification_counts()` - Get counts by type
- `cleanup_old_notifications()` - Remove notifications older than N days

#### 1.3 Update Notification Model (Optional)
**File:** [`pillio-backend/app/models/notification.py`](pillio-backend/app/models/notification.py)

Add fields if needed:
- `action_taken` - Boolean for tick/cross action
- `action_type` - 'taken', 'skipped', 'snoozed'
- `expires_at` - Notification expiration

---

### Phase 2: Frontend API Integration - Easy Difficulty

#### 2.1 Create Notification API Client
**File:** `src/lib/notification-api.ts` (new)

```typescript
// Functions to implement:
- fetchNotifications(page, limit)
- markNotificationRead(id)
- markAllNotificationsRead()
- deleteNotification(id)
- getNotificationCounts()
```

#### 2.2 Update Notification Context
**File:** [`src/contexts/NotificationContext.tsx`](src/contexts/NotificationContext.tsx)

Replace mock data with API calls:
```typescript
- useEffect to fetch notifications on mount
- updateNotification() calls API
- removeNotification() calls API
- markAsRead() calls API
```

#### 2.3 Update Notification Types
**File:** [`src/types/index.ts`](src/types/index.ts)

Add new notification sub-types:
```typescript
export type NotificationSubtype = 
  | 'time_to_take'
  | 'missed_medicine'
  | 'low_stock'
  | 'critical_stock'
  | 'prescription_expiring'
  | 'prescription_expired'
  | 'adherence_streak'
  | 'adherence_drop'
  | 'system';
```

---

### Phase 3: Tick/Cross Action UI - Medium Difficulty

#### 3.1 Update Notification Item Component
**File:** [`src/components/notifications/NotificationBell.tsx`](src/components/notifications/NotificationBell.tsx)

Modify `NotificationItem` component:

```typescript
// Current state - only has Check (mark as read) and X (remove)
// Required - Add tick/cross for action handling

interface NotificationAction {
  onMarkTaken?: (id: string) => void;
  onMarkSkipped?: (id: string) => void;
  onSnooze?: (id: string) => void;
}
```

#### 3.2 Add Action Handlers to Context
**File:** [`src/contexts/NotificationContext.tsx`](src/contexts/NotificationContext.tsx)

```typescript
// Add to NotificationContextType:
interface NotificationContextType {
  // ... existing methods
  markAsTaken: (id: string) => void;
  markAsSkipped: (id: string) => void;
  snoozeNotification: (id: string, minutes: number) => void;
}
```

#### 3.3 Enhanced Notification Item UI

**Visual Design:**
```
┌─────────────────────────────────────────────────────┐
│ 💊 Time to take your medicine                       │
│ Aspirin 100mg - 1 tablet                            │
│ Today                                               │
│                      ✓ Done    ✗ Skip    ⏰ Later  │
└─────────────────────────────────────────────────────┘
```

**Action Types by Notification:**
| Notification Type | ✓ Action | ✗ Action | ⏰ Action |
|-------------------|----------|----------|-----------|
| Time to take medicine | Mark taken | Mark skipped | Snooze 15min |
| Low stock alert | Open inventory | Dismiss | - |
| Prescription expiry | View prescription | Dismiss | - |

---

### Phase 4: Notification Triggers (Backend) - Hard Difficulty

#### 4.1 Reminder Notification Trigger
**File:** `pillio-backend/app/services/notification_service.py`

```python
async def create_reminder_notification(
    user_id: int,
    reminder_id: int,
    medicine_name: str,
    dosage: str
) -> Notification:
    """Create notification when reminder is due"""
```

**Trigger Points:**
- When reminder time is reached (requires background job/worker)
- When user marks reminder as taken (immediate confirmation)
- When reminder is missed (after grace period)

#### 4.2 Low Stock Notification Trigger
**File:** `pillio-backend/app/services/notification_service.py`

```python
async def check_and_notify_low_stock(user_id: int) -> List[Notification]:
    """Check stock levels and create notifications"""
```

**Trigger Points:**
- After any stock adjustment
- Daily background check
- On medicine page load (real-time)

#### 4.3 Prescription Expiry Notification Trigger
**File:** `pillio-backend/app/services/notification_service.py`

```python
async def check_prescription_expiry(user_id: int) -> List[Notification]:
    """Check expiring prescriptions and notify"""
```

**Trigger Points:**
- Daily background check
- On prescription list view
- When prescription is created/updated

#### 4.4 Adherence Notification Trigger
**File:** `pillio-backend/app/services/notification_service.py`

```python
async def check_adherence_patterns(user_id: int) -> List[Notification]:
    """Analyze adherence and create notifications"""
```

**Trigger Points:**
- Daily adherence calculation
- When streak milestones are reached
- When adherence rate drops below threshold

---

### Phase 5: Dedicated Notifications Page - Medium Difficulty

#### 5.1 Create Notifications Page
**File:** `src/pages/NotificationsPage.tsx` (new)

**Features:**
- Full list of all notifications
- Filter by type (All, Reminders, Stock, Prescriptions, System)
- Search functionality
- Bulk actions (mark all read, clear all)
- Pagination

#### 5.2 Add Navigation
**File:** [`src/components/layout/Sidebar.tsx`](src/components/layout/Sidebar.tsx)

Add "Notifications" nav item with badge count

#### 5.3 Notification Settings
**File:** `src/pages/NotificationSettings.tsx` (new)

**Settings:**
- Enable/disable notification types
- Notification frequency
- Low stock threshold
- Prescription expiry warning days

---

## Notification Types by Difficulty Summary

### Easy (Frontend-focused, no backend changes needed)
1. ✅ Low stock alert notification UI
2. ✅ Prescription expiring notification UI
3. ✅ System notification display
4. ✅ Notification bell with badge count
5. ✅ Basic tick/cross UI implementation

### Medium (Requires API integration)
1. 🔄 Notification API endpoints
2. 🔄 Frontend API integration
3. 🔄 Notification context refactoring
4. 🔄 Dedicated notifications page
5. 🔄 Notification settings page
6. 🔄 Reminder taken/skipped actions
7. 🔄 Adherence streak notifications

### Hard (Requires background jobs/scheduling)
1. ⏰ Automatic reminder notifications (scheduled)
2. ⏰ Daily low stock checks
3. ⏰ Prescription expiry monitoring
4. ⏰ Adherence pattern analysis
5. ⏰ Notification cleanup job
6. ⏰ Real-time notification delivery (WebSocket)

---

## Implementation Order Recommendation

```
Phase 1 (Foundation): Backend API + Notification Service
         ↓
Phase 2 (Integration): Frontend API integration + Context update
         ↓
Phase 3 (Actions): Tick/Cross UI + Action handlers
         ↓
Phase 4 (Triggers): Backend notification triggers (background jobs)
         ↓
Phase 5 (Polish): Dedicated page + Settings + Polish
```

---

## Mock Data Format (Current)

The UI should continue to match this mock data format:

```typescript
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
```

---

## Files to Create/Modify

### New Files
| File | Purpose | Difficulty |
|------|---------|------------|
| `pillio-backend/app/api/notifications.py` | API endpoints | Medium |
| `pillio-backend/app/services/notification_service.py` | Business logic | Medium |
| `src/lib/notification-api.ts` | API client | Easy |
| `src/pages/NotificationsPage.tsx` | Full page view | Medium |
| `src/pages/NotificationSettings.tsx` | Settings page | Medium |

### Modified Files
| File | Changes | Difficulty |
|------|---------|------------|
| `pillio-backend/app/main.py` | Add notification router | Easy |
| `src/contexts/NotificationContext.tsx` | API integration + actions | Medium |
| `src/components/notifications/NotificationBell.tsx` | Tick/cross actions | Medium |
| `src/types/index.ts` | Add new types | Easy |
| `src/components/layout/Sidebar.tsx` | Add nav item | Easy |

---

## Success Criteria

1. ✅ Notifications persist in database (not just mock data)
2. ✅ All notification types display correctly with icons
3. ✅ Tick/cross actions work for applicable notifications
4. ✅ Notification counts update in real-time
5. ✅ Background triggers create notifications automatically
6. ✅ Users can manage notification preferences
7. ✅ Notifications are deleted after action or expiration
