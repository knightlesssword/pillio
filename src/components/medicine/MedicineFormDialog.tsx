import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { MedicineForm } from '@/types';
import medicinesApi, { type MedicineCreate, type MedicineUpdate } from '@/lib/medicines-api';
import { toMedicine, type Medicine } from '@/types';
import { Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { getErrorMessage } from '@/lib/api';

interface MedicineFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  medicine?: Medicine | null;
  onSuccess: () => void;
}

const INITIAL_FORM: MedicineForm = {
  name: '',
  genericName: '',
  category: 'tablet',
  dosage: '',
  unit: 'tablets',
  currentStock: 0,
  minimumStock: 5,
};

const MEDICINE_FORMS = ['tablet', 'capsule', 'syrup', 'injection', 'cream', 'drops', 'inhaler', 'patch', 'other'];
const UNITS = ['tablets', 'capsules', 'ml', 'mg', 'units', 'drops', 'grams', 'puffs'];

export function MedicineFormDialog({ open, onOpenChange, medicine, onSuccess }: MedicineFormDialogProps) {
  const [form, setForm] = useState<MedicineForm>(INITIAL_FORM);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const isEditing = Boolean(medicine);

  useEffect(() => {
    if (medicine) {
      setForm({
        name: medicine.name,
        genericName: medicine.genericName || '',
        category: medicine.category,
        dosage: medicine.dosage,
        unit: medicine.unit,
        currentStock: medicine.currentStock,
        minimumStock: medicine.minimumStock,
      });
    } else {
      setForm(INITIAL_FORM);
    }
  }, [medicine, open]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      if (isEditing && medicine) {
        // Update existing medicine
        const updateData: MedicineUpdate = {
          name: form.name,
          generic_name: form.genericName || undefined,
          form: form.category,
          dosage: form.dosage,
          unit: form.unit,
          current_stock: form.currentStock,
          min_stock_alert: form.minimumStock,
        };
        await medicinesApi.update(Number(medicine.id), updateData);
        toast({ title: 'Medicine updated', description: `${form.name} has been updated.` });
      } else {
        // Create new medicine
        const createData: MedicineCreate = {
          name: form.name,
          generic_name: form.genericName || undefined,
          form: form.category,
          dosage: form.dosage,
          unit: form.unit,
          current_stock: form.currentStock,
          min_stock_alert: form.minimumStock,
        };
        await medicinesApi.create(createData);
        toast({ title: 'Medicine added', description: `${form.name} has been added.` });
      }
      onSuccess();
      onOpenChange(false);
    } catch (error) {
      const message = getErrorMessage(error);
      toast({
        title: isEditing ? 'Error updating medicine' : 'Error adding medicine',
        description: message,
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>{isEditing ? 'Edit Medicine' : 'Add New Medicine'}</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <Label htmlFor="name">Medicine Name *</Label>
              <Input
                id="name"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="e.g., Aspirin"
                required
              />
            </div>

            <div className="col-span-2">
              <Label htmlFor="genericName">Generic Name</Label>
              <Input
                id="genericName"
                value={form.genericName}
                onChange={(e) => setForm({ ...form, genericName: e.target.value })}
                placeholder="e.g., Acetylsalicylic acid"
              />
            </div>

            <div>
              <Label htmlFor="dosage">Dosage *</Label>
              <Input
                id="dosage"
                value={form.dosage}
                onChange={(e) => setForm({ ...form, dosage: e.target.value })}
                placeholder="e.g., 100mg"
                required
              />
            </div>

            <div>
              <Label htmlFor="form">Form *</Label>
              <select
                id="form"
                value={form.category}
                onChange={(e) => setForm({ ...form, category: e.target.value })}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                {MEDICINE_FORMS.map((form) => (
                  <option key={form} value={form}>
                    {form.charAt(0).toUpperCase() + form.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <Label htmlFor="unit">Unit *</Label>
              <select
                id="unit"
                value={form.unit}
                onChange={(e) => setForm({ ...form, unit: e.target.value })}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                {UNITS.map((unit) => (
                  <option key={unit} value={unit}>
                    {unit}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <Label htmlFor="currentStock">Current Stock</Label>
              <Input
                id="currentStock"
                type="number"
                min="0"
                value={form.currentStock}
                onChange={(e) => setForm({ ...form, currentStock: Number(e.target.value) })}
              />
            </div>

            <div>
              <Label htmlFor="minimumStock">Min Stock Alert</Label>
              <Input
                id="minimumStock"
                type="number"
                min="0"
                value={form.minimumStock}
                onChange={(e) => setForm({ ...form, minimumStock: Number(e.target.value) })}
              />
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)} disabled={isLoading}>
              Cancel
            </Button>
            <Button type="submit" className="gradient-primary" disabled={isLoading}>
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {isEditing ? 'Save Changes' : 'Add Medicine'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
