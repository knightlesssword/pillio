# History Page Implementation Plan

## Current State Analysis

### History Page (`src/pages/HistoryPage.tsx`)
- Has hardcoded mock data with 4 entries
- Displays medicine name, action (Taken/Missed/Skipped), and time
- Uses static text like "Missed at 1:00 PM"

### Backend Capability
- `ReminderLog` model exists with fields:
  - `scheduled_time` - when reminder was scheduled
  - `taken_time` - when user marked as taken
  - `status` - taken, skipped, missed
  - `notes` - optional notes
- `mark_reminder_taken()` and `mark_reminder_skipped()` methods exist
- **Missing**: Endpoint to fetch reminder logs for history view

## Answer to "Missed at 1:00pm" Question

**No, it's not implemented.** The "missed at 1:00pm" in mock data is just static text. 

The backend CAN track this because:
1. `ReminderLog.scheduled_time` stores the scheduled time
2. When a user skips a reminder, a log is created with status "skipped"

**However**, there's a gap:
- No automatic marking of reminders as "missed" when they pass without action
- No API endpoint to retrieve history/logs for the frontend

## Implementation Plan

### Phase 1: Backend - Add History API Endpoint

#### 1.1 Add Service Method
File: `pillio-backend/app/services/reminder_service.py`

```python
async def get_reminder_history(
    self, 
    user_id: int, 
    start_date: date, 
    end_date: date,
    status: Optional[str] = None,
    medicine_id: Optional[int] = None,
    page: int = 1,
    per_page: int = 20
) -> Tuple[List[ReminderLog], int]:
    """Get reminder history with filtering and pagination"""
```

#### 1.2 Add API Endpoint
File: `pillio-backend/app/api/reminders.py`

```python
@router.get("/history", response_model=PaginatedResponse[dict])
async def get_reminder_history(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    status: Optional[str] = Query(None, description="Filter by status"),
    medicine_id: Optional[int] = Query(None, description="Filter by medicine"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    reminder_service: ReminderService = Depends(get_reminder_service)
):
    """Get reminder history with optional filtering"""
```

#### 1.3 Add Response Schema
File: `pillio-backend/app/schemas/reminder.py`

```python
class ReminderLogWithMedicine(BaseModel):
    """Reminder log with medicine info for history"""
    id: int
    medicine_name: str
    dosage: str
    scheduled_time: datetime
    taken_time: Optional[datetime]
    status: str
    notes: Optional[str]
```

### Phase 2: Frontend - Integrate History API

#### 2.1 Add API Function
File: `src/lib/reminders-api.ts`

```typescript
export async function getReminderHistory(params: HistoryParams): Promise<HistoryResponse> {
  const queryParams = new URLSearchParams()
  queryParams.append('start_date', params.start_date)
  queryParams.append('end_date', params.end_date)
  if (params.status) queryParams.append('status', params.status)
  if (params.medicine_id) queryParams.append('medicine_id', params.medicine_id.toString())
  queryParams.append('page', params.page.toString())
  queryParams.append('per_page', params.per_page.toString())
  
  const response = await api.get(`/reminders/history?${queryParams}`)
  return response.data
}
```

#### 2.2 Update HistoryPage Component
File: `src/pages/HistoryPage.tsx`

- Replace mock data with API call
- Add loading states
- Add date range picker
- Add status filter
- Add pagination

### Phase 3: Auto-Mark Missed Reminders

#### 3.1 Add Service Method
File: `pillio-backend/app/services/reminder_service.py`

```python
async def mark_overdue_reminders_as_missed(self, user_id: Optional[int] = None) -> int:
    """Mark all reminders that passed their scheduled time without action as missed"""
    # Get all pending reminders where scheduled_time has passed
    # and no log entry exists, then create 'missed' log entries
```

#### 3.2 Add API Endpoint for Manual Trigger
File: `pillio-backend/app/api/reminders.py`

```python
@router.post("/mark-missed")
async def mark_overdue_reminders_missed(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    reminder_service: ReminderService = Depends(get_reminder_service)
):
    """Mark all overdue reminders as missed (can be called by scheduler)"""
    count = await reminder_service.mark_overdue_reminders_as_missed(user_id=current_user.id)
    return {"message": f"Marked {count} reminders as missed"}
```

#### 3.3 Setup Scheduler (Optional)
- Add APScheduler or similar for periodic execution
- Run every hour or at midnight to mark previous day's missed reminders

### Phase 4: Additional Features (Optional)

1. **Adherence summary card** - Show overall adherence rate
2. **Export functionality** - Export history to CSV/PDF
3. **Streak tracking** - Show consecutive days of adherence
4. **Medicine filter dropdown** - Filter by specific medicine

## Mermaid: Data Flow

```mermaid
graph TD
    A[HistoryPage] --> B[getReminderHistory API]
    B --> C[reminders-api.ts]
    C --> D[/reminders/history Endpoint]
    D --> E[ReminderService.get_reminder_history]
    E --> F[Query ReminderLogs with joins]
    F --> G[Return paginated results]
    G --> H[HistoryPage displays data]
```

## Files to Modify

| File | Changes |
|------|---------|
| `pillio-backend/app/services/reminder_service.py` | Add `get_reminder_history()` method |
| `pillio-backend/app/api/reminders.py` | Add `/history` endpoint |
| `pillio-backend/app/schemas/reminder.py` | Add `ReminderLogWithMedicine` schema |
| `src/lib/reminders-api.ts` | Add `getReminderHistory()` function |
| `src/pages/HistoryPage.tsx` | Replace mock data with real data, add filters |

## Questions for Clarification

1. **Date range default** - Should history show last 7 days, 30 days, or current week by default?
- Keep default as current week but show options for current month, 3months and 6 months, current year, all time.
2. **Missed reminders auto-marking** - Should we implement automatic marking of missed reminders?
- as mentioned above 
3. **Additional features** - Which of the optional features should be prioritized?
- continue as planned in the doc
