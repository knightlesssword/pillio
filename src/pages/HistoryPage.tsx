import React, { useState, useEffect, useCallback } from 'react';
import PageHeader from '@/components/common/PageHeader';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from '@/components/ui/table';
import {
  History,
  CheckCircle,
  XCircle,
  Clock,
  Loader2,
  Calendar,
  Filter,
  RotateCw,
  Download,
  FileSpreadsheet,
  FileText,
  FileJson,
  Copy,
  Package,
  ArrowUpCircle,
  ArrowDownCircle,
  Settings
} from 'lucide-react';
import { remindersApi, type ReminderHistoryItem } from '@/lib/reminders-api';
import { medicinesApi, type InventoryHistoryWithMedicine, type PaginatedResponse } from '@/lib/medicines-api';
import { useToast } from '@/hooks/use-toast';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

type DateRange = 'week' | 'month' | '3months' | '6months' | 'year' | 'all';

interface HistoryState {
  items: ReminderHistoryItem[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
  loading: boolean;
  error: string | null;
}

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

export default function HistoryPage() {
  const { toast } = useToast();
  const [dateRange, setDateRange] = useState<DateRange>('week');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [showJsonModal, setShowJsonModal] = useState(false);
  const [showInventoryDetailModal, setShowInventoryDetailModal] = useState(false);
  const [jsonModalType, setJsonModalType] = useState<'medication' | 'inventory'>('medication');
  const [selectedInventoryItem, setSelectedInventoryItem] = useState<InventoryHistoryWithMedicine | null>(null);
  const [inventoryChangeTypeFilter, setInventoryChangeTypeFilter] = useState<string>('all');
  const [inventoryDateRange, setInventoryDateRange] = useState<DateRange>('all');
  const [history, setHistory] = useState<HistoryState>({
    items: [],
    total: 0,
    page: 1,
    per_page: 20,
    pages: 0,
    loading: false,
    error: null,
  });

  const [inventoryHistory, setInventoryHistory] = useState<InventoryHistoryState>({
    items: [],
    total: 0,
    page: 1,
    per_page: 20,
    pages: 0,
    loading: false,
    error: null,
    changeTypeFilter: 'all',
  });

  const getDateRangeForFilter = useCallback((range: DateRange): { start_date: string; end_date: string } => {
    const endDate = new Date();
    let startDate = new Date();

    switch (range) {
      case 'week':
        startDate = new Date(endDate);
        startDate.setDate(endDate.getDate() - 7);
        break;
      case 'month':
        startDate = new Date(endDate);
        startDate.setMonth(endDate.getMonth() - 1);
        break;
      case '3months':
        startDate = new Date(endDate);
        startDate.setMonth(endDate.getMonth() - 3);
        break;
      case '6months':
        startDate = new Date(endDate);
        startDate.setMonth(endDate.getMonth() - 6);
        break;
      case 'year':
        startDate = new Date(endDate);
        startDate.setFullYear(endDate.getFullYear() - 1);
        break;
      case 'all':
        startDate = new Date('2020-01-01');
        break;
    }

    return {
      start_date: startDate.toISOString().split('T')[0],
      end_date: endDate.toISOString().split('T')[0],
    };
  }, []);

  const fetchHistory = useCallback(async () => {
    setHistory(prev => ({ ...prev, loading: true, error: null }));

    try {
      const dates = getDateRangeForFilter(dateRange);
      const params: Parameters<typeof remindersApi.getHistory>[0] = {
        start_date: dates.start_date,
        end_date: dates.end_date,
        page: history.page,
        per_page: history.per_page,
      };

      if (statusFilter !== 'all') {
        params.reminder_status = statusFilter;
      }

      const response = await remindersApi.getHistory(params);
      setHistory(prev => ({
        ...prev,
        items: response.data.items,
        total: response.data.total,
        pages: response.data.pages,
        loading: false,
      }));
    } catch (error) {
      console.error('Error fetching history:', error);
      setHistory(prev => ({
        ...prev,
        loading: false,
        error: 'Failed to load history. Please try again.',
      }));
      toast({
        title: 'Error',
        description: 'Failed to load medication history',
        variant: 'destructive',
      });
    }
  }, [dateRange, statusFilter, history.page, history.per_page, getDateRangeForFilter, toast]);

  const fetchInventoryHistory = useCallback(async () => {
    setInventoryHistory(prev => ({ ...prev, loading: true, error: null }));

    try {
      const dates = getDateRangeForFilter(inventoryDateRange);
      const params: Parameters<typeof medicinesApi.getAllInventoryHistory>[0] = {
        page: inventoryHistory.page,
        per_page: inventoryHistory.per_page,
        start_date: dates.start_date,
        end_date: dates.end_date,
      };

      if (inventoryChangeTypeFilter !== 'all') {
        params.change_type = inventoryChangeTypeFilter;
      }

      const response = await medicinesApi.getAllInventoryHistory(params);
      setInventoryHistory(prev => ({
        ...prev,
        items: response.data.items,
        total: response.data.total,
        pages: response.data.pages,
        loading: false,
      }));
    } catch (error) {
      console.error('Error fetching inventory history:', error);
      setInventoryHistory(prev => ({
        ...prev,
        loading: false,
        error: 'Failed to load inventory history. Please try again.',
      }));
      toast({
        title: 'Error',
        description: 'Failed to load inventory history',
        variant: 'destructive',
      });
    }
  }, [inventoryHistory.page, inventoryHistory.per_page, inventoryChangeTypeFilter, inventoryDateRange, getDateRangeForFilter, toast]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  useEffect(() => {
    fetchInventoryHistory();
  }, [fetchInventoryHistory]);

  const formatDateTime = (dateTimeStr: string | null) => {
    if (!dateTimeStr) return '';
    const date = new Date(dateTimeStr);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  };

  // Format for CSV export (no commas to avoid breaking CSV columns)
  const formatDateTimeForCSV = (dateTimeStr: string | null) => {
    if (!dateTimeStr) return '';
    const date = new Date(dateTimeStr);
    return date.toISOString().replace('T', ' ').replace(/\..+/, '');
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'taken':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'missed':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'skipped':
        return <Clock className="h-5 w-5 text-yellow-500" />;
      default:
        return <Clock className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusAction = (status: string) => {
    switch (status) {
      case 'taken':
        return 'Taken';
      case 'missed':
        return 'Missed';
      case 'skipped':
        return 'Skipped';
      default:
        return status;
    }
  };

  const getChangeTypeIcon = (changeType: string) => {
    switch (changeType) {
      case 'added':
        return <ArrowUpCircle className="h-4 w-4 text-green-500" />;
      case 'consumed':
        return <ArrowDownCircle className="h-4 w-4 text-red-500" />;
      case 'adjusted':
        return <Settings className="h-4 w-4 text-blue-500" />;
      case 'expired':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      default:
        return <Package className="h-4 w-4 text-gray-500" />;
    }
  };

  const getChangeTypeLabel = (changeType: string) => {
    switch (changeType) {
      case 'added':
        return 'Added';
      case 'consumed':
        return 'Consumed';
      case 'adjusted':
        return 'Adjusted';
      case 'expired':
        return 'Expired';
      default:
        return changeType;
    }
  };

  const handlePageChange = (newPage: number) => {
    setHistory(prev => ({ ...prev, page: newPage }));
  };

  const handleInventoryPageChange = (newPage: number) => {
    setInventoryHistory(prev => ({ ...prev, page: newPage }));
  };

  const handleDateRangeChange = (value: DateRange) => {
    setDateRange(value);
    setHistory(prev => ({ ...prev, page: 1 }));
  };

  const handleStatusChange = (value: string) => {
    setStatusFilter(value);
    setHistory(prev => ({ ...prev, page: 1 }));
  };

  const handleInventoryChangeTypeChange = (value: string) => {
    setInventoryChangeTypeFilter(value);
    setInventoryHistory(prev => ({ ...prev, page: 1 }));
  };

  const handleInventoryDateRangeChange = (value: DateRange) => {
    setInventoryDateRange(value);
    setInventoryHistory(prev => ({ ...prev, page: 1 }));
  };

  const handleInventoryRowClick = (item: InventoryHistoryWithMedicine) => {
    setSelectedInventoryItem(item);
    setShowInventoryDetailModal(true);
  };

  const downloadFile = (content: string, filename: string, mimeType: string) => {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const exportToCSV = () => {
    const headers = ['Medicine', 'Status', 'Scheduled Time', 'Taken Time', 'Dosage'];
    const rows = history.items.map(item => [
      item.medicine_name,
      item.status,
      formatDateTimeForCSV(item.scheduled_time),
      formatDateTimeForCSV(item.taken_time),
      item.dosage
    ]);
    
    const csvContent = [headers.join(','), ...rows.map(row => row.join(','))]
      .join('\n');
    
    downloadFile(csvContent, `medication-history-${dateRange}.csv`, 'text/csv');
    
    toast({
      title: 'Export Complete',
      description: 'History exported as CSV',
    });
  };

  const exportToPDF = () => {
    const doc = new jsPDF();
    
    // Add title
    doc.setFontSize(18);
    doc.text('Medication History', 14, 22);
    
    // Add date range
    doc.setFontSize(11);
    doc.text(`Date Range: ${dateRange}`, 14, 32);
    doc.text(`Generated: ${new Date().toLocaleDateString()}`, 14, 38);
    
    // Prepare table data
    const tableData = history.items.map(item => [
      item.medicine_name,
      getStatusAction(item.status),
      formatDateTime(item.scheduled_time),
      formatDateTime(item.taken_time),
      item.dosage || '-'
    ]);
    
    // Add table
    autoTable(doc, {
      head: [['Medicine', 'Status', 'Scheduled Time', 'Taken Time', 'Dosage']],
      body: tableData,
      startY: 45,
      styles: { fontSize: 9 },
      headStyles: { fillColor: [59, 130, 246] },
    });
    
    // Save PDF
    doc.save(`medication-history-${dateRange}.pdf`);
    
    toast({
      title: 'Export Complete',
      description: 'History exported as PDF',
    });
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(history.items, null, 2));
      toast({
        title: 'Copied',
        description: 'JSON data copied to clipboard',
      });
    } catch (error) {
      console.error('Failed to copy:', error);
      toast({
        title: 'Error',
        description: 'Failed to copy to clipboard',
        variant: 'destructive',
      });
    }
  };

  const exportToText = () => {
    // Simple text-based export
    const headers = ['Medicine', 'Status', 'Scheduled Time', 'Taken Time', 'Dosage'];
    const content = history.items.map(item => 
      `${item.medicine_name} | ${item.status} | ${formatDateTime(item.scheduled_time)} | ${formatDateTime(item.taken_time)} | ${item.dosage}`
    ).join('\n');
    
    const fullContent = `MEDICATION HISTORY\n${'='.repeat(50)}\nDate Range: ${dateRange}\n\n${headers.join(',')}\n${'─'.repeat(50)}\n${content}`;
    
    downloadFile(fullContent, `medication-history-${dateRange}.txt`, 'text/plain');
    
    toast({
      title: 'Export Complete',
      description: 'History exported as text file',
    });
  };

  // Inventory History Export Functions
  const exportInventoryToCSV = () => {
    const headers = ['Medicine', 'Type', 'Amount', 'Previous Stock', 'New Stock', 'Notes', 'Date'];
    const rows = inventoryHistory.items.map(item => [
      item.medicine_name,
      getChangeTypeLabel(item.change_type),
      String(item.change_amount),
      String(item.previous_stock),
      String(item.new_stock),
      item.notes || '',
      formatDateTimeForCSV(item.created_at)
    ]);
    
    const csvContent = [headers.join(','), ...rows.map(row => row.join(','))]
      .join('\n');
    
    downloadFile(csvContent, `inventory-history-${inventoryDateRange}.csv`, 'text/csv');
    
    toast({
      title: 'Export Complete',
      description: 'Inventory history exported as CSV',
    });
  };

  const exportInventoryToPDF = () => {
    const doc = new jsPDF();
    
    // Add title
    doc.setFontSize(18);
    doc.text('Inventory History', 14, 22);
    
    // Add date range
    doc.setFontSize(11);
    doc.text(`Date Range: ${inventoryDateRange}`, 14, 32);
    doc.text(`Generated: ${new Date().toLocaleDateString()}`, 14, 38);
    
    // Prepare table data
    const tableData = inventoryHistory.items.map(item => [
      item.medicine_name,
      getChangeTypeLabel(item.change_type),
      String(item.change_amount),
      String(item.previous_stock),
      String(item.new_stock),
      item.notes || '-',
      formatDateTime(item.created_at)
    ]);
    
    // Add table
    autoTable(doc, {
      head: [['Medicine', 'Type', 'Amount', 'Previous', 'New', 'Notes', 'Date']],
      body: tableData,
      startY: 45,
      styles: { fontSize: 9 },
      headStyles: { fillColor: [59, 130, 246] },
    });
    
    // Save PDF
    doc.save(`inventory-history-${inventoryDateRange}.pdf`);
    
    toast({
      title: 'Export Complete',
      description: 'Inventory history exported as PDF',
    });
  };

  const copyInventoryToClipboard = () => {
    setJsonModalType('inventory');
    setShowJsonModal(true);
  };

  const exportInventoryToText = () => {
    // Simple text-based export
    const headers = ['Medicine', 'Type', 'Amount', 'Previous', 'New', 'Notes', 'Date'];
    const content = inventoryHistory.items.map(item => 
      `${item.medicine_name} | ${getChangeTypeLabel(item.change_type)} | ${item.change_amount} | ${item.previous_stock} | ${item.new_stock} | ${item.notes || '-'} | ${formatDateTime(item.created_at)}`
    ).join('\n');
    
    const fullContent = `INVENTORY HISTORY\n${'='.repeat(50)}\nDate Range: ${inventoryDateRange}\n\n${headers.join(',')}\n${'─'.repeat(50)}\n${content}`;
    
    downloadFile(fullContent, `inventory-history-${inventoryDateRange}.txt`, 'text/plain');
    
    toast({
      title: 'Export Complete',
      description: 'Inventory history exported as text file',
    });
  };

  const showInventoryJsonModal = () => {
    setShowJsonModal(true);
  };

  return (
    <div className="space-y-6">
      <PageHeader title="History" description="View your medication history and inventory expenditures" />

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Left Column: Medication History */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <History className="h-5 w-5" />
              Medication History
            </CardTitle>
          </CardHeader>
          <CardContent>
            {/* Medication History Filters */}
            <div className="flex gap-2 mb-4">
              <Select value={dateRange} onValueChange={handleDateRangeChange}>
                <SelectTrigger className="w-auto">
                  <Calendar className="h-4 w-4 mr-2" />
                  <SelectValue placeholder="Date Range" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="week">Current Week</SelectItem>
                  <SelectItem value="month">Current Month</SelectItem>
                  <SelectItem value="3months">Last 3 Months</SelectItem>
                  <SelectItem value="6months">Last 6 Months</SelectItem>
                  <SelectItem value="year">Current Year</SelectItem>
                  <SelectItem value="all">All Time</SelectItem>
                </SelectContent>
              </Select>

              <Select value={statusFilter} onValueChange={handleStatusChange}>
                <SelectTrigger className="w-[130px]">
                  <Filter className="h-4 w-4 mr-2" />
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="taken">Taken</SelectItem>
                  <SelectItem value="skipped">Skipped</SelectItem>
                  <SelectItem value="missed">Missed</SelectItem>
                </SelectContent>
              </Select>

              <Button variant="outline" size="icon" onClick={fetchHistory} disabled={history.loading}>
                {history.loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <RotateCw className="h-4 w-4" />}
                <span className="sr-only">Refresh</span>
              </Button>

              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="icon">
                    <Download className="h-4 w-4" />
                    <span className="sr-only">Export</span>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuItem onClick={exportToCSV}>
                    <FileSpreadsheet className="h-4 w-4 mr-2" />
                    Export as CSV
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={exportToPDF}>
                    <FileText className="h-4 w-4 mr-2" />
                    Export as PDF
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={exportToText}>
                    <FileText className="h-4 w-4 mr-2" />
                    Export as Text
                  </DropdownMenuItem>
                  <DropdownMenuItem 
                    onClick={() => {
                      setJsonModalType('medication');
                      setShowJsonModal(true);
                    }}
                  >
                    <FileJson className="h-4 w-4 mr-2" />
                    Show JSON
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>

            {history.loading ? (
              <div className="flex justify-center items-center py-8">
                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
              </div>
            ) : history.error ? (
              <div className="text-center py-8 text-red-500">
                {history.error}
              </div>
            ) : history.items.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No medication history found for the selected filters.
              </div>
            ) : (
              <>
                <div className="space-y-3">
                  {history.items.map((item) => (
                    <div key={item.id} className="flex items-center gap-4 p-3 rounded-lg border">
                      {getStatusIcon(item.status)}
                      <div className="flex-1">
                        <p className="font-medium">{item.medicine_name}</p>
                        <p className="text-sm text-muted-foreground">
                          {getStatusAction(item.status)} at {formatDateTime(item.scheduled_time)}
                          {item.dosage && ` • ${item.dosage}`}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Pagination */}
                {history.pages > 1 && (
                  <div className="flex items-center justify-between mt-4 pt-4 border-t">
                    <p className="text-sm text-muted-foreground">
                      Page {history.page} of {history.pages} ({history.total} total)
                    </p>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handlePageChange(history.page - 1)}
                        disabled={history.page === 1}
                      >
                        Previous
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handlePageChange(history.page + 1)}
                        disabled={history.page === history.pages}
                      >
                        Next
                      </Button>
                    </div>
                  </div>
                )}
              </>
            )}
          </CardContent>
        </Card>

        {/* Right Column: Inventory History Table */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Package className="h-5 w-5" />
                Inventory History
              </CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            {/* Inventory History Filters */}
            <div className="flex gap-2 mb-4 flex-wrap">
              <Select value={inventoryDateRange} onValueChange={handleInventoryDateRangeChange}>
                <SelectTrigger className="w-auto">
                  <Calendar className="h-4 w-4 mr-2" />
                  <SelectValue placeholder="Date Range" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="week">Current Week</SelectItem>
                  <SelectItem value="month">Current Month</SelectItem>
                  <SelectItem value="3months">Last 3 Months</SelectItem>
                  <SelectItem value="6months">Last 6 Months</SelectItem>
                  <SelectItem value="year">Current Year</SelectItem>
                  <SelectItem value="all">All Time</SelectItem>
                </SelectContent>
              </Select>

              <Select value={inventoryChangeTypeFilter} onValueChange={handleInventoryChangeTypeChange}>
                <SelectTrigger className="w-[130px]">
                  <Filter className="h-4 w-4 mr-2" />
                  <SelectValue placeholder="Type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  <SelectItem value="added">Added</SelectItem>
                  <SelectItem value="consumed">Consumed</SelectItem>
                  <SelectItem value="adjusted">Adjusted</SelectItem>
                  <SelectItem value="expired">Expired</SelectItem>
                </SelectContent>
              </Select>

              <Button 
                variant="outline" 
                size="icon" 
                onClick={fetchInventoryHistory}
                disabled={inventoryHistory.loading}
              >
                {inventoryHistory.loading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <RotateCw className="h-4 w-4" />
                )}
                <span className="sr-only">Refresh</span>
              </Button>

              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="icon">
                    <Download className="h-4 w-4" />
                    <span className="sr-only">Export</span>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuItem onClick={exportInventoryToCSV}>
                    <FileSpreadsheet className="h-4 w-4 mr-2" />
                    Export as CSV
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={exportInventoryToPDF}>
                    <FileText className="h-4 w-4 mr-2" />
                    Export as PDF
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={exportInventoryToText}>
                    <FileText className="h-4 w-4 mr-2" />
                    Export as Text
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={copyInventoryToClipboard}>
                    <FileJson className="h-4 w-4 mr-2" />
                    Copy JSON
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>

            {inventoryHistory.loading ? (
              <div className="flex justify-center items-center py-8">
                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
              </div>
            ) : inventoryHistory.error ? (
              <div className="text-center py-8 text-red-500">
                {inventoryHistory.error}
              </div>
            ) : inventoryHistory.items.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No inventory history found.
              </div>
            ) : (
              <>
                <div className="rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Medicine</TableHead>
                        {/* <TableHead>Type</TableHead> */}
                        <TableHead>Amount</TableHead>
                        {/* <TableHead>Previous</TableHead> */}
                        <TableHead>New</TableHead>
                        {/* <TableHead>Notes</TableHead> */}
                        <TableHead>Date</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {inventoryHistory.items.map((item) => (
                        <TableRow 
                          key={item.id} 
                          className="cursor-pointer hover:bg-muted/50"
                          onClick={() => handleInventoryRowClick(item)}
                        >
                          <TableCell className="font-medium">{item.medicine_name}</TableCell>
                          {/* <TableCell>
                            <div className="flex items-center gap-1">
                              {getChangeTypeIcon(item.change_type)}
                              <span>{getChangeTypeLabel(item.change_type)}</span>
                            </div>
                          </TableCell> */}
                          <TableCell className={item.change_amount > 0 ? 'text-green-500' : item.change_amount < 0 ? 'text-red-500' : ''}>
                            {item.change_amount > 0 ? '+' : ''}{item.change_amount}
                          </TableCell>
                          {/* <TableCell>{item.previous_stock}</TableCell> */}
                          <TableCell>{item.new_stock}</TableCell>
                          {/* <TableCell className="max-w-[150px] truncate" title={item.notes || undefined}>
                            {item.notes || '-'}
                          </TableCell> */}
                          <TableCell className="text-sm text-muted-foreground">
                            {formatDateTime(item.created_at)}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>

                {/* Pagination */}
                {inventoryHistory.pages > 1 && (
                  <div className="flex items-center justify-between mt-4 pt-4 border-t">
                    <p className="text-sm text-muted-foreground">
                      Page {inventoryHistory.page} of {inventoryHistory.pages} ({inventoryHistory.total} total)
                    </p>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleInventoryPageChange(inventoryHistory.page - 1)}
                        disabled={inventoryHistory.page === 1}
                      >
                        Previous
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleInventoryPageChange(inventoryHistory.page + 1)}
                        disabled={inventoryHistory.page === inventoryHistory.pages}
                      >
                        Next
                      </Button>
                    </div>
                  </div>
                )}
              </>
            )}
          </CardContent>
        </Card>

      </div>

      {/* JSON Modal */}
      <Dialog open={showJsonModal} onOpenChange={setShowJsonModal}>
        <DialogContent className="max-w-2xl [&_button.absolute]:hidden">
          <DialogHeader>
            <div className="flex items-center justify-between">
              <DialogTitle className="flex items-center gap-2">
                <FileJson className="h-5 w-5" />
                {jsonModalType === 'medication' ? 'Medication History (JSON)' : 'Inventory History (JSON)'}
              </DialogTitle>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => {
                  const content = jsonModalType === 'medication' 
                    ? JSON.stringify(history.items, null, 2) 
                    : JSON.stringify(inventoryHistory.items, null, 2);
                  navigator.clipboard.writeText(content);
                  toast({
                    title: 'Copied',
                    description: 'JSON data copied to clipboard',
                  });
                }}
              >
                <Copy className="h-4 w-4 mr-2" />
                Copy
              </Button>
            </div>
          </DialogHeader>
          <ScrollArea className="h-96">
            <pre className="text-sm bg-muted p-4 rounded-lg overflow-x-auto">
              {jsonModalType === 'medication' 
                ? JSON.stringify(history.items, null, 2) 
                : JSON.stringify(inventoryHistory.items, null, 2)}
            </pre>
          </ScrollArea>
        </DialogContent>
      </Dialog>

      {/* Inventory History Detail Modal */}
      <Dialog open={showInventoryDetailModal} onOpenChange={setShowInventoryDetailModal}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Package className="h-5 w-5" />
              Inventory History Details
            </DialogTitle>
          </DialogHeader>
          {selectedInventoryItem && (
            <div className="space-y-4">
              <div className="rounded-lg bg-slate-100 dark:bg-slate-800 border-0">
                <Table>
                  <TableBody>
                    <TableRow>
                      <TableCell className="font-medium text-muted-foreground w-1/3">Medicine</TableCell>
                      <TableCell className="font-medium">{selectedInventoryItem.medicine_name}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell className="font-medium text-muted-foreground">Type</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          {getChangeTypeIcon(selectedInventoryItem.change_type)}
                          <span>{getChangeTypeLabel(selectedInventoryItem.change_type)}</span>
                        </div>
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell className="font-medium text-muted-foreground">Amount</TableCell>
                      <TableCell className={selectedInventoryItem.change_amount > 0 ? 'text-green-500 font-medium' : selectedInventoryItem.change_amount < 0 ? 'text-red-500 font-medium' : ''}>
                        {selectedInventoryItem.change_amount > 0 ? '+' : ''}{selectedInventoryItem.change_amount}
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell className="font-medium text-muted-foreground">Previous Stock</TableCell>
                      <TableCell>{selectedInventoryItem.previous_stock}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell className="font-medium text-muted-foreground">New Stock</TableCell>
                      <TableCell>{selectedInventoryItem.new_stock}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell className="font-medium text-muted-foreground">Date</TableCell>
                      <TableCell>{formatDateTime(selectedInventoryItem.created_at)}</TableCell>
                    </TableRow>
                    {selectedInventoryItem.notes && (
                      <TableRow>
                        <TableCell className="font-medium text-muted-foreground">Notes</TableCell>
                        <TableCell>{selectedInventoryItem.notes}</TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
