import React, { useState } from 'react';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import { Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import remindersApi from '@/lib/reminders-api';

interface DeleteReminderDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  reminderId: number;
  reminderName: string;
  onSuccess: () => void;
}

export function DeleteReminderDialog({ 
  open, 
  onOpenChange, 
  reminderId, 
  reminderName, 
  onSuccess 
}: DeleteReminderDialogProps) {
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleDelete = async () => {
    setIsLoading(true);
    try {
      await remindersApi.delete(reminderId);
      toast({
        title: 'Reminder deleted',
        description: `${reminderName} has been deleted.`,
      });
      onSuccess();
      onOpenChange(false);
    } catch (error) {
      console.error('Failed to delete reminder:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete reminder. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Delete Reminder</AlertDialogTitle>
          <AlertDialogDescription>
            Are you sure you want to delete the reminder for <strong>{reminderName}</strong>? 
            This action cannot be undone and will also delete all associated reminder logs.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={isLoading}>Cancel</AlertDialogCancel>
          <AlertDialogAction 
            onClick={(e) => { e.preventDefault(); handleDelete(); }}
            disabled={isLoading}
            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
          >
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Delete
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
