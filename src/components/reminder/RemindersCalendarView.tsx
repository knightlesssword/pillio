import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { remindersApi, type ApiReminderWithMedicine } from '@/lib/reminders-api';

interface RemindersCalendarViewProps {
  onReminderClick?: (reminder: ApiReminderWithMedicine) => void;
}

export function RemindersCalendarView({ onReminderClick }: RemindersCalendarViewProps) {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [reminders, setReminders] = useState<ApiReminderWithMedicine[]>([]);
  const [loading, setLoading] = useState(true);

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const firstDayOfMonth = new Date(year, month, 1).getDay();

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const fetchReminders = async () => {
    try {
      setLoading(true);
      const response = await remindersApi.list({ per_page: 100 });
      setReminders(response.data.items);
    } catch (error) {
      console.error('Failed to fetch reminders:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReminders();
  }, []);

  const getRemindersForDay = (day: number) => {
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    return reminders.filter(r => {
      const startDate = new Date(r.start_date);
      const endDate = r.end_date ? new Date(r.end_date) : null;
      const targetDate = new Date(dateStr);
      
      if (targetDate < startDate) return false;
      if (endDate && targetDate > endDate) return false;
      
      // Check frequency
      if (r.frequency === 'daily') return true;
      if (r.frequency === 'specific_days' && r.specific_days?.includes(targetDate.getDay())) return true;
      if (r.frequency === 'interval') return true;
      
      return false;
    });
  };

  const prevMonth = () => {
    setCurrentDate(new Date(year, month - 1, 1));
  };

  const nextMonth = () => {
    setCurrentDate(new Date(year, month + 1, 1));
  };

  const formatTime = (timeStr: string) => {
    const [hours, minutes] = timeStr.split(':');
    return `${hours}:${minutes}`;
  };

  // Generate calendar days
  const days: (number | null)[] = [];
  for (let i = 0; i < firstDayOfMonth; i++) {
    days.push(null);
  }
  for (let i = 1; i <= daysInMonth; i++) {
    days.push(i);
  }

  const today = new Date();
  const isToday = (day: number) => {
    return day === today.getDate() && 
           month === today.getMonth() && 
           year === today.getFullYear();
  };

  return (
    <Card className="animate-in slide-in-from-bottom-4 duration-300">
      <CardHeader className="flex flex-row items-center justify-between animate-in fade-in-50 delay-150 duration-300">
        <CardTitle className="text-lg font-semibold">
          {monthNames[month]} {year}
        </CardTitle>
        <div className="flex gap-2">
          <Button variant="outline" size="icon" onClick={prevMonth}>
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="icon" onClick={nextMonth}>
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="animate-in fade-in-50 delay-150 duration-300">
        {/* Day headers */}
        <div className="grid grid-cols-7 gap-1 mb-2">
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
            <div key={day} className="text-center text-sm font-medium text-muted-foreground py-2">
              {day}
            </div>
          ))}
        </div>

        {/* Calendar grid */}
        <div className="grid grid-cols-7 gap-1">
          {days.map((day, index) => {
            const dayReminders = day ? getRemindersForDay(day) : [];
            const isCurrentToday = day ? isToday(day) : false;

            return (
              <div
                key={index}
                className={cn(
                  'min-h-[80px] p-2 border rounded-lg',
                  day === null ? 'bg-muted/30' : 'bg-card',
                  isCurrentToday && 'border-primary border-2'
                )}
              >
                {day && (
                  <>
                    <div className={cn(
                      'text-sm font-medium mb-1',
                      isCurrentToday && 'text-primary'
                    )}>
                      {day}
                    </div>
                    <div className="space-y-1">
                      {dayReminders.slice(0, 3).map((reminder) => (
                        <div
                          key={reminder.id}
                          onClick={() => onReminderClick?.(reminder)}
                          className={cn(
                            'text-xs p-1 rounded cursor-pointer truncate',
                            reminder.is_active 
                              ? 'bg-primary/10 text-primary hover:bg-primary/20' 
                              : 'bg-muted text-muted-foreground'
                          )}
                        >
                          <div className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {formatTime(reminder.reminder_time)}
                          </div>
                          <div className="truncate">{reminder.medicine?.name}</div>
                        </div>
                      ))}
                      {dayReminders.length > 3 && (
                        <div className="text-xs text-muted-foreground text-center">
                          +{dayReminders.length - 3} more
                        </div>
                      )}
                    </div>
                  </>
                )}
              </div>
            );
          })}
        </div>

        {/* Legend */}
        <div className="flex gap-4 mt-4 pt-4 border-t">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-primary/20 border border-primary" />
            <span className="text-sm text-muted-foreground">Active</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-muted" />
            <span className="text-sm text-muted-foreground">Inactive</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded border-2 border-primary" />
            <span className="text-sm text-muted-foreground">Today</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
