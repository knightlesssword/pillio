import React from 'react';
import PageHeader from '@/components/common/PageHeader';
import { Button } from '@/components/ui/button';
import { Plus, Search, Filter } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import EmptyState from '@/components/common/EmptyState';
import { Pill } from 'lucide-react';

const mockMedicines = [
  { id: '1', name: 'Aspirin', category: 'Tablets', dosage: '100mg', stock: 25, unit: 'tablets' },
  { id: '2', name: 'Vitamin D3', category: 'Capsules', dosage: '1000 IU', stock: 8, unit: 'capsules' },
  { id: '3', name: 'Metformin', category: 'Tablets', dosage: '500mg', stock: 45, unit: 'tablets' },
  { id: '4', name: 'Lisinopril', category: 'Tablets', dosage: '10mg', stock: 30, unit: 'tablets' },
];

export default function MedicinesPage() {
  return (
    <div className="space-y-6">
      <PageHeader title="Medicines" description="Manage your medication inventory">
        <Button className="gradient-primary">
          <Plus className="h-4 w-4 mr-2" />
          Add Medicine
        </Button>
      </PageHeader>

      <div className="flex gap-4 flex-wrap">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input placeholder="Search medicines..." className="pl-10" />
        </div>
        <Button variant="outline">
          <Filter className="h-4 w-4 mr-2" />
          Filter
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {mockMedicines.map((med) => (
          <Card key={med.id} className="hover-lift cursor-pointer">
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
                <Badge variant="secondary">{med.category}</Badge>
              </div>
              <div className="mt-4 pt-4 border-t flex justify-between text-sm">
                <span className="text-muted-foreground">Stock</span>
                <span className="font-medium">{med.stock} {med.unit}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
