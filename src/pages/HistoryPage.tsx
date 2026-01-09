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
  Copy
} from 'lucide-react';
import { remindersApi, type ReminderHistoryItem, type ReminderHistoryResponse } from '@/lib/reminders-api';
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

export default function HistoryPage() {
  const { toast } = useToast();
  const [dateRange, setDateRange] = useState<DateRange>('week');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [showJsonModal, setShowJsonModal] = useState(false);
  const [history, setHistory] = useState<HistoryState>({
    items: [],
    total: 0,
    page: 1,
    per_page: 20,
    pages: 0,
    loading: false,
    error: null,
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

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

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
        return <CheckCircle className="h-5 w-5 text-success" />;
      case 'missed':
        return <XCircle className="h-5 w-5 text-destructive" />;
      case 'skipped':
        return <Clock className="h-5 w-5 text-warning" />;
      default:
        return <Clock className="h-5 w-5 text-muted-foreground" />;
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

  const handlePageChange = (newPage: number) => {
    setHistory(prev => ({ ...prev, page: newPage }));
  };

  const handleDateRangeChange = (value: DateRange) => {
    setDateRange(value);
    setHistory(prev => ({ ...prev, page: 1 }));
  };

  const handleStatusChange = (value: string) => {
    setStatusFilter(value);
    setHistory(prev => ({ ...prev, page: 1 }));
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

  return (
    <div className="space-y-6">
      <PageHeader title="History" description="View your medication history and adherence" />

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="w-full sm:w-48">
          <Select value={dateRange} onValueChange={handleDateRangeChange}>
            <SelectTrigger>
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
        </div>

        <div className="w-full sm:w-48">
          <Select value={statusFilter} onValueChange={handleStatusChange}>
            <SelectTrigger>
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
        </div>

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
            <DropdownMenuItem onClick={() => setShowJsonModal(true)}>
              <FileJson className="h-4 w-4 mr-2" />
              Show JSON
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* History Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <History className="h-5 w-5" />
            Medication History
          </CardTitle>
        </CardHeader>
        <CardContent>
          {history.loading ? (
            <div className="flex justify-center items-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : history.error ? (
            <div className="text-center py-8 text-destructive">
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
                    {/* {item.taken_time && (
                      <p className="text-xs text-muted-foreground">
                        Taken: {formatDateTime(item.taken_time)}
                      </p>
                    )} */}
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

      {/* JSON Modal */}
      <Dialog open={showJsonModal} onOpenChange={setShowJsonModal}>
        <DialogContent className="max-w-2xl [&_button.absolute]:hidden">
          <DialogHeader>
            <div className="flex items-center justify-between">
              <DialogTitle className="flex items-center gap-2">
                <FileJson className="h-5 w-5" />
                History Data (JSON)
              </DialogTitle>
              <Button variant="outline" size="sm" onClick={copyToClipboard}>
                <Copy className="h-4 w-4 mr-2" />
                Copy
              </Button>
            </div>
          </DialogHeader>
          <ScrollArea className="h-96">
            <pre className="text-sm bg-muted p-4 rounded-lg overflow-x-auto">
              {JSON.stringify(history.items, null, 2)}
            </pre>
          </ScrollArea>
        </DialogContent>
      </Dialog>
    </div>
  );
}
