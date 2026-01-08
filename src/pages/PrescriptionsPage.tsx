import React, { useState, useEffect } from 'react';
import PageHeader from '@/components/common/PageHeader';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Plus, FileText, Search, Filter } from 'lucide-react';
import { PrescriptionCard } from '@/components/prescription/PrescriptionCard';
import { PrescriptionFormDialog } from '@/components/prescription/PrescriptionFormDialog';
import { PrescriptionDetailDialog } from '@/components/prescription/PrescriptionDetailDialog';
import { DeletePrescriptionDialog } from '@/components/prescription/DeletePrescriptionDialog';
import prescriptionsApi, { 
  type PrescriptionWithMedicines, 
  type PrescriptionFilter 
} from '@/lib/prescriptions-api';
import { useToast } from '@/hooks/use-toast';
import { getErrorMessage } from '@/lib/api';
import { Loader2 } from 'lucide-react';

export default function PrescriptionsPage() {
  const [prescriptions, setPrescriptions] = useState<PrescriptionWithMedicines[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'expired'>('all');
  
  // Dialog states
  const [formDialogOpen, setFormDialogOpen] = useState(false);
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  
  const [selectedPrescription, setSelectedPrescription] = useState<PrescriptionWithMedicines | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  
  const { toast } = useToast();

  const fetchPrescriptions = async () => {
    setIsLoading(true);
    try {
      const filters: PrescriptionFilter = {
        search: searchQuery || undefined,
      };
      
      if (filterStatus === 'active') {
        filters.is_active = true;
      } else if (filterStatus === 'expired') {
        filters.is_expired = true;
      }
      
      const response = await prescriptionsApi.list(filters);
      setPrescriptions(response.data.items);
    } catch (error) {
      const message = getErrorMessage(error);
      toast({
        title: 'Error loading prescriptions',
        description: message,
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPrescriptions();
  }, [filterStatus]);

  useEffect(() => {
    const delaySearch = setTimeout(() => {
      fetchPrescriptions();
    }, 300);

    return () => clearTimeout(delaySearch);
  }, [searchQuery]);

  const handleView = (prescription: PrescriptionWithMedicines) => {
    setSelectedPrescription(prescription);
    setDetailDialogOpen(true);
  };

  const handleEdit = (prescription: PrescriptionWithMedicines) => {
    setSelectedPrescription(prescription);
    setFormDialogOpen(true);
  };

  const handleDelete = (prescription: PrescriptionWithMedicines) => {
    setSelectedPrescription(prescription);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!selectedPrescription) return;
    
    setIsDeleting(true);
    try {
      await prescriptionsApi.delete(Number(selectedPrescription.id));
      toast({
        title: 'Prescription deleted',
        description: 'The prescription has been deleted.',
      });
      fetchPrescriptions();
      setDeleteDialogOpen(false);
      setSelectedPrescription(null);
    } catch (error) {
      const message = getErrorMessage(error);
      toast({
        title: 'Error deleting prescription',
        description: message,
        variant: 'destructive',
      });
    } finally {
      setIsDeleting(false);
    }
  };

  const handleFormSuccess = () => {
    fetchPrescriptions();
    setSelectedPrescription(null);
  };

  const handleAddNew = () => {
    setSelectedPrescription(null);
    setFormDialogOpen(true);
  };

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Prescriptions" 
        description="Manage your prescriptions and track your medications"
      >
        <Button className="gradient-primary" onClick={handleAddNew}>
          <Plus className="h-4 w-4 mr-2" />
          Add Prescription
        </Button>
      </PageHeader>

      {/* Search and Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search prescriptions..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
        
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value as 'all' | 'active' | 'expired')}
            className="flex h-10 w-40 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            <option value="all">All</option>
            <option value="active">Active</option>
            <option value="expired">Expired</option>
          </select>
        </div>
      </div>

      {/* Prescriptions List */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : prescriptions.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <div className="rounded-full bg-muted p-4 mb-4">
            <FileText className="h-8 w-8 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-medium mb-1">No prescriptions yet</h3>
          <p className="text-muted-foreground mb-4">
            Add your first prescription to start tracking your medications
          </p>
          <Button className="gradient-primary" onClick={handleAddNew}>
            <Plus className="h-4 w-4 mr-2" />
            Add Your First Prescription
          </Button>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {prescriptions.map((prescription) => (
            <PrescriptionCard
              key={prescription.id}
              prescription={prescription}
              onView={handleView}
              onEdit={handleEdit}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}

      {/* Dialogs */}
      <PrescriptionFormDialog
        open={formDialogOpen}
        onOpenChange={setFormDialogOpen}
        prescription={selectedPrescription}
        onSuccess={handleFormSuccess}
      />

      <PrescriptionDetailDialog
        open={detailDialogOpen}
        onOpenChange={setDetailDialogOpen}
        prescription={selectedPrescription}
      />

      <DeletePrescriptionDialog
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
        prescription={selectedPrescription}
        onConfirm={handleDeleteConfirm}
        isLoading={isDeleting}
      />
    </div>
  );
}
