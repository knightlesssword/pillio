import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import prescriptionsApi, { 
  type PrescriptionWithMedicines, 
  type PrescriptionCreate, 
  type PrescriptionMedicineCreate 
} from '@/lib/prescriptions-api';
import { Loader2, Plus, Trash2, FileText } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { getErrorMessage } from '@/lib/api';

interface PrescriptionFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  prescription?: PrescriptionWithMedicines | null;
  onSuccess: () => void;
}

const EMPTY_MEDICINE: PrescriptionMedicineCreate = {
  medicine_name: '',
  dosage: '',
  frequency: '',
  duration_days: 7,
  instructions: '',
};

const FREQUENCY_OPTIONS = [
  'Once daily',
  'Twice daily',
  'Three times daily',
  'Four times daily',
  'Every 4 hours',
  'Every 6 hours',
  'Every 8 hours',
  'Every 12 hours',
  'As needed',
  'At bedtime',
  'Once weekly',
];

const DURATION_OPTIONS = [
  { label: '3 days', value: 3 },
  { label: '5 days', value: 5 },
  { label: '7 days (1 week)', value: 7 },
  { label: '10 days', value: 10 },
  { label: '14 days (2 weeks)', value: 14 },
  { label: '21 days (3 weeks)', value: 21 },
  { label: '30 days (1 month)', value: 30 },
  { label: '60 days (2 months)', value: 60 },
  { label: '90 days (3 months)', value: 90 },
];

