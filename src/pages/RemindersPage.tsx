import React from 'react';
import PageHeader from '@/components/common/PageHeader';
import { Button } from '@/components/ui/button';
import { Plus, Calendar, List } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import UpcomingReminders from '@/components/dashboard/UpcomingReminders';

export default function RemindersPage() {
  return (
    <div className="space-y-6">
      <PageHeader title="Reminders" description="Manage your medication reminders">
        <Button className="gradient-primary">
          <Plus className="h-4 w-4 mr-2" />
          Add Reminder
        </Button>
      </PageHeader>

      <Tabs defaultValue="list" className="space-y-4">
        <TabsList>
          <TabsTrigger value="list" className="gap-2">
            <List className="h-4 w-4" />
            List
          </TabsTrigger>
          <TabsTrigger value="calendar" className="gap-2">
            <Calendar className="h-4 w-4" />
            Calendar
          </TabsTrigger>
        </TabsList>

        <TabsContent value="list">
          <UpcomingReminders />
        </TabsContent>

        <TabsContent value="calendar">
          <Card>
            <CardHeader>
              <CardTitle>Calendar View</CardTitle>
            </CardHeader>
            <CardContent className="min-h-[400px] flex items-center justify-center text-muted-foreground">
              Calendar view coming soon...
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
