import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, Package } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { cn, getStockStatus } from '@/lib/utils';
import medicinesApi, { type ApiMedicine } from '@/lib/medicines-api';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import { StockAdjustmentDialog } from '@/components/medicine/StockAdjustmentDialog';

function StockItem({ item, onClick }: { item: ApiMedicine; onClick: () => void }) {
  const percentage = Math.round((item.current_stock / item.min_stock_alert) * 100);
  const status = getStockStatus(item.current_stock, item.min_stock_alert);

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      onClick={onClick}
      className="p-3 rounded-lg border border-border bg-card hover:bg-muted/50 transition-colors cursor-pointer"
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
          {item.current_stock} {item.unit} left
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
  const [lowStockItems, setLowStockItems] = useState<ApiMedicine[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedMedicine, setSelectedMedicine] = useState<ApiMedicine | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  const fetchLowStockItems = async () => {
    try {
      setLoading(true);
      const response = await medicinesApi.getLowStock();
      setLowStockItems(response.data);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch low stock items:', err);
      setError('Failed to load stock data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLowStockItems();
  }, []);

  const handleItemClick = (item: ApiMedicine) => {
    setSelectedMedicine(item);
    setDialogOpen(true);
  };

  const handleSuccess = () => {
    fetchLowStockItems();
  };

  if (loading) {
    return (
      <Card className="h-full">
        <CardHeader className="pb-4">
          <CardTitle className="text-lg font-semibold flex items-center gap-2">
            <Package className="h-5 w-5 text-muted-foreground" />
            Stock Levels
          </CardTitle>
        </CardHeader>
        <CardContent className="flex items-center justify-center py-8">
          <LoadingSpinner size="sm" />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="h-full">
        <CardHeader className="pb-4">
          <CardTitle className="text-lg font-semibold flex items-center gap-2">
            <Package className="h-5 w-5 text-muted-foreground" />
            Stock Levels
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-6 text-destructive text-sm">
            {error}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (lowStockItems.length === 0) {
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
    <>
      <Card className="h-full">
        <CardHeader className="pb-4">
          <CardTitle className="text-lg font-semibold flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-warning" />
            Low Stock Alert
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {lowStockItems.map((item, index) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <StockItem item={item} onClick={() => handleItemClick(item)} />
            </motion.div>
          ))}
        </CardContent>
      </Card>

      <StockAdjustmentDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        medicine={selectedMedicine}
        onSuccess={handleSuccess}
      />
    </>
  );
}
