import React from 'react';
import * as ProgressPrimitive from "@radix-ui/react-progress";
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import type { MedicineAdherenceResponse } from '@/lib/reminders-api';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface MedicineAdherenceCardProps {
  data?: MedicineAdherenceResponse;
  isLoading?: boolean;
}

// Custom Progress component with color support
function ColoredProgress({ value, colorClass, className }: { value: number; colorClass: string; className?: string }) {
  return (
    <ProgressPrimitive.Root
      className={cn("relative h-2 w-full overflow-hidden rounded-full bg-secondary", className)}
    >
      <ProgressPrimitive.Indicator
        className={cn("h-full transition-all", colorClass)}
        style={{ transform: `translateX(-${100 - (value || 0)}%)` }}
      />
    </ProgressPrimitive.Root>
  );
}

export default function MedicineAdherenceCard({ data, isLoading }: MedicineAdherenceCardProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-semibold">Adherence by Medicine</CardTitle>
          <p className="text-sm text-muted-foreground">
            Your medication adherence breakdown by medicine
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="space-y-2">
                <div className="flex justify-between">
                  <div className="h-4 w-24 bg-muted rounded animate-pulse"></div>
                  <div className="h-4 w-12 bg-muted rounded animate-pulse"></div>
                </div>
                <div className="h-2 w-full bg-muted rounded animate-pulse"></div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!data || data.medicines.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-semibold">Adherence by Medicine</CardTitle>
          <p className="text-sm text-muted-foreground">
            Your medication adherence breakdown by medicine
          </p>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <div className="w-12 h-12 rounded-xl bg-muted/10 flex items-center justify-center mb-3">
              <Minus className="h-6 w-6 text-muted" />
            </div>
            <p className="text-muted-foreground">No medication data available</p>
            <p className="text-sm text-muted-foreground mt-1">
              Start tracking your medications to see adherence by medicine
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const getAdherenceColor = (rate: number) => {
    if (rate >= 90) return 'bg-green-500';
    if (rate >= 70) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getAdherenceTextColor = (rate: number) => {
    if (rate >= 90) return 'text-green-600';
    if (rate >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getAdherenceIcon = (rate: number) => {
    if (rate >= 90) return <TrendingUp className="h-4 w-4 text-green-500" />;
    if (rate >= 70) return <Minus className="h-4 w-4 text-yellow-500" />;
    return <TrendingDown className="h-4 w-4 text-red-500" />;
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-lg font-semibold">Adherence by Medicine</CardTitle>
            <p className="text-sm text-muted-foreground">
              Your medication adherence breakdown by medicine
            </p>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold">{data.overall_adherence}%</p>
            <p className="text-xs text-muted-foreground">Overall</p>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {data.medicines.map((medicine) => (
            <div key={medicine.medicine_id} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {getAdherenceIcon(medicine.adherence_rate)}
                  <span className="font-medium text-foreground truncate max-w-[180px]">
                    {medicine.medicine_name}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className={getAdherenceTextColor(medicine.adherence_rate)}>
                    {medicine.adherence_rate}%
                  </span>
                  <span className="text-xs text-muted-foreground">
                    ({medicine.taken}/{medicine.total_scheduled})
                  </span>
                </div>
              </div>
              <ColoredProgress
                value={medicine.adherence_rate}
                colorClass={getAdherenceColor(medicine.adherence_rate)}
              />
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span>{medicine.taken} taken</span>
                <span>{medicine.skipped} skipped</span>
                <span>{medicine.missed} missed</span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
