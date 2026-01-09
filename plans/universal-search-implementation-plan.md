# Universal Search Implementation Plan

## Overview

Implement a universal search bar in the navbar that allows users to search across medicines, reminders, and prescriptions from a single input field.

## User Flow

1. User clicks or focuses on the search bar in the navbar
2. User types a search query (e.g., "Aspirin", "Morning", "Dr. Smith")
3. Results appear in a dropdown as the user types (debounced)
4. Results are grouped by category (Medicines, Reminders, Prescriptions)
5. User can navigate results with keyboard arrows
6. Clicking or pressing Enter on a result navigates to the appropriate page

## Components to Create

### Frontend

| Component | Purpose | Location |
|-----------|---------|----------|
| `UniversalSearch.tsx` | Main search component with dropdown | `src/components/search/` |
| `SearchResultItem.tsx` | Individual result item | `src/components/search/` |
| `SearchResultGroup.tsx` | Grouped results by category | `src/components/search/` |

### Backend

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/search` | GET | Unified search across all entities |

## Implementation Steps

### Step 1: Create Search Component Structure

- Create `src/components/search/` directory
- Create `UniversalSearch.tsx` with state for query, results, and dropdown visibility
- Add debounced search hook (300ms delay)
- Style with Tailwind CSS

### Step 2: Implement Search API Endpoint

- Create backend search endpoint in `pillio-backend/app/api/search.py`
- Query medicines table (name, generic_name)
- Query reminders table (medicine_name, notes)
- Query prescriptions table (doctor_name, notes)
- Return combined results with type indicators

### Step 3: Add Search API Client

- Create `src/lib/search-api.ts`
- Implement `searchAll(query: string)` function
- Handle API errors gracefully

### Step 4: Connect Search to Navbar

- Replace static `Input` in Navbar with `UniversalSearch` component
- Ensure mobile responsive behavior

### Step 5: Add Keyboard Navigation

- Arrow keys to navigate results
- Enter to select
- Escape to close dropdown

### Step 6: Add Empty State & Loading

- Show "No results found" when query returns nothing
- Show loading spinner while fetching results

## Technical Details

### API Response Structure

```typescript
interface SearchResult {
  id: string;
  type: 'medicine' | 'reminder' | 'prescription';
  title: string;
  subtitle: string;
  route: string;
}

interface SearchResponse {
  results: SearchResult[];
  total: number;
}
```

### Component State

```typescript
interface SearchState {
  query: string;
  results: SearchResult[];
  isOpen: boolean;
  selectedIndex: number;
  isLoading: boolean;
}
```

### Debounce Logic

- Use `useDebounce` hook with 300ms delay
- Only trigger search when query length >= 2 characters

## File Structure

```
src/
  components/
    search/
      UniversalSearch.tsx
      SearchResultItem.tsx
      SearchResultGroup.tsx
  lib/
    search-api.ts
pillio-backend/
  app/
    api/
      search.py
```

## Future Enhancements (Post-MVP)

- Search within inventory history
- Recent searches history
- Search by barcode/QR code
- Voice search
- Search analytics
