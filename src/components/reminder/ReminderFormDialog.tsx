import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { getErrorMessage } from '@/lib/api';
import remindersApi, { type ReminderCreate, type ReminderUpdate, type ApiReminderWithMedicine } from '@/lib/reminders-api';
import medicinesApi, { type ApiMedicine } from '@/lib/medicines-api';

interface ReminderFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  reminder?: ApiReminderWithMedicine | null;
  onSuccess: () => void;
}

interface ReminderFormData {
  medicine_id: string;
  reminder_time: string;
  frequency: 'daily' | 'specific_days' | 'interval';
  specific_days: number[];
  interval_days: number;
  dosage_amount: string;
  dosage_unit: string;
  start_date: string;
  end_date: string;
  is_active: boolean;
  notes: string;
}

const INITIAL_FORM: ReminderFormData = {
  medicine_id: '',
  reminder_time: '08:00',
  frequency: 'daily',
  specific_days: [],
  interval_days: 2,
  dosage_amount: '',
  dosage_unit: 'tablet',
  start_date: new Date().toISOString().split('T')[0],
  end_date: '',
  is_active: true,
  notes: '',
};

const FREQUENCIES = [
  { value: 'daily', label: 'Daily' },
  { value: 'specific_days', label: 'Specific Days' },
  { value: 'interval', label: 'Every X Days' },
];
const DAYS_OF_WEEK = [
  { value: 0, label: 'Sunday' },
  { value: 1, label: 'Monday' },
  { value: 2, label: 'Tuesday' },
  { value: 3, label: 'Wednesday' },
  { value: 4, label: 'Thursday' },
  { value: 5, label: 'Friday' },
  { value: 6, label: 'Saturday' },
];
const UNITS = ['tablet', 'capsule', 'ml', 'mg', 'drops', 'puffs', 'units'];

