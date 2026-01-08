import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import { type ApiMedicine } from '@/lib/medicines-api';
import medicinesApi from '@/lib/medicines-api';
import { Loader2, Plus, Minus, Trash2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { getErrorMessage } from '@/lib/api';

interface StockAdjustmentDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  medicine: ApiMedicine | null;
  onSuccess: () => void;
}

export function StockAdjustmentDialog({ open, onOpenChange, medicine, onSuccess }: StockAdjustmentDialogProps) {
  const [adjustment, setAdjustment] = useState<number>(0);
  // const [reason, setReason] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const { toast } = useToast();

  const handleAdjustStock = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!medicine || adjustment === 0) return;

    setIsLoading(true);
    try {
      await medicinesApi.adjustStock(Number(medicine.id), adjustment, undefined);
      toast({
        title: 'Stock updated',
        description: `${medicine.name} stock adjusted by ${adjustment > 0 ? '+' : ''}${adjustment}.`,
      });
      onSuccess();
      onOpenChange(false);
      setAdjustment(0);
      // setReason('');
    } catch (error) {
      const message = getErrorMessage(error);
      toast({
        title: 'Error adjusting stock',
        description: message,
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!medicine) return;

    try {
      await medicinesApi.delete(Number(medicine.id));
      toast({
        title: 'Medicine deleted',
        description: `${medicine.name} has been removed.`,
      });
      onSuccess();
      onOpenChange(false);
    } catch (error) {
      const message = getErrorMessage(error);
      toast({
        title: 'Error deleting medicine',
        description: message,
        variant: 'destructive',
      });
    }
  };

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="sm:max-w-[400px]">
          <DialogHeader>
            <DialogTitle>Adjust Stock - {medicine?.name}</DialogTitle>
          </DialogHeader>

          <div className="mb-4 p-4 bg-muted rounded-lg">
            <p className="text-sm text-muted-foreground">Current Stock</p>
            <p className="text-2xl font-semibold">{medicine?.current_stock} {medicine?.unit}</p>
          </div>

          <form onSubmit={handleAdjustStock} className="space-y-4">
            <div>
              <Label>Adjust Stock</Label>
              <div className="flex items-center gap-2 mt-2">
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  onClick={() => setAdjustment(adjustment - 1)}
                  disabled={medicine?.current_stock === 0 && adjustment <= 0}
                >
                  <Minus className="h-4 w-4" />
                </Button>
                <Input
                  type="number"
                  value={adjustment}
                  onChange={(e) => setAdjustment(Number(e.target.value))}
                  className="text-center text-lg font-semibold"
                  placeholder="0"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  onClick={() => setAdjustment(adjustment + 1)}
                >
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              <p className="text-xs text-muted-foreground mt-2 text-center">
                New stock will be: {medicine ? medicine.current_stock + adjustment : 0} {medicine?.unit}
              </p>
            </div>

            {/* <div>
              <Label htmlFor="reason">Reason (optional)</Label>
              <Input
                id="reason"
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder="e.g., Refill, Used, Expired"
                className="mt-1"
              />
            </div> */}

            <DialogFooter className="flex justify-between items-center mt-6">
              <Button
                type="button"
                variant="destructive"
                size="sm"
                onClick={() => setShowDeleteConfirm(true)}
                className="ml-0"
              >
                <Trash2 className="h-4 w-4 mr-1" />
                Delete
              </Button>
              <div className="flex gap-2">
                <Button type="button" variant="outline" onClick={() => onOpenChange(false)} disabled={isLoading}>
                  Cancel
                </Button>
                <Button type="submit" className="gradient-primary" disabled={isLoading || adjustment === 0}>
                  {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Apply Adjustment
                </Button>
              </div>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <AlertDialog open={showDeleteConfirm} onOpenChange={setShowDeleteConfirm}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Medicine</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{medicine?.name}</strong>?
              This action cannot be undone and will delete all associated reminders.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
