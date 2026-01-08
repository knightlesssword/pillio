import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Clock, Check, X, Bell, ChevronRight, Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn, formatTime } from '@/lib/utils';
import { ROUTES } from '@/lib/constants';
import { remindersApi, type ReminderWithStatus } from '@/lib/reminders-api';
import { useToast } from '@/hooks/use-toast';

interface ReminderDisplay {
  id: number;
  medicineName: string;
  dosage: string;
  time: Date;
  status: 'pending' | 'taken' | 'missed' | 'upcoming' | 'skipped';
  is_pending: boolean;
}

function ReminderItem({ 
  reminder, 
  onTake, 
  onSkip 
}: { 
  reminder: ReminderDisplay; 
  onTake: (id: number) => void;
  onSkip: (id: number) => void;
}) {
  const statusConfig = {
    taken: {
      badge: 'Taken',
      badgeClass: 'bg-success/10 text-success border-success/20',
      icon: <Check className="h-4 w-4" />,
    },
    pending: {
      badge: 'Due Now',
      badgeClass: 'bg-accent/10 text-accent border-accent/20',
      icon: <Bell className="h-4 w-4" />,
    },
    missed: {
      badge: 'Missed',
      badgeClass: 'bg-destructive/10 text-destructive border-destructive/20',
      icon: <X className="h-4 w-4" />,
    },
    upcoming: {
      badge: 'Upcoming',
      badgeClass: 'bg-muted text-muted-foreground',
      icon: <Clock className="h-4 w-4" />,
    },
  };

  const config = statusConfig[reminder.status as keyof typeof statusConfig] || statusConfig.upcoming;

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      className={cn(
        'flex items-center gap-4 p-4 rounded-lg border transition-all',
        reminder.status === 'pending' ? 'bg-accent/5 border-accent/20' : 'bg-card border-border hover:bg-muted/50'
      )}
    >
      <div
        className={cn(
          'w-10 h-10 rounded-full flex items-center justify-center',
          reminder.status === 'taken' ? 'bg-success/10 text-success' :
          reminder.status === 'pending' ? 'bg-accent/10 text-accent' :
          reminder.status === 'missed' ? 'bg-destructive/10 text-destructive' :
          'bg-muted text-muted-foreground'
        )}
      >
        {config.icon}
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <h4 className="font-medium text-foreground truncate">{reminder.medicineName}</h4>
          <Badge variant="outline" className={config.badgeClass}>
            {config.badge}
          </Badge>
        </div>
        <p className="text-sm text-muted-foreground">{reminder.dosage}</p>
      </div>

      <div className="text-right">
        <p className="text-sm font-medium text-foreground">{formatTime(reminder.time)}</p>
      </div>

      {reminder.status === 'pending' && (
        <div className="flex gap-2">
          <Button 
            size="sm" 
            variant="outline" 
            className="h-8"
            onClick={() => onSkip(reminder.id)}
          >
            Skip
          </Button>
          <Button 
            size="sm" 
            className="h-8 gradient-primary"
            onClick={() => onTake(reminder.id)}
          >
            Take
          </Button>
        </div>
      )}
    </motion.div>
  );
}

export default function UpcomingReminders() {
  const [reminders, setReminders] = useState<ReminderDisplay[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<number | null>(null);
  const { toast } = useToast();

  const fetchReminders = async () => {
    try {
      setLoading(true);
      const response = await remindersApi.getTodayWithStatus();
      const data = response.data;
      
      const formatted: ReminderDisplay[] = data.map((r) => ({
        id: r.id,
        medicineName: r.medicineName,
        dosage: r.dosage || 'As prescribed',
        time: new Date(r.time),
        status: r.is_pending ? 'pending' : (r.status === 'upcoming' ? 'upcoming' : r.status),
        is_pending: r.is_pending,
      }));
      
      setReminders(formatted);
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

  const handleTake = async (id: number) => {
    try {
      setActionLoading(id);
      await remindersApi.markTaken(id);
      toast({
        title: 'Success',
        description: 'Reminder marked as taken',
      });
      fetchReminders();
    } catch (error) {
      console.error('Failed to mark as taken:', error);
      toast({
        title: 'Error',
        description: 'Failed to update reminder',
        variant: 'destructive',
      });
    } finally {
      setActionLoading(null);
    }
  };

  const handleSkip = async (id: number) => {
    try {
      setActionLoading(id);
      await remindersApi.markSkipped(id);
      toast({
        title: 'Success',
        description: 'Reminder skipped',
      });
      fetchReminders();
    } catch (error) {
      console.error('Failed to skip:', error);
      toast({
        title: 'Error',
        description: 'Failed to update reminder',
        variant: 'destructive',
      });
    } finally {
      setActionLoading(null);
    }
  };

  return (
    <Card className="h-full">
      <CardHeader className="flex flex-row items-center justify-between pb-4">
        <CardTitle className="text-lg font-semibold">Today's Schedule</CardTitle>
        <Link to={ROUTES.REMINDERS}>
          <Button variant="ghost" size="sm" className="text-primary">
            View All
            <ChevronRight className="h-4 w-4 ml-1" />
          </Button>
        </Link>
      </CardHeader>
      <CardContent className="space-y-3">
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : reminders.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            No reminders scheduled for today
          </div>
        ) : (
          reminders.map((reminder, index) => (
            <motion.div
              key={reminder.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <ReminderItem 
                reminder={reminder} 
                onTake={handleTake}
                onSkip={handleSkip}
              />
            </motion.div>
          ))
        )}
      </CardContent>
    </Card>
  );
}
