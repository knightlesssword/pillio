import React from 'react';
import PageHeader from '@/components/common/PageHeader';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { History, CheckCircle, XCircle, Clock } from 'lucide-react';

const mockHistory = [
  { id: '1', medicine: 'Aspirin', action: 'Taken', time: '8:00 AM', status: 'taken' },
  { id: '2', medicine: 'Vitamin D3', action: 'Taken', time: '9:00 AM', status: 'taken' },
  { id: '3', medicine: 'Metformin', action: 'Missed', time: '1:00 PM', status: 'missed' },
  { id: '4', medicine: 'Lisinopril', action: 'Skipped', time: '6:00 PM', status: 'skipped' },
];

export default function HistoryPage() {
  return (
    <div className="space-y-6">
      <PageHeader title="History" description="View your medication history and adherence" />

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <History className="h-5 w-5" />
            Recent Activity
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {mockHistory.map((item) => (
            <div key={item.id} className="flex items-center gap-4 p-3 rounded-lg border">
              {item.status === 'taken' ? (
                <CheckCircle className="h-5 w-5 text-success" />
              ) : item.status === 'missed' ? (
                <XCircle className="h-5 w-5 text-destructive" />
              ) : (
                <Clock className="h-5 w-5 text-warning" />
              )}
              <div className="flex-1">
                <p className="font-medium">{item.medicine}</p>
                <p className="text-sm text-muted-foreground">{item.action} at {item.time}</p>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
