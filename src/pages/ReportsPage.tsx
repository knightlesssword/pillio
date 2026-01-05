import React from 'react';
import PageHeader from '@/components/common/PageHeader';
import AdherenceChart from '@/components/analytics/AdherenceChart';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart3, TrendingUp, Calendar } from 'lucide-react';

export default function ReportsPage() {
  return (
    <div className="space-y-6">
      <PageHeader title="Reports" description="Analytics and insights about your medication adherence" />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-6 text-center">
            <div className="w-12 h-12 rounded-xl bg-success/10 flex items-center justify-center mx-auto mb-3">
              <TrendingUp className="h-6 w-6 text-success" />
            </div>
            <p className="text-3xl font-bold text-foreground">87%</p>
            <p className="text-sm text-muted-foreground">Overall Adherence</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6 text-center">
            <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mx-auto mb-3">
              <Calendar className="h-6 w-6 text-primary" />
            </div>
            <p className="text-3xl font-bold text-foreground">28</p>
            <p className="text-sm text-muted-foreground">Day Streak</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6 text-center">
            <div className="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center mx-auto mb-3">
              <BarChart3 className="h-6 w-6 text-accent" />
            </div>
            <p className="text-3xl font-bold text-foreground">156</p>
            <p className="text-sm text-muted-foreground">Doses Taken</p>
          </CardContent>
        </Card>
      </div>

      <AdherenceChart />
    </div>
  );
}
