# Updated Frontend-Backend Integration Plan

## Current Status (as of Jan 6, 2025)

### ✅ Completed Modules

#### Phase 1: Authentication Integration
- **Backend Status:** Ready (no changes needed)
- **Frontend Status:** Completed
- **Files Created:**
  - [`src/lib/auth-api.ts`](src/lib/auth-api.ts) - Auth API service
  - [`src/contexts/auth-context.ts`](src/contexts/auth-context.ts) - Type definitions
- **Files Modified:**
  - [`src/lib/api.ts`](src/lib/api.ts) - Switched to axios with token refresh
  - [`src/contexts/AuthContext.tsx`](src/contexts/AuthContext.tsx) - Connected to real API
- **Features Implemented:**
  - Login with `POST /auth/login`
  - Register with `POST /auth/register`
  - Automatic token refresh on 401
  - Profile fetching with `GET /auth/me`
  - Profile update with `PUT /auth/me`
  - Logout with `POST /auth/logout`

#### Phase 2: Medicines CRUD Integration
- **Backend Status:** Ready (no changes needed)
- **Frontend Status:** Completed
- **Files Created:**
  - [`src/lib/medicines-api.ts`](src/lib/medicines-api.ts) - Medicines API service
  - [`src/lib/users-api.ts`](src/lib/users-api.ts) - Users API service
  - [`src/components/medicine/MedicineFormDialog.tsx`](src/components/medicine/MedicineFormDialog.tsx) - Add/Edit form
  - [`src/components/medicine/DeleteMedicineDialog.tsx`](src/components/medicine/DeleteMedicineDialog.tsx) - Delete confirmation
- **Files Modified:**
  - [`src/types/index.ts`](src/types/index.ts) - Added API types and converters
  - [`src/pages/MedicinesPage.tsx`](src/pages/MedicinesPage.tsx) - Connected to API + CRUD dialogs
  - [`src/components/dashboard/DashboardStats.tsx`](src/components/dashboard/DashboardStats.tsx) - Connected to stats API
- **Features Implemented:**
  - List medicines with `GET /medicines`
  - Search medicines with `GET /medicines/search`
  - Create medicine with `POST /medicines`
  - Update medicine with `PUT /medicines/{id}`
  - Delete medicine with `DELETE /medicines/{id}`
  - Dashboard stats with `GET /users/stats`
  - Add/Edit/Delete modals with form validation

---

## 📋 Remaining Work

### Phase 3: Reminders API & Integration
**Priority:** High (core feature)

#### Backend Tasks (Create new)
| File | Description |
|------|-------------|
| `pillio-backend/app/api/reminders.py` | Reminders router with CRUD endpoints |
| `pillio-backend/app/services/reminder_service.py` | Reminder business logic |
| `pillio-backend/app/schemas/reminder.py` | Reminder Pydantic schemas |

#### Backend Endpoints to Create
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/reminders` | Create reminder |
| `GET` | `/api/v1/reminders` | List reminders |
| `GET` | `/api/v1/reminders/{id}` | Get reminder |
| `PUT` | `/api/v1/reminders/{id}` | Update reminder |
| `DELETE` | `/api/v1/reminders/{id}` | Delete reminder |
| `POST` | `/api/v1/reminders/{id}/take` | Mark as taken |
| `POST` | `/api/v1/reminders/{id}/skip` | Skip reminder |

#### Frontend Tasks
| File | Description |
|------|-------------|
| `src/lib/reminders-api.ts` | Create Reminders API service |
| `src/pages/RemindersPage.tsx` | Connect to real API + CRUD dialogs |
| `src/components/dashboard/UpcomingReminders.tsx` | Connect to reminders API |
| `src/components/reminder/ReminderFormDialog.tsx` | Create Add/Edit reminder dialog |

---

### Phase 4: Prescriptions API & Integration
**Priority:** Medium

#### Backend Tasks (Create new)
| File | Description |
|------|-------------|
| `pillio-backend/app/api/prescriptions.py` | Prescriptions router |
| `pillio-backend/app/services/prescription_service.py` | Prescription business logic |
| `pillio-backend/app/schemas/prescription.py` | Prescription Pydantic schemas |

#### Backend Endpoints to Create
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/prescriptions` | Create prescription |
| `GET` | `/api/v1/prescriptions` | List prescriptions |
| `GET` | `/api/v1/prescriptions/{id}` | Get prescription |
| `PUT` | `/api/v1/prescriptions/{id}` | Update prescription |
| `DELETE` | `/api/v1/prescriptions/{id}` | Delete prescription |
| `POST` | `/api/v1/prescriptions/{id}/upload` | Upload prescription image |

#### Frontend Tasks
| File | Description |
|------|-------------|
| `src/lib/prescriptions-api.ts` | Create Prescriptions API service |
| `src/pages/PrescriptionsPage.tsx` | Connect to real API + CRUD dialogs |
| `src/components/prescription/PrescriptionFormDialog.tsx` | Create Add/Edit prescription dialog |
| `src/components/prescription/PrescriptionUpload.tsx` | Create image upload component |

---

### Phase 5: Notifications API & Integration
**Priority:** Medium

#### Backend Tasks (Create new)
| File | Description |
|------|-------------|
| `pillio-backend/app/api/notifications.py` | Notifications router |
| `pillio-backend/app/services/notification_service.py` | Notification business logic |
| `pillio-backend/app/schemas/notification.py` | Notification Pydantic schemas |

