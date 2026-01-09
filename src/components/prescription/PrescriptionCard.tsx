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
  Eye,
  Edit,
  Trash2,
  Pill
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
        <Badge variant="destructive" className="gap-1 font-medium">
          <AlertCircle className="h-3.5 w-3.5" />
          Expired
        </Badge>
      );
    }
    if (!prescription.is_active) {
      return (
        <Badge variant="secondary" className="gap-1 font-medium bg-gray-100 text-gray-600 border-gray-200">
          <FileText className="h-3.5 w-3.5" />
          Inactive
        </Badge>
      );
    }
    if (prescription.days_until_expiry <= 14 && prescription.valid_until) {
      return (
        <Badge className="gap-1 bg-amber-500/10 text-amber-700 border-amber-200 hover:bg-amber-500/20 font-medium">
          <Clock className="h-3.5 w-3.5" />
          {prescription.days_until_expiry} days left
        </Badge>
      );
    }
    return (
      <Badge className="gap-1 bg-emerald-500/10 text-emerald-700 border-emerald-200 hover:bg-emerald-500/20 font-medium">
        <FileText className="h-3.5 w-3.5" />
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
    <Card className="hover:shadow-lg transition-all duration-200 border-border/60 hover:border-border">
      <CardHeader className="pb-4 space-y-3">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <CardTitle className="text-xl font-bold mb-2 truncate">
              {prescription.doctor_name}
            </CardTitle>
            <div className="flex flex-col gap-1.5">
              {prescription.hospital_clinic && (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Building2 className="h-4 w-4 flex-shrink-0" />
                  <span className="truncate">{prescription.hospital_clinic}</span>
                </div>
              )}
            </div>
          </div>
          <div className="flex flex-col items-end gap-2">
            {getStatusBadge()}
            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 hover:bg-primary/80"
                onClick={() => onView(prescription)}
              >
                <Eye className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 hover:bg-primary/80"
                onClick={() => onEdit(prescription)}
              >
                <Edit className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-destructive hover:bg-destructive/80"
                onClick={() => onDelete(prescription)}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
        {/* Expiry Info */}
        <div className="flex items-center justify-between gap-4 pt-2 text-xs text-muted-foreground border-t border-border/40">
          <div className="flex items-center gap-1.5">
            <Calendar className="h-4 w-4 flex-shrink-0" />
            <span className="font-medium">
              {formatDate(prescription.prescription_date)}
            </span>
          </div>
          {prescription.valid_until ? (
            <div className="flex items-center gap-1.5">
              <Clock className="h-3.5 w-3.5 flex-shrink-0" />
              <span className="font-medium">
                Valid until {formatDate(prescription.valid_until)}
              </span>
            </div>
          ) : (
            <div className="flex items-center gap-1.5">
              <Clock className="h-3.5 w-3.5 flex-shrink-0" />
              <span className="font-medium">
                Duration unspecified
              </span>
            </div>
          )}
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4 pt-0">
        <div className="h-px bg-border/50" />
        
        {/* Medicines Summary */}
        <div className="space-y-2.5">
          <div className="flex items-center gap-2">
            <Pill className="h-4 w-4 text-muted-foreground" />
            <p className="text-sm font-semibold text-foreground">
              Medicines ({prescription.prescription_medicines.length})
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            {prescription.prescription_medicines.slice(0, 3).map((med, index) => (
              <Badge 
                key={index} 
                variant="secondary" 
                className="text-xs font-medium py-1 px-2.5 bg-secondary/60 hover:bg-secondary/80"
              >
                {med.medicine_name} • {med.dosage}
              </Badge>
            ))}
            {prescription.prescription_medicines.length > 3 && (
              <Badge 
                variant="outline" 
                className="text-xs font-medium py-1 px-2.5 bg-muted/30"
              >
                +{prescription.prescription_medicines.length - 3} more
              </Badge>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
