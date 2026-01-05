import React from 'react';
import PageHeader from '@/components/common/PageHeader';
import LowStockAlert from '@/components/inventory/LowStockAlert';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Plus, Package } from 'lucide-react';

export default function InventoryPage() {
  return (
    <div className="space-y-6">
      <PageHeader title="Inventory" description="Track your medication stock levels">
        <Button className="gradient-primary">
          <Plus className="h-4 w-4 mr-2" />
          Add Stock
        </Button>
      </PageHeader>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Package className="h-5 w-5" />
                All Inventory
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">Inventory management table coming soon...</p>
            </CardContent>
          </Card>
        </div>
        <LowStockAlert />
      </div>
    </div>
  );
}