export function ReminderFormDialog({ open, onOpenChange, reminder, onSuccess }: ReminderFormDialogProps) {
  const [form, setForm] = useState<ReminderFormData>(INITIAL_FORM);
  const [medicines, setMedicines] = useState<ApiMedicine[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isFetchingMedicines, setIsFetchingMedicines] = useState(true);
  const { toast } = useToast();

  const isEditing = Boolean(reminder);

  useEffect(() => {
    const fetchMedicines = async () => {
      try {
        setIsFetchingMedicines(true);
        const response = await medicinesApi.list({ per_page: 100 });
        setMedicines(response.data.items);
      } catch (error) {
        console.error('Failed to fetch medicines:', error);
        toast({
          title: 'Error',
          description: 'Failed to load medicines',
          variant: 'destructive',
        });
      } finally {
        setIsFetchingMedicines(false);
      }
    };

    if (open) {
      fetchMedicines();
    }
  }, [open, toast]);

  useEffect(() => {
    if (reminder) {
      setForm({
        medicine_id: String(reminder.medicine_id),
        reminder_time: reminder.reminder_time.substring(0, 5),
        frequency: reminder.frequency as 'daily' | 'specific_days' | 'interval',
        specific_days: reminder.specific_days || [],
        interval_days: reminder.interval_days || 2,
        dosage_amount: reminder.dosage_amount || '',
        dosage_unit: reminder.dosage_unit || 'tablet',
        start_date: reminder.start_date,
        end_date: reminder.end_date || '',
        is_active: reminder.is_active,
        notes: reminder.notes || '',
      });
    } else {
      setForm(INITIAL_FORM);
    }
  }, [reminder, open]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      if (isEditing && reminder) {
        const updateData: ReminderUpdate = {
          reminder_time: form.reminder_time + ':00',
          frequency: form.frequency as 'daily' | 'specific_days' | 'interval',
          specific_days: form.specific_days.length > 0 ? form.specific_days : undefined,
          interval_days: form.frequency === 'interval' ? form.interval_days : undefined,
          dosage_amount: form.dosage_amount || undefined,
          dosage_unit: form.dosage_unit || undefined,
          start_date: form.start_date,
          end_date: form.end_date || undefined,
          is_active: form.is_active,
          notes: form.notes || undefined,
        };
        await remindersApi.update(reminder.id, updateData);
        toast({ title: 'Reminder updated', description: 'Reminder has been updated.' });
      } else {
        const createData: ReminderCreate = {
          medicine_id: parseInt(form.medicine_id),
          reminder_time: form.reminder_time + ':00',
          frequency: form.frequency as 'daily' | 'specific_days' | 'interval',
          specific_days: form.specific_days.length > 0 ? form.specific_days : undefined,
          interval_days: form.frequency === 'interval' ? form.interval_days : undefined,
          dosage_amount: form.dosage_amount || undefined,
          dosage_unit: form.dosage_unit || undefined,
          start_date: form.start_date,
          end_date: form.end_date || undefined,
          is_active: form.is_active,
          notes: form.notes || undefined,
        };
        await remindersApi.create(createData);
        toast({ title: 'Reminder created', description: 'Reminder has been created.' });
      }
      onSuccess();
      onOpenChange(false);
    } catch (error) {
      const message = getErrorMessage(error);
      toast({
        title: isEditing ? 'Error updating reminder' : 'Error creating reminder',
        description: message,
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const toggleDay = (day: number) => {
    setForm(prev => ({
      ...prev,
      specific_days: prev.specific_days.includes(day)
        ? prev.specific_days.filter(d => d !== day)
        : [...prev.specific_days, day]
    }));
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>{isEditing ? 'Edit Reminder' : 'Add New Reminder'}</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid gap-4">
            {/* Medicine Selection */}
            <div>
              <Label htmlFor="medicine">Medicine *</Label>
              {isFetchingMedicines ? (
                <div className="flex items-center gap-2 py-2 text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Loading medicines...
                </div>
              ) : (
                <Select
                  value={form.medicine_id}
                  onValueChange={(value) => setForm({ ...form, medicine_id: value })}
                  disabled={isEditing}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a medicine" />
                  </SelectTrigger>
                  <SelectContent>
                    {medicines.map((medicine) => (
                      <SelectItem key={medicine.id} value={String(medicine.id)}>
                        {medicine.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
            </div>

            {/* Time */}
            <div>
              <Label htmlFor="reminder_time">Time *</Label>
              <Input
                id="reminder_time"
                type="time"
                value={form.reminder_time}
                onChange={(e) => setForm({ ...form, reminder_time: e.target.value })}
                required
              />
            </div>

            {/* Frequency */}
            <div>
              <Label htmlFor="frequency">Frequency *</Label>
              <Select
                value={form.frequency}
                onValueChange={(value: 'daily' | 'specific_days' | 'interval') => setForm({ ...form, frequency: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {FREQUENCIES.map((freq) => (
                    <SelectItem key={freq.value} value={freq.value}>
                      {freq.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Days of Week (for specific_days) */}
            {form.frequency === 'specific_days' && (
              <div>
                <Label>Days of Week</Label>
                <div className="flex flex-wrap gap-2 mt-2">
                  {DAYS_OF_WEEK.map((day) => (
                    <Button
                      key={day.value}
                      type="button"
                      variant={form.specific_days.includes(day.value) ? "default" : "outline"}
                      size="sm"
                      onClick={() => toggleDay(day.value)}
                      className={form.specific_days.includes(day.value) ? "gradient-primary" : ""}
                    >
                      {day.label.slice(0, 3)}
                    </Button>
                  ))}
                </div>
              </div>
            )}

            {/* Interval Days (for interval) */}
            {form.frequency === 'interval' && (
              <div>
                <Label htmlFor="interval_days">Repeat every X days</Label>
                <Input
                  id="interval_days"
                  type="number"
                  min="1"
                  max="365"
                  value={form.interval_days}
                  onChange={(e) => setForm({ ...form, interval_days: parseInt(e.target.value) || 1 })}
                  className="mt-1"
                />
                <p className="text-sm text-muted-foreground mt-1">
                  Example: Enter 2 for every other day, 3 for every 3 days
                </p>
              </div>
            )}

            {/* Dosage */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="dosage_amount">Dosage Amount</Label>
                <Input
                  id="dosage_amount"
                  value={form.dosage_amount}
                  onChange={(e) => setForm({ ...form, dosage_amount: e.target.value })}
                  placeholder="e.g., 1"
                />
              </div>
              <div>
                <Label htmlFor="dosage_unit">Unit</Label>
                <Select
                  value={form.dosage_unit}
                  onValueChange={(value) => setForm({ ...form, dosage_unit: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {UNITS.map((unit) => (
                      <SelectItem key={unit} value={unit}>
                        {unit}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Date Range */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="start_date">Start Date *</Label>
                <Input
                  id="start_date"
                  type="date"
                  value={form.start_date}
                  onChange={(e) => setForm({ ...form, start_date: e.target.value })}
                  required
                />
              </div>
              <div>
                <Label htmlFor="end_date">End Date</Label>
                <Input
                  id="end_date"
                  type="date"
                  value={form.end_date}
                  onChange={(e) => setForm({ ...form, end_date: e.target.value })}
                />
              </div>
            </div>

            {/* Notes */}
            <div>
              <Label htmlFor="notes">Notes</Label>
              <Input
                id="notes"
                value={form.notes}
                onChange={(e) => setForm({ ...form, notes: e.target.value })}
                placeholder="Optional notes..."
              />
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)} disabled={isLoading}>
              Cancel
            </Button>
            <Button type="submit" className="gradient-primary" disabled={isLoading || isFetchingMedicines}>
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {isEditing ? 'Save Changes' : 'Create Reminder'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
