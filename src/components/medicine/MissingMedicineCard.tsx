import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { MissingMedicineItem } from '@/lib/medicines-api';
import { Plus, EyeOff, Pill } from 'lucide-react';

interface MissingMedicineCardProps {
  medicine: MissingMedicineItem;
  onAddToInventory: (medicine: MissingMedicineItem) => void;
  onHide: (id: number) => void;
}

export function MissingMedicineCard({
  medicine,
  onAddToInventory,
  onHide,
}: MissingMedicineCardProps) {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-lg bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
              <Pill className="h-5 w-5 text-amber-600 dark:text-amber-400" />
            </div>
            <div>
              <CardTitle className="text-lg">{medicine.medicine_name}</CardTitle>
              <p className="text-sm text-muted-foreground">{medicine.dosage}</p>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Frequency:</span>
            <span className="font-medium">{medicine.frequency}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Duration:</span>
            <span className="font-medium">{medicine.duration_days} days</span>
          </div>
          {medicine.instructions && (
            <div className="pt-2 border-t">
              <span className="text-muted-foreground block mb-1">Instructions:</span>
              <p className="text-muted-foreground italic">{medicine.instructions}</p>
            </div>
          )}
          <div className="pt-2 border-t">
            <p className="text-muted-foreground text-xs">
              Appears in {medicine.prescriptions_count} prescription{medicine.prescriptions_count > 1 ? 's' : ''}
            </p>
          </div>
        </div>

        <div className="flex gap-2 mt-4">
          <Button
            onClick={() => onAddToInventory(medicine)}
            className="flex-1"
            size="sm"
          >
            <Plus className="h-4 w-4 mr-1" />
            Add to Inventory
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => onHide(medicine.id)}
            title="Hide this suggestion"
          >
            <EyeOff className="h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
