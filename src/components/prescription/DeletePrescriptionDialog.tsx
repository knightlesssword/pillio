import React from 'react';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import { PrescriptionWithMedicines } from '@/lib/prescriptions-api';

interface DeletePrescriptionDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  prescription: PrescriptionWithMedicines | null;
  onConfirm: () => void;
  isLoading: boolean;
}

export function DeletePrescriptionDialog({
  open,
  onOpenChange,
  prescription,
  onConfirm,
  isLoading,
}: DeletePrescriptionDialogProps) {
  if (!prescription) return null;

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Delete Prescription</AlertDialogTitle>
          <AlertDialogDescription>
            Are you sure you want to delete the prescription from{' '}
            <strong>{prescription.doctor_name}</strong>
            {prescription.hospital_clinic && ` at ${prescription.hospital_clinic}`}?
            <br /><br />
            This will permanently delete the prescription and all{' '}
            <strong>{prescription.prescription_medicines.length} medicine(ies)</strong> associated with it.
            <br /><br />
            This action cannot be undone.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={isLoading}>Cancel</AlertDialogCancel>
          <AlertDialogAction
            onClick={(e) => {
              e.preventDefault();
              onConfirm();
            }}
            disabled={isLoading}
            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
          >
            {isLoading ? 'Deleting...' : 'Delete'}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
