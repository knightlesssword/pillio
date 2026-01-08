import React from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { PrescriptionWithMedicines } from '@/lib/prescriptions-api';
import { 
  Calendar, 
  Building2, 
  Clock, 
  FileText,
  Pill,
  AlertCircle,
  CheckCircle,
  ExternalLink
} from 'lucide-react';

interface PrescriptionDetailDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  prescription: PrescriptionWithMedicines | null;
}

export function PrescriptionDetailDialog({
  open,
  onOpenChange,
  prescription,
}: PrescriptionDetailDialogProps) {
  if (!prescription) return null;

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const getStatusBadge = () => {
    if (prescription.is_expired) {
      return (
        <Badge variant="destructive" className="gap-1">
          <AlertCircle className="h-3 w-3" />
          Expired
        </Badge>
      );
    }
    if (prescription.days_until_expiry <= 14 && prescription.valid_until) {
      return (
        <Badge variant="secondary" className="gap-1 bg-orange-100 text-orange-800 border-orange-300">
          <Clock className="h-3 w-3" />
          {prescription.days_until_expiry} days left
        </Badge>
      );
    }
    return (
      <Badge variant="secondary" className="gap-1 bg-green-100 text-green-800 border-green-300">
        <CheckCircle className="h-3 w-3" />
        Active
      </Badge>
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <DialogTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Prescription Details
            </DialogTitle>
            {getStatusBadge()}
          </div>
        </DialogHeader>

        <div className="space-y-6">
          {/* Doctor Information */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
                Doctor Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4 text-muted-foreground" />
                <span className="font-medium">{prescription.doctor_name}</span>
              </div>
              {prescription.hospital_clinic && (
                <div className="flex items-center gap-2">
                  <Building2 className="h-4 w-4 text-muted-foreground" />
                  <span>{prescription.hospital_clinic}</span>
                </div>
              )}
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4 text-muted-foreground" />
                <span>{formatDate(prescription.prescription_date)}</span>
              </div>
              {prescription.valid_until && (
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <span>Valid until: {formatDate(prescription.valid_until)}</span>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Medicines */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
                Medicines ({prescription.prescription_medicines.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {prescription.prescription_medicines.map((med, index) => (
                  <div
                    key={index}
                    className="p-4 border rounded-lg space-y-2 bg-muted/30"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2">
                        <Pill className="h-4 w-4 text-primary" />
                        <span className="font-medium">{med.medicine_name}</span>
                      </div>
                      <Badge variant="outline">{med.dosage}</Badge>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div>
                        <span className="text-muted-foreground">Frequency: </span>
                        <span>{med.frequency}</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Duration: </span>
                        <span>{med.duration_days} days</span>
                      </div>
                    </div>
                    
                    {med.instructions && (
                      <div className="text-sm">
                        <span className="text-muted-foreground">Instructions: </span>
                        <span>{med.instructions}</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Notes */}
          {prescription.notes && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
                  Notes
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm">{prescription.notes}</p>
              </CardContent>
            </Card>
          )}

          {/* View Image Button (if image exists) */}
          {prescription.image_url && (
            <Button
              variant="outline"
              className="w-full gap-2"
              onClick={() => window.open(prescription.image_url || '', '_blank')}
            >
              <ExternalLink className="h-4 w-4" />
              View Scanned Prescription
            </Button>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
