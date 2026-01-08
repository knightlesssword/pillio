import React from 'react';
import { PrescriptionWithMedicines } from '@/lib/prescriptions-api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Calendar, 
  Building2, 
  FileText, 
  AlertCircle, 
  Clock,
  MoreVertical,
  Eye,
  Edit,
  Trash2
} from 'lucide-react';

interface PrescriptionCardProps {
  prescription: PrescriptionWithMedicines;
  onView: (prescription: PrescriptionWithMedicines) => void;
  onEdit: (prescription: PrescriptionWithMedicines) => void;
  onDelete: (prescription: PrescriptionWithMedicines) => void;
}

export function PrescriptionCard({ 
  prescription, 
  onView, 
  onEdit, 
  onDelete 
}: PrescriptionCardProps) {
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
        <FileText className="h-3 w-3" />
        Active
      </Badge>
    );
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <CardTitle className="text-lg font-semibold">
              {prescription.doctor_name}
            </CardTitle>
            <div className="flex items-center gap-3 text-sm text-muted-foreground">
              {prescription.hospital_clinic && (
                <span className="flex items-center gap-1">
                  <Building2 className="h-3.5 w-3.5" />
                  {prescription.hospital_clinic}
                </span>
              )}
              <span className="flex items-center gap-1">
                <Calendar className="h-3.5 w-3.5" />
                {formatDate(prescription.prescription_date)}
              </span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {getStatusBadge()}
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={() => onView(prescription)}
            >
              <Eye className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={() => onEdit(prescription)}
            >
              <Edit className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-destructive hover:text-destructive"
              onClick={() => onDelete(prescription)}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-3">
        {/* Medicines Summary */}
        <div className="space-y-2">
          <p className="text-sm font-medium text-muted-foreground">
            Medicines ({prescription.prescription_medicines.length})
          </p>
          <div className="flex flex-wrap gap-1.5">
            {prescription.prescription_medicines.slice(0, 3).map((med, index) => (
              <Badge key={index} variant="secondary" className="text-xs">
                {med.medicine_name} - {med.dosage}
              </Badge>
            ))}
            {prescription.prescription_medicines.length > 3 && (
              <Badge variant="outline" className="text-xs">
                +{prescription.prescription_medicines.length - 3} more
              </Badge>
            )}
          </div>
        </div>

        {/* Expiry Info */}
        {prescription.valid_until && (
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Clock className="h-3.5 w-3.5" />
            <span>
              Valid until: {formatDate(prescription.valid_until)}
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
