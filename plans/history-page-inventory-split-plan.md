# History Page 50/50 Split with Inventory History Table

## Overview
Divide the HistoryPage into two equal columns (vertical split on desktop):
- **Left Column**: Existing medication reminder history
- **Right Column**: New inventory history table showing medicine expenditures

## Implementation Plan

### Step 1: Backend - Add New API Endpoint
**File**: `pillio-backend/app/api/medicines.py`

Add a new endpoint to get all inventory history for the current user:

```python
@router.get("/inventory-history", response_model=PaginatedResponse[InventoryHistoryWithMedicine])
async def get_all_inventory_history(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    change_type: Optional[str] = Query(None, description="Filter by change type"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all inventory history records for the current user with pagination and filtering.
    """
```

**Schema Update**: Update `InventoryHistoryWithMedicine` in `pillio-backend/app/schemas/inventory_history.py` to include medicine name.

### Step 2: Frontend API - Add New Function
**File**: `src/lib/medicines-api.ts`

Add a new function to fetch all inventory history:

```typescript
// Get all inventory history for user
getAllInventoryHistory: (params?: {
  page?: number;
  per_page?: number;
  change_type?: string;
}): Promise<AxiosResponse<PaginatedResponse<InventoryHistoryWithMedicine>>> =>
  api.get<PaginatedResponse<InventoryHistoryWithMedicine>>('/medicines/inventory-history', { params }),
```

Update the `InventoryHistory` interface to include `medicine_name`.

### Step 3: Modify HistoryPage Layout
**File**: `src/pages/HistoryPage.tsx`

1. Import table components from `@/components/ui/table`
2. Add state for inventory history data
3. Create a grid layout with 2 columns:
   - Use CSS grid: `grid grid-cols-1 lg:grid-cols-2 gap-6`
4. Keep existing medication history in left column
5. Add new inventory history table in right column

### Step 4: Inventory History Table Columns
The table will display:
| Column | Description |
|--------|-------------|
| Medicine Name | Name of the medicine |
| Change Type | added, consumed, adjusted, expired |
| Amount | Change amount (positive/negative) |
| Previous Stock | Stock before change |
| New Stock | Stock after change |
| Notes | Additional notes |
| Date | Created at timestamp |

### Step 5: Inventory History State Management
```typescript
interface InventoryHistoryState {
  items: InventoryHistoryWithMedicine[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
  loading: boolean;
  error: string | null;
  changeTypeFilter: string;
}
```

## Visual Layout

```
+------------------------------------------------------------------+
|                          Page Header                             |
+------------------------------------------------------------------+
|  Filters (shared or separate for each section?)                  |
+------------------------------------------------------------------+
|  +--------------------------------+  +------------------------+  |
|  |  Medication History            |  |  Inventory History     |  |
|  |  (Left Column)                 |  |  (Right Column)        |  |
|  |                                |  |                        |  |
|  |  - List of reminders          |  |  - Table with 7 cols   |  |
|  |  - Status icons               |  |  - Pagination          |  |
|  |  - Pagination                 |  |  - Filtering           |  |
|  |                                |  |                        |  |
|  +--------------------------------+  +------------------------+  |
+------------------------------------------------------------------+
```

## Dependencies
- No new dependencies needed
- Uses existing table UI components
- Uses existing pagination patterns

## Estimated Changes
- Backend: ~50 lines (new endpoint + schema update)
- Frontend API: ~20 lines (new function + interface update)
- Frontend Page: ~150 lines (layout + table + state management)
