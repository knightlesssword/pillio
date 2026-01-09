# History Page UI Improvements Plan

## Overview
This plan covers UI improvements to the History Page:
1. Add icons to dropdown triggers (date range, status)
2. Change refresh button to icon-only
3. Add export dropdown with CSV, PDF, and Show JSON options

---

## Current State
The HistoryPage.tsx currently has:
- Text-based dropdown triggers (no icons)
- Text-based refresh button with icon
- Simple card display

---

## Changes Required

### 1. Icons for Date Range Dropdown Trigger

**Current**:
```tsx
<SelectTrigger>
  <SelectValue placeholder="Date Range" />
</SelectTrigger>
```

**Updated**:
```tsx
<SelectTrigger>
  <Calendar className="h-4 w-4 mr-2" />
  <SelectValue placeholder="Date Range" />
</SelectTrigger>
```

### 2. Icons for Status Dropdown Trigger

**Current**:
```tsx
<SelectTrigger>
  <SelectValue placeholder="Status" />
</SelectTrigger>
```

**Updated**:
```tsx
<SelectTrigger>
  <Filter className="h-4 w-4 mr-2" />
  <SelectValue placeholder="Status" />
</SelectTrigger>
```

### 3. Icon-Only Refresh Button

**Current**:
```tsx
<Button variant="outline" onClick={fetchHistory} disabled={history.loading}>
  {history.loading ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
  Refresh
</Button>
```

**Updated**:
```tsx
<Button variant="outline" size="icon" onClick={fetchHistory} disabled={history.loading}>
  {history.loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <RotateCw className="h-4 w-4" />}
  <span className="sr-only">Refresh</span>
</Button>
```

### 4. Export Dropdown with CSV, PDF, Show JSON

**Add imports**:
```typescript
import {
  Download,
  FileJson,
  FileSpreadsheet,
  FileText
} from 'lucide-react';
```

**Add state for JSON modal**:
```typescript
const [showJsonModal, setShowJsonModal] = useState(false);
```

**Add Export Dropdown**:
```tsx
<DropdownMenu>
  <DropdownMenuTrigger asChild>
    <Button variant="outline" size="icon">
      <Download className="h-4 w-4" />
      <span className="sr-only">Export</span>
    </Button>
  </DropdownMenuTrigger>
  <DropdownMenuContent>
    <DropdownMenuItem onClick={() => exportToCSV()}>
      <FileSpreadsheet className="h-4 w-4 mr-2" />
      Export as CSV
    </DropdownMenuItem>
    <DropdownMenuItem onClick={() => exportToPDF()}>
      <FileText className="h-4 w-4 mr-2" />
      Export as PDF
    </DropdownMenuItem>
    <DropdownMenuItem onClick={() => setShowJsonModal(true)}>
      <FileJson className="h-4 w-4 mr-2" />
      Show JSON
    </DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

### 5. Export Functionality

**CSV Export**:
```typescript
const exportToCSV = () => {
  const headers = ['Medicine', 'Status', 'Scheduled Time', 'Taken Time', 'Dosage'];
  const rows = history.items.map(item => [
    item.medicine_name,
    item.status,
    formatDateTime(item.scheduled_time),
    formatDateTime(item.taken_time),
    item.dosage
  ]);
  
  const csvContent = [headers.join(','), ...rows.map(row => row.join(','))]
    .join('\n');
  
  downloadFile(csvContent, `medication-history-${dateRange}.csv`, 'text/csv');
};
```

**PDF Export**:
```typescript
const exportToPDF = () => {
  // Use jspdf and jspdf-autotable for PDF generation
  // Create table with history data
};
```

**JSON Modal Component**:
```tsx
<Dialog open={showJsonModal} onOpenChange={setShowJsonModal}>
  <DialogContent className="max-w-2xl">
    <DialogHeader>
      <DialogTitle>History Data (JSON)</DialogTitle>
    </DialogHeader>
    <ScrollArea className="h-96">
      <pre className="text-sm">
        {JSON.stringify(history.items, null, 2)}
      </pre>
    </ScrollArea>
  </DialogContent>
</Dialog>
```

---

## Updated Filter Section Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│ [📅 Current Week ▼]  [�Filter All Status ▼]  [↻]  [⬇ Export ▼]    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Files to Modify

| File | Changes |
|------|---------|
| `src/pages/HistoryPage.tsx` | Add icons to dropdowns, icon-only buttons, export dropdown, JSON modal |

---

## Dependencies

For PDF export, install (if not already):
```bash
npm install jspdf jspdf-autotable
```

---

## Testing Checklist

- [ ] Date range dropdown shows calendar icon
- [ ] Status dropdown shows filter icon
- [ ] Refresh button is icon-only with tooltip
- [ ] Export dropdown shows all three options
- [ ] CSV export downloads correct file
- [ ] PDF export downloads correct file
- [ ] JSON modal displays formatted data
- [ ] Modal can be closed with X or clicking outside
