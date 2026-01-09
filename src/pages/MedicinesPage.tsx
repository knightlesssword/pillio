import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import PageHeader from '@/components/common/PageHeader';
import { Button } from '@/components/ui/button';
import { Plus, Search, Filter, Loader2, MoreVertical, Edit, Trash2, AlertTriangle } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Pill } from 'lucide-react';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import medicinesApi, { type ApiMedicine, type MissingMedicineItem } from '@/lib/medicines-api';
import { toMedicine, type Medicine } from '@/types';
import { useToast } from '@/hooks/use-toast';
import { getErrorMessage } from '@/lib/api';
import { MedicineFormDialog } from '@/components/medicine/MedicineFormDialog';
import { DeleteMedicineDialog } from '@/components/medicine/DeleteMedicineDialog';
import { MissingMedicineCard } from '@/components/medicine/MissingMedicineCard';
import { type MedicineCreate } from '@/lib/medicines-api';

export default function MedicinesPage() {
  const [medicines, setMedicines] = useState<Medicine[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [error, setError] = useState<string | null>(null);
  
  // Dialog states
  const [formDialogOpen, setFormDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedMedicine, setSelectedMedicine] = useState<Medicine | null>(null);
  
  // Missing medicine from prescription (for pre-filling form)
  const [pendingMissingMedicine, setPendingMissingMedicine] = useState<MissingMedicineItem | null>(null);
  
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const fetchMedicines = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await medicinesApi.list({ search: searchQuery || undefined });
      const medicinesData = response.data.items.map((apiMed: ApiMedicine) => toMedicine(apiMed));
      setMedicines(medicinesData);
    } catch (err) {
      const message = getErrorMessage(err);
      setError(message);
      toast({
        title: 'Error fetching medicines',
        description: message,
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  }, [searchQuery, toast]);

  useEffect(() => {
    fetchMedicines();
  }, [fetchMedicines]);

  const handleAddMedicine = () => {
    setSelectedMedicine(null);
    setFormDialogOpen(true);
  };

  const handleEditMedicine = (medicine: Medicine) => {
    setSelectedMedicine(medicine);
    setFormDialogOpen(true);
  };

  const handleDeleteMedicine = (medicine: Medicine) => {
    setSelectedMedicine(medicine);
    setDeleteDialogOpen(true);
  };

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  // Fetch missing medicines from prescriptions
  const { data: missingMedicines, refetch: refetchMissing } = useQuery({
    queryKey: ['missing-from-inventory'],
    queryFn: async () => {
      const response = await medicinesApi.getMissingFromInventory();
      return response.data;
    },
  });

  const handleAddToInventory = (medicine: MissingMedicineItem) => {
    setPendingMissingMedicine(medicine);
    setSelectedMedicine(null); // Clear any selected medicine
    setFormDialogOpen(true);
  };

  const handleHideMissing = async (id: number) => {
    // For now, just refresh the list
    // In the future, we could add an API endpoint to hide specific missing medicine
    refetchMissing();
    toast({
      title: 'Hidden',
      description: 'This suggestion has been hidden.',
    });
  };

  return (
    <div className="space-y-6">
      <PageHeader title="Medicines" description="Manage your medication inventory">
        <Button className="gradient-primary" onClick={handleAddMedicine}>
          <Plus className="h-4 w-4 mr-2" />
          Add Medicine
        </Button>
      </PageHeader>

      <div className="flex gap-4 flex-wrap">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input 
            placeholder="Search medicines..." 
            className="pl-10" 
            value={searchQuery}
            onChange={handleSearch}
          />
        </div>
        <Button variant="outline">
          <Filter className="h-4 w-4 mr-2" />
          Filter
        </Button>
      </div>

      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      )}

      {!isLoading && error && (
        <div className="text-center py-12">
          <p className="text-destructive">{error}</p>
          <Button onClick={fetchMedicines} variant="outline" className="mt-4">
            Retry
          </Button>
        </div>
      )}

      {!isLoading && !error && medicines.length === 0 && (
        <div className="text-center py-12">
          <p className="text-muted-foreground">No medicines found</p>
          <Button onClick={handleAddMedicine} className="mt-4">
            Add your first medicine
          </Button>
        </div>
      )}

      {!isLoading && !error && medicines.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {medicines.map((med, index) => (
            <motion.div
              key={med.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
            >
              <Card className="hover-lift">
                <CardContent className="p-5">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                        <Pill className="h-6 w-6 text-primary" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-foreground">{med.name}</h3>
                        <p className="text-sm text-muted-foreground">{med.dosage}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary">{med.category}</Badge>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon" className="h-8 w-8">
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => handleEditMedicine(med)}>
                            <Edit className="h-4 w-4 mr-2" />
                            Edit
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => handleDeleteMedicine(med)} className="text-destructive">
                            <Trash2 className="h-4 w-4 mr-2" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </div>
                  <div className="mt-4 pt-4 border-t flex justify-between text-sm">
                    <span className="text-muted-foreground">Stock</span>
                    <span className={`font-medium ${med.currentStock <= med.minimumStock ? 'text-warning' : ''}`}>
                      {med.currentStock} {med.unit}
                    </span>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      )}

      {/* Missing from Inventory Section */}
      {missingMedicines && missingMedicines.length > 0 && (
        <div className="mt-12">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle className="h-5 w-5 text-amber-500" />
            <h2 className="text-lg font-semibold">
              Missing from Inventory ({missingMedicines.length})
            </h2>
          </div>
          <p className="text-sm text-muted-foreground mb-4">
            These medicines appear in your prescriptions but not in your inventory.
            Add them to keep track of your medication stock.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {missingMedicines.map((med) => (
              <MissingMedicineCard
                key={med.id}
                medicine={med}
                onAddToInventory={handleAddToInventory}
                onHide={handleHideMissing}
              />
            ))}
          </div>
        </div>
      )}

      {/* Add/Edit Medicine Dialog */}
      <MedicineFormDialog
        open={formDialogOpen}
        onOpenChange={(open) => {
          setFormDialogOpen(open);
          if (!open) {
            setPendingMissingMedicine(null);
          }
        }}
        medicine={selectedMedicine}
        preFillFromPrescription={pendingMissingMedicine || undefined}
        onSuccess={() => {
          fetchMedicines();
          refetchMissing();
        }}
      />

      {/* Delete Confirmation Dialog */}
      <DeleteMedicineDialog
        medicine={selectedMedicine}
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
        onSuccess={fetchMedicines}
      />
    </div>
  );
}