export function PrescriptionFormDialog({ 
  open, 
  onOpenChange, 
  prescription, 
  onSuccess 
}: PrescriptionFormDialogProps) {
  const [form, setForm] = useState({
    doctor_name: '',
    hospital_clinic: '',
    prescription_date: new Date().toISOString().split('T')[0],
    valid_until: '',
    notes: '',
  });
  const [medicines, setMedicines] = useState<PrescriptionMedicineCreate[]>([{ ...EMPTY_MEDICINE }]);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const isEditing = Boolean(prescription);

  useEffect(() => {
    if (prescription) {
      setForm({
        doctor_name: prescription.doctor_name,
        hospital_clinic: prescription.hospital_clinic || '',
        prescription_date: prescription.prescription_date.split('T')[0],
        valid_until: prescription.valid_until ? prescription.valid_until.split('T')[0] : '',
        notes: prescription.notes || '',
      });
      setMedicines(
        prescription.prescription_medicines.map((pm) => ({
          id: pm.id,
          medicine_id: pm.medicine_id || undefined,
          medicine_name: pm.medicine_name,
          dosage: pm.dosage,
          frequency: pm.frequency,
          duration_days: pm.duration_days,
          instructions: pm.instructions || undefined,
        }))
      );
    } else {
      setForm({
        doctor_name: '',
        hospital_clinic: '',
        prescription_date: new Date().toISOString().split('T')[0],
        valid_until: '',
        notes: '',
      });
      setMedicines([{ ...EMPTY_MEDICINE }]);
    }
  }, [prescription, open]);

  const handleAddMedicine = () => {
    setMedicines([...medicines, { ...EMPTY_MEDICINE }]);
  };

  const handleRemoveMedicine = (index: number) => {
    if (medicines.length > 1) {
      setMedicines(medicines.filter((_, i) => i !== index));
    }
  };

  const handleMedicineChange = (index: number, field: keyof PrescriptionMedicineCreate, value: string | number) => {
    const updated = [...medicines];
    updated[index] = { ...updated[index], [field]: value };
    setMedicines(updated);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate medicines
    const validMedicines = medicines.filter(
      (m) => m.medicine_name.trim() && m.dosage.trim() && m.frequency.trim()
    );
    
    if (validMedicines.length === 0) {
      toast({
        title: 'Validation Error',
        description: 'Please add at least one medicine with name, dosage, and frequency.',
        variant: 'destructive',
      });
      return;
    }

    setIsLoading(true);

    try {
      const createData: PrescriptionCreate = {
        doctor_name: form.doctor_name,
        hospital_clinic: form.hospital_clinic || undefined,
        prescription_date: form.prescription_date,
        valid_until: form.valid_until || undefined,
        notes: form.notes || undefined,
        medicines: validMedicines,
      };

      if (isEditing && prescription) {
        await prescriptionsApi.update(Number(prescription.id), {
          doctor_name: form.doctor_name,
          hospital_clinic: form.hospital_clinic || undefined,
          prescription_date: form.prescription_date,
          valid_until: form.valid_until || undefined,
          notes: form.notes || undefined,
        });
        toast({ title: 'Prescription updated', description: 'Prescription has been updated.' });
      } else {
        await prescriptionsApi.create(createData);
        toast({ title: 'Prescription added', description: 'Prescription has been added.' });
      }
      
      onSuccess();
      onOpenChange(false);
    } catch (error) {
      const message = getErrorMessage(error);
      toast({
        title: isEditing ? 'Error updating prescription' : 'Error adding prescription',
        description: message,
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[700px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            {isEditing ? 'Edit Prescription' : 'Add New Prescription'}
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Doctor Information */}
          <div className="space-y-4">
            <h3 className="font-medium text-sm text-muted-foreground uppercase tracking-wider">
              Doctor Information
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="col-span-2">
                <Label htmlFor="doctor_name">Doctor Name *</Label>
                <Input
                  id="doctor_name"
                  value={form.doctor_name}
                  onChange={(e) => setForm({ ...form, doctor_name: e.target.value })}
                  placeholder="e.g., Dr. John Smith"
                  required
                />
              </div>

              <div className="col-span-2">
                <Label htmlFor="hospital_clinic">Hospital / Clinic</Label>
                <Input
                  id="hospital_clinic"
                  value={form.hospital_clinic}
                  onChange={(e) => setForm({ ...form, hospital_clinic: e.target.value })}
                  placeholder="e.g., City General Hospital"
                />
              </div>

              <div>
                <Label htmlFor="prescription_date">Prescription Date *</Label>
                <Input
                  id="prescription_date"
                  type="date"
                  value={form.prescription_date}
                  onChange={(e) => setForm({ ...form, prescription_date: e.target.value })}
                  required
                />
              </div>

              <div>
                <Label htmlFor="valid_until">Valid Until</Label>
                <Input
                  id="valid_until"
                  type="date"
                  value={form.valid_until}
                  onChange={(e) => setForm({ ...form, valid_until: e.target.value })}
                />
              </div>
            </div>
          </div>

          {/* Medicines */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-medium text-sm text-muted-foreground uppercase tracking-wider">
                Medicines
              </h3>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleAddMedicine}
                className="gap-1"
              >
                <Plus className="h-4 w-4" />
                Add Medicine
              </Button>
            </div>

            <div className="space-y-4">
              {medicines.map((medicine, index) => (
                <div
                  key={index}
                  className="p-4 border rounded-lg space-y-3 bg-muted/30 relative"
                >
                  {medicines.length > 1 && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      className="absolute top-2 right-2 h-8 w-8 text-muted-foreground hover:text-destructive"
                      onClick={() => handleRemoveMedicine(index)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}

                  <div className="grid grid-cols-2 gap-3">
                    <div className="col-span-2">
                      <Label htmlFor={`medicine_name_${index}`}>Medicine Name *</Label>
                      <Input
                        id={`medicine_name_${index}`}
                        value={medicine.medicine_name}
                        onChange={(e) => handleMedicineChange(index, 'medicine_name', e.target.value)}
                        placeholder="e.g., Amoxicillin"
                        required
                      />
                    </div>

                    <div>
                      <Label htmlFor={`dosage_${index}`}>Dosage *</Label>
                      <Input
                        id={`dosage_${index}`}
                        value={medicine.dosage}
                        onChange={(e) => handleMedicineChange(index, 'dosage', e.target.value)}
                        placeholder="e.g., 500mg"
                        required
                      />
                    </div>

                    <div>
                      <Label htmlFor={`frequency_${index}`}>Frequency *</Label>
                      <select
                        id={`frequency_${index}`}
                        value={medicine.frequency}
                        onChange={(e) => handleMedicineChange(index, 'frequency', e.target.value)}
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                        required
                      >
                        <option value="">Select frequency</option>
                        {FREQUENCY_OPTIONS.map((freq) => (
                          <option key={freq} value={freq}>
                            {freq}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <Label htmlFor={`duration_${index}`}>Duration *</Label>
                      <select
                        id={`duration_${index}`}
                        value={medicine.duration_days}
                        onChange={(e) => handleMedicineChange(index, 'duration_days', Number(e.target.value))}
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                        required
                      >
                        {DURATION_OPTIONS.map((opt) => (
                          <option key={opt.value} value={opt.value}>
                            {opt.label}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="col-span-2">
                      <Label htmlFor={`instructions_${index}`}>Instructions</Label>
                      <Input
                        id={`instructions_${index}`}
                        value={medicine.instructions || ''}
                        onChange={(e) => handleMedicineChange(index, 'instructions', e.target.value)}
                        placeholder="e.g., Take with food"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Notes */}
          <div>
            <Label htmlFor="notes">Notes</Label>
            <Textarea
              id="notes"
              value={form.notes}
              onChange={(e) => setForm({ ...form, notes: e.target.value })}
              placeholder="Additional notes about this prescription..."
              rows={3}
            />
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button type="submit" className="gradient-primary" disabled={isLoading}>
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {isEditing ? 'Save Changes' : 'Add Prescription'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
