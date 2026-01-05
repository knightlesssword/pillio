import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Clock, Check, X, Bell, ChevronRight } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn, formatTime } from '@/lib/utils';
import { ROUTES } from '@/lib/constants';

interface Reminder {
  id: string;
  medicineName: string;
  dosage: string;
  time: Date;
  status: 'pending' | 'taken' | 'missed' | 'upcoming';
}

// Mock data
const mockReminders: Reminder[] = [
  {
    id: '1',
    medicineName: 'Aspirin',
    dosage: '1 tablet (100mg)',
    time: new Date(new Date().setHours(8, 0)),
    status: 'taken',
  },
  {
    id: '2',
    medicineName: 'Vitamin D3',
    dosage: '1 capsule (1000 IU)',
    time: new Date(new Date().setHours(9, 0)),
    status: 'taken',
  },
  {
    id: '3',
    medicineName: 'Metformin',
    dosage: '1 tablet (500mg)',
    time: new Date(new Date().setHours(13, 0)),
    status: 'pending',
  },
  {
    id: '4',
    medicineName: 'Lisinopril',
    dosage: '1 tablet (10mg)',
    time: new Date(new Date().setHours(18, 0)),
    status: 'upcoming',
  },
  {
    id: '5',
    medicineName: 'Omega-3',
    dosage: '2 capsules',
    time: new Date(new Date().setHours(21, 0)),
    status: 'upcoming',
  },
];

function ReminderItem({ reminder }: { reminder: Reminder }) {
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

  const config = statusConfig[reminder.status];

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
          <Button size="sm" variant="outline" className="h-8">
            Skip
          </Button>
          <Button size="sm" className="h-8 gradient-primary">
            Take
          </Button>
        </div>
      )}
    </motion.div>
  );
}

export default function UpcomingReminders() {
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
        {mockReminders.map((reminder, index) => (
          <motion.div
            key={reminder.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
          >
            <ReminderItem reminder={reminder} />
          </motion.div>
        ))}
      </CardContent>
    </Card>
  );
}
