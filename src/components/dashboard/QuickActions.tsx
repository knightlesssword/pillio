import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Plus, Bell, FileText, BarChart3 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { ROUTES } from '@/lib/constants';

interface QuickActionProps {
  icon: React.ReactNode;
  label: string;
  description: string;
  to: string;
  gradient: string;
}

function QuickAction({ icon, label, description, to, gradient }: QuickActionProps) {
  return (
    <Link to={to}>
      <motion.div
        whileHover={{ scale: 1.02, y: -2 }}
        whileTap={{ scale: 0.98 }}
        className={cn(
          'p-4 rounded-xl text-primary-foreground transition-shadow',
          'hover:shadow-lg cursor-pointer',
          gradient
        )}
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-primary-foreground/20 flex items-center justify-center">
            {icon}
          </div>
          <div>
            <h3 className="font-semibold">{label}</h3>
            <p className="text-sm opacity-90">{description}</p>
          </div>
        </div>
      </motion.div>
    </Link>
  );
}

export default function QuickActions() {
  const actions: QuickActionProps[] = [
    {
      icon: <Plus className="h-5 w-5" />,
      label: 'Add Medicine',
      description: 'Track a new medication',
      to: ROUTES.MEDICINES,
      gradient: 'gradient-primary',
    },
    {
      icon: <Bell className="h-5 w-5" />,
      label: 'Set Reminder',
      description: 'Create a new reminder',
      to: ROUTES.REMINDERS,
      gradient: 'gradient-accent',
    },
    {
      icon: <FileText className="h-5 w-5" />,
      label: 'Add Prescription',
      description: 'Upload a prescription',
      to: ROUTES.PRESCRIPTIONS,
      gradient: 'gradient-success',
    },
    {
      icon: <BarChart3 className="h-5 w-5" />,
      label: 'View Reports',
      description: 'Check your adherence',
      to: ROUTES.REPORTS,
      gradient: 'bg-gradient-to-r from-info to-primary',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {actions.map((action, index) => (
        <motion.div
          key={action.label}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: index * 0.1 }}
        >
          <QuickAction {...action} />
        </motion.div>
      ))}
    </div>
  );
}
