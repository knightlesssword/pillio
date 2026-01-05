import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { AlertTriangle, Package, ChevronRight, Plus } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { cn, getStockStatus, getStockStatusColor } from '@/lib/utils';
import { ROUTES } from '@/lib/constants';

interface LowStockItem {
  id: string;
  name: string;
  currentStock: number;
  minimumStock: number;
  unit: string;
}

// Mock data
const mockLowStockItems: LowStockItem[] = [
  {
    id: '1',
    name: 'Aspirin',
    currentStock: 5,
    minimumStock: 30,
    unit: 'tablets',
  },
  {
    id: '2',
    name: 'Vitamin D3',
    currentStock: 8,
    minimumStock: 30,
    unit: 'capsules',
  },
  {
    id: '3',
    name: 'Metformin',
    currentStock: 12,
    minimumStock: 60,
    unit: 'tablets',
  },
];

function StockItem({ item }: { item: LowStockItem }) {
  const percentage = Math.round((item.currentStock / item.minimumStock) * 100);
  const status = getStockStatus(item.currentStock, item.minimumStock);

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      className="p-3 rounded-lg border border-border bg-card hover:bg-muted/50 transition-colors"
    >
      <div className="flex items-center justify-between mb-2">
        <h4 className="font-medium text-foreground text-sm">{item.name}</h4>
        <span
          className={cn(
            'text-xs font-medium px-2 py-0.5 rounded-full',
            status === 'critical' ? 'bg-destructive/10 text-destructive' :
            status === 'low' ? 'bg-warning/10 text-warning' :
            'bg-info/10 text-info'
          )}
        >
          {item.currentStock} {item.unit} left
        </span>
      </div>
      <Progress
        value={percentage}
        className={cn(
          'h-2',
          status === 'critical' ? '[&>div]:bg-destructive' :
          status === 'low' ? '[&>div]:bg-warning' :
          '[&>div]:bg-info'
        )}
      />
    </motion.div>
  );
}

export default function LowStockAlert() {
  if (mockLowStockItems.length === 0) {
    return (
      <Card className="h-full">
        <CardHeader className="pb-4">
          <CardTitle className="text-lg font-semibold flex items-center gap-2">
            <Package className="h-5 w-5 text-muted-foreground" />
            Stock Levels
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-6">
            <div className="w-12 h-12 rounded-full bg-success/10 flex items-center justify-center mx-auto mb-3">
              <Package className="h-6 w-6 text-success" />
            </div>
            <p className="text-sm text-muted-foreground">All stock levels are good!</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="h-full">
      <CardHeader className="flex flex-row items-center justify-between pb-4">
        <CardTitle className="text-lg font-semibold flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-warning" />
          Low Stock Alert
        </CardTitle>
        <Link to={ROUTES.INVENTORY}>
          <Button variant="ghost" size="sm" className="text-primary">
            View All
            <ChevronRight className="h-4 w-4 ml-1" />
          </Button>
        </Link>
      </CardHeader>
      <CardContent className="space-y-3">
        {mockLowStockItems.map((item, index) => (
          <motion.div
            key={item.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
          >
            <StockItem item={item} />
          </motion.div>
        ))}
        <Button variant="outline" className="w-full mt-4" asChild>
          <Link to={ROUTES.INVENTORY}>
            <Plus className="h-4 w-4 mr-2" />
            Refill Stock
          </Link>
        </Button>
      </CardContent>
    </Card>
  );
}
