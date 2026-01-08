import React, { useState, useEffect } from 'react';
import PageHeader from '@/components/common/PageHeader';
import { Button } from '@/components/ui/button';
import { Plus, Calendar, List, Loader2, Edit, Trash2, Clock } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Loader2 as LoaderIcon } from 'lucide-react';
import UpcomingReminders from '@/components/dashboard/UpcomingReminders';
import { ReminderFormDialog } from '@/components/reminder/ReminderFormDialog';
import { DeleteReminderDialog } from '@/components/reminder/DeleteReminderDialog';
import { RemindersCalendarView } from '@/components/reminder/RemindersCalendarView';
import { remindersApi, type ApiReminderWithMedicine } from '@/lib/reminders-api';
import { useToast } from '@/hooks/use-toast';
import { cn } from '@/lib/utils';

export default function RemindersPage() {
  const [reminders, setReminders] = useState<ApiReminderWithMedicine[]>([]);
  const [loading, setLoading] = useState(true);
  const [formDialogOpen, setFormDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [editingReminder, setEditingReminder] = useState<ApiReminderWithMedicine | null>(null);
  const [deletingReminder, setDeletingReminder] = useState<{ id: number; name: string } | null>(null);
  const { toast } = useToast();

  const fetchReminders = async () => {
    try {
      setLoading(true);
      const response = await remindersApi.list({ per_page: 100 });
      setReminders(response.data.items);
    } catch (error) {
      console.error('Failed to fetch reminders:', error);
      toast({
        title: 'Error',
        description: 'Failed to load reminders',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReminders();
  }, []);

  const handleCreate = () => {
    setEditingReminder(null);
    setFormDialogOpen(true);
  };

  const handleEdit = (reminder: ApiReminderWithMedicine) => {
    setEditingReminder(reminder);
    setFormDialogOpen(true);
  };

  const handleDeleteClick = (reminder: ApiReminderWithMedicine) => {
    setDeletingReminder({ id: reminder.id, name: reminder.medicine?.name || 'Unknown' });
    setDeleteDialogOpen(true);
  };

  const formatTime = (timeStr: string) => {
    const [hours, minutes] = timeStr.split(':');
    return `${hours}:${minutes}`;
  };

  const getFrequencyLabel = (freq: string, interval_days?: number) => {
    switch (freq) {
      case 'daily': return 'Daily';
      case 'specific_days': return 'Specific Days';
      case 'interval': return interval_days ? `Every ${interval_days} Days` : 'Every X Days';
      default: return freq;
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader title="Reminders" description="Manage your medication reminders">
        <Button className="gradient-primary" onClick={handleCreate}>
          <Plus className="h-4 w-4 mr-2" />
          Add Reminder
        </Button>
      </PageHeader>

      <Tabs defaultValue="list" className="space-y-4">
        <TabsList>
          <TabsTrigger value="list" className="gap-2">
            <List className="h-4 w-4" />
            List
          </TabsTrigger>
          <TabsTrigger value="calendar" className="gap-2">
            <Calendar className="h-4 w-4" />
            Calendar
          </TabsTrigger>
        </TabsList>

        <TabsContent value="list" className="animate-in fade-in-50 duration-300">
          <Card className="animate-in slide-in-from-bottom-4 duration-300">
            <CardHeader>
              <CardTitle>All Reminders</CardTitle>
            </CardHeader>
            <CardContent className="animate-in fade-in-50 delay-150 duration-300">
              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <LoaderIcon className="h-6 w-6 animate-spin text-muted-foreground" />
                </div>
              ) : reminders.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No reminders found. Click "Add Reminder" to create one.
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Medicine</TableHead>
                      <TableHead>Time</TableHead>
                      <TableHead>Frequency</TableHead>
                      <TableHead>Dosage</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {reminders.map((reminder) => (
                      <TableRow key={reminder.id}>
                        <TableCell>
                          <div>
                            <p className="font-medium">{reminder.medicine?.name || 'Unknown'}</p>
                            <p className="text-sm text-muted-foreground">
                              {reminder.start_date} → {reminder.end_date || 'Ongoing'}
                            </p>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Clock className="h-4 w-4 text-muted-foreground" />
                            {formatTime(reminder.reminder_time)}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">
                            {getFrequencyLabel(reminder.frequency, reminder.interval_days)}
                          </Badge>
                          {reminder.frequency === 'specific_days' && reminder.specific_days && (
                            <p className="text-xs text-muted-foreground mt-1">
                              {reminder.specific_days.map(d => ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'][d]).join(', ')}
                            </p>
                          )}
                        </TableCell>
                        <TableCell>
                          {reminder.dosage_amount && (
                            <span>{reminder.dosage_amount} {reminder.dosage_unit}</span>
                          )}
                        </TableCell>
                        <TableCell>
                          <Badge 
                            variant={reminder.is_active ? "default" : "secondary"}
                            className={cn(
                              "pointer-events-none cursor-default",
                              reminder.is_active ? "bg-success/10 text-success" : "bg-muted"
                            )}
                          >
                            {reminder.is_active ? 'Active' : 'Inactive'}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="flex justify-end gap-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleEdit(reminder)}
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-destructive hover:text-destructive"
                              onClick={() => handleDeleteClick(reminder)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="calendar" className="animate-in fade-in-50 duration-300">
          <RemindersCalendarView 
            onReminderClick={(reminder) => handleEdit(reminder)}
          />
        </TabsContent>

        <TabsContent value="today">
          <UpcomingReminders />
        </TabsContent>
      </Tabs>

      {/* Create/Edit Dialog */}
      <ReminderFormDialog
        open={formDialogOpen}
        onOpenChange={setFormDialogOpen}
        reminder={editingReminder}
        onSuccess={fetchReminders}
      />

      {/* Delete Confirmation Dialog */}
      {deletingReminder && (
        <DeleteReminderDialog
          open={deleteDialogOpen}
          onOpenChange={setDeleteDialogOpen}
          reminderId={deletingReminder.id}
          reminderName={deletingReminder.name}
          onSuccess={fetchReminders}
        />
      )}
    </div>
  );
}

