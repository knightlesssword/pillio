import React from 'react';
import { motion } from 'framer-motion';
import { Plus, Pill, Clock, AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Link } from 'react-router-dom';
import PageHeader from '@/components/common/PageHeader';
import DashboardStats from '@/components/dashboard/DashboardStats';
import UpcomingReminders from '@/components/dashboard/UpcomingReminders';
import LowStockAlert from '@/components/inventory/LowStockAlert';
import AdherenceChart from '@/components/analytics/AdherenceChart';
import QuickActions from '@/components/dashboard/QuickActions';
import { useAuth } from '@/contexts/AuthContext';
import { getGreeting } from '@/lib/utils';
import { ROUTES } from '@/lib/constants';

export default function DashboardPage() {
  const { user } = useAuth();
  const greeting = getGreeting();

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Header */}
      <motion.div variants={itemVariants}>
        <PageHeader
          title={`${greeting}, ${user?.name?.split(' ')[0] || 'there'}!`}
          description="Here's an overview of your medication schedule"
        >
          <Link to={ROUTES.MEDICINES}>
            <Button className="gradient-primary">
              <Plus className="h-4 w-4 mr-2" />
              Add Medicine
            </Button>
          </Link>
        </PageHeader>
      </motion.div>

      {/* Stats Grid */}
      <motion.div variants={itemVariants}>
        <DashboardStats />
      </motion.div>

      {/* Quick Actions */}
      <motion.div variants={itemVariants}>
        <QuickActions />
      </motion.div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upcoming Reminders */}
        <motion.div variants={itemVariants} className="lg:col-span-2">
          <UpcomingReminders />
        </motion.div>

        {/* Low Stock Alerts */}
        <motion.div variants={itemVariants}>
          <LowStockAlert />
        </motion.div>
      </div>

      {/* Adherence Chart */}
      <motion.div variants={itemVariants}>
        <AdherenceChart />
      </motion.div>
    </motion.div>
  );
}
