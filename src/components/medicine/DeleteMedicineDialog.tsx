import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { Medicine } from '@/types';
import medicinesApi from '@/lib/medicines-api';
import { useToast } from '@/hooks/use-toast';
import { getErrorMessage } from '@/lib/api';

interface DeleteMedicineDialogProps {
  medicine: Medicine | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export function DeleteMedicineDialog({ medicine, open, onOpenChange, onSuccess }: DeleteMedicineDialogProps) {
  const { toast } = useToast();

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
    <AlertDialog open={open} onOpenChange={onOpenChange}>
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
  );
}
