import React from 'react';
import { motion } from 'framer-motion';
import { Pill, Clock, CheckCircle, AlertTriangle, TrendingUp, TrendingDown } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface StatCardProps {
  title: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  icon: React.ReactNode;
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger';
}

function StatCard({ title, value, change, changeLabel, icon, variant = 'default' }: StatCardProps) {
  const variantStyles = {
    default: 'bg-card',
    primary: 'bg-primary/5 border-primary/20',
    success: 'bg-success/5 border-success/20',
    warning: 'bg-warning/5 border-warning/20',
    danger: 'bg-destructive/5 border-destructive/20',
  };

  const iconStyles = {
    default: 'bg-muted text-muted-foreground',
    primary: 'bg-primary/10 text-primary',
    success: 'bg-success/10 text-success',
    warning: 'bg-warning/10 text-warning',
    danger: 'bg-destructive/10 text-destructive',
  };

  return (
    <Card className={cn('hover-lift border', variantStyles[variant])}>
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">{title}</p>
            <p className="text-3xl font-bold text-foreground">{value}</p>
            {change !== undefined && (
              <div className="flex items-center gap-1 text-sm">
                {change >= 0 ? (
                  <TrendingUp className="h-4 w-4 text-success" />
                ) : (
                  <TrendingDown className="h-4 w-4 text-destructive" />
                )}
                <span className={change >= 0 ? 'text-success' : 'text-destructive'}>
                  {change > 0 ? '+' : ''}{change}%
                </span>
                {changeLabel && (
                  <span className="text-muted-foreground">{changeLabel}</span>
                )}
              </div>
            )}
          </div>
          <div className={cn('w-12 h-12 rounded-xl flex items-center justify-center', iconStyles[variant])}>
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default function DashboardStats() {
  // Mock data - would come from API
  const stats = [
    {
      title: 'Total Medicines',
      value: 12,
      icon: <Pill className="h-6 w-6" />,
      variant: 'primary' as const,
    },
    {
      title: "Today's Reminders",
      value: 8,
      icon: <Clock className="h-6 w-6" />,
      variant: 'default' as const,
    },
    {
      title: 'Completed Today',
      value: '6/8',
      change: 15,
      changeLabel: 'vs yesterday',
      icon: <CheckCircle className="h-6 w-6" />,
      variant: 'success' as const,
    },
    {
      title: 'Low Stock Items',
      value: 3,
      icon: <AlertTriangle className="h-6 w-6" />,
      variant: 'warning' as const,
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat, index) => (
        <motion.div
          key={stat.title}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: index * 0.1 }}
        >
          <StatCard {...stat} />
        </motion.div>
      ))}
    </div>
  );
}