#### Backend Endpoints to Create
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/notifications` | List notifications |
| `GET` | `/api/v1/notifications/unread` | Get unread count |
| `PUT` | `/api/v1/notifications/{id}/read` | Mark as read |
| `PUT` | `/api/v1/notifications/read-all` | Mark all as read |
| `DELETE` | `/api/v1/notifications/{id}` | Delete notification |

#### Frontend Tasks
| File | Description |
|------|-------------|
| `src/lib/notifications-api.ts` | Create Notifications API service |
| `src/contexts/NotificationContext.tsx` | Connect to real API |
| `src/components/notifications/NotificationBell.tsx` | Connect to notifications API |
| `src/components/notifications/NotificationDropdown.tsx` | Create notification list dropdown |

---

### Phase 6: Reports & Analytics API
**Priority:** Low

#### Backend Tasks (Create new)
| File | Description |
|------|-------------|
| `pillio-backend/app/api/reports.py` | Reports router |
| `pillio-backend/app/services/report_service.py` | Report generation logic |

#### Backend Endpoints to Create
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/reports/adherence` | Get adherence report |
| `GET` | `/api/v1/reports/consumption` | Get consumption report |
| `GET` | `/api/v1/reports/inventory` | Get inventory report |
| `GET` | `/api/v1/reports/summary` | Get summary report |

#### Frontend Tasks
| File | Description |
|------|-------------|
| `src/lib/reports-api.ts` | Create Reports API service |
| `src/pages/ReportsPage.tsx` | Connect to real API |
| `src/components/analytics/AdherenceChart.tsx` | Connect to adherence API |

---

## 🔧 Additional Frontend Components Needed

### Dialogs/Forms to Create
| Component | Status | Description |
|-----------|--------|-------------|
| `MedicineFormDialog` | ✅ Created | Add/Edit medicine form |
| `DeleteMedicineDialog` | ✅ Created | Delete confirmation |
| `ReminderFormDialog` | ❌ Pending | Add/Edit reminder form |
| `DeleteReminderDialog` | ❌ Pending | Delete confirmation |
| `PrescriptionFormDialog` | ❌ Pending | Add/Edit prescription form |
| `DeletePrescriptionDialog` | ❌ Pending | Delete confirmation |
| `StockAdjustmentDialog` | ❌ Pending | Adjust stock dialog |
| `PrescriptionUploadDialog` | ❌ Pending | Upload prescription image |

### Pages Still Using Mock Data
| Page | Status | Notes |
|------|--------|-------|
| `DashboardPage` | ⚠️ Partial | Stats connected, reminders still mock |
| `MedicinesPage` | ✅ Done | Fully connected |
| `RemindersPage` | ❌ Mock | Needs backend API |
| `PrescriptionsPage` | ❌ Mock | Needs backend API |
| `InventoryPage` | ❌ Not checked | Needs verification |
| `HistoryPage` | ❌ Mock | Needs backend API |
| `ReportsPage` | ❌ Mock | Needs backend API |
| `SettingsPage` | ❌ Mock | Needs API connection |

---

## 📁 Files Summary

### Files Created (Phase 1 & 2)
```
src/lib/
├── api.ts (modified - axios + token refresh)
├── auth-api.ts (new)
├── medicines-api.ts (new)
├── users-api.ts (new)

src/contexts/
├── auth-context.ts (new - type definitions)
└── AuthContext.tsx (modified - real API)

src/components/
├── medicine/
│   ├── MedicineFormDialog.tsx (new)
│   └── DeleteMedicineDialog.tsx (new)
└── dashboard/
    └── DashboardStats.tsx (modified - real API)

src/pages/
└── MedicinesPage.tsx (modified - real API + dialogs)

src/types/
└── index.ts (modified - API types + converters)
```

### Files to Create (Phase 3-6)
```
src/lib/
├── reminders-api.ts (new)
├── prescriptions-api.ts (new)
├── notifications-api.ts (new)
└── reports-api.ts (new)

src/components/
├── reminder/
│   ├── ReminderFormDialog.tsx (new)
│   └── DeleteReminderDialog.tsx (new)
├── prescription/
│   ├── PrescriptionFormDialog.tsx (new)
│   ├── DeletePrescriptionDialog.tsx (new)
│   └── PrescriptionUploadDialog.tsx (new)
├── notifications/
│   ├── NotificationDropdown.tsx (new)
│   └── NotificationItem.tsx (new)
└── inventory/
    └── StockAdjustmentDialog.tsx (new)

src/pages/
├── RemindersPage.tsx (modify)
├── PrescriptionsPage.tsx (modify)
├── InventoryPage.tsx (modify)
├── HistoryPage.tsx (modify)
├── ReportsPage.tsx (modify)
└── SettingsPage.tsx (modify)

src/contexts/
└── NotificationContext.tsx (modify)
```

---

## 🎯 Next Steps

1. **Phase 3 (Reminders)**: Create backend API first, then frontend integration
2. **Phase 4 (Prescriptions)**: Create backend API, then frontend integration  
3. **Phase 5 (Notifications)**: Create backend API, then frontend integration
4. **Phase 6 (Reports)**: Create backend API, then frontend integration
5. **Testing**: Comprehensive integration testing across all modules

**Recommended:** Continue with Phase 3 (Reminders) as it's a core feature and the `RemindersPage` already has mock data that needs to be connected.
