import React from 'react';
import PageHeader from '@/components/common/PageHeader';
import { Button } from '@/components/ui/button';
import { Plus, FileText } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import EmptyState from '@/components/common/EmptyState';

export default function PrescriptionsPage() {
  return (
    <div className="space-y-6">
      <PageHeader title="Prescriptions" description="Manage your prescriptions">
        <Button className="gradient-primary">
          <Plus className="h-4 w-4 mr-2" />
          Add Prescription
        </Button>
      </PageHeader>

      <EmptyState
        icon={<FileText className="h-8 w-8 text-muted-foreground" />}
        title="No prescriptions yet"
        description="Upload your prescriptions to keep track of your medications"
        action={
          <Button className="gradient-primary">
            <Plus className="h-4 w-4 mr-2" />
            Add Your First Prescription
          </Button>
        }
      />
    </div>
  );
}
