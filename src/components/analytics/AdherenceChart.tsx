import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { CHART_COLORS } from '@/lib/constants';
import type { DailyAdherenceData } from '@/lib/reminders-api';

interface AdherenceChartProps {
  data?: DailyAdherenceData[];
  isLoading?: boolean;
}

// Mock data for fallback
const mockData = [
  { day: 'Mon', adherence: 85, target: 90 },
  { day: 'Tue', adherence: 90, target: 90 },
  { day: 'Wed', adherence: 78, target: 90 },
  { day: 'Thu', adherence: 95, target: 90 },
  { day: 'Fri', adherence: 88, target: 90 },
  { day: 'Sat', adherence: 92, target: 90 },
  { day: 'Sun', adherence: 87, target: 90 },
];

export default function AdherenceChart({ data, isLoading }: AdherenceChartProps) {
  const chartData = data ? data.map(item => ({
    day: item.day,
    adherence: item.adherence_rate,
    target: 90,
    scheduled: item.scheduled,
    taken: item.taken,
  })) : mockData;

  const averageAdherence = data && data.length > 0
    ? Math.round(data.reduce((acc, curr) => acc + curr.adherence_rate, 0) / data.length)
    : Math.round(chartData.reduce((acc, curr) => acc + curr.adherence, 0) / chartData.length);

  if (isLoading) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <div>
            <CardTitle className="text-lg font-semibold">Weekly Adherence</CardTitle>
            <p className="text-sm text-muted-foreground mt-1">
              Your medication adherence over the past week
            </p>
          </div>
          <div className="text-right">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-muted" />
              <span className="text-2xl font-bold text-muted">--%</span>
            </div>
            <p className="text-xs text-muted-foreground">Average adherence</p>
          </div>
        </CardHeader>
        <CardContent>
          <div className="h-[250px] mt-4 flex items-center justify-center">
            <div className="animate-pulse flex flex-col items-center">
              <div className="h-8 w-32 bg-muted rounded mb-2"></div>
              <div className="h-4 w-24 bg-muted rounded"></div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div>
          <CardTitle className="text-lg font-semibold">Weekly Adherence</CardTitle>
          <p className="text-sm text-muted-foreground mt-1">
            Your medication adherence over the past week
          </p>
        </div>
        <div className="text-right">
          <div className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-success" />
            <span className="text-2xl font-bold text-foreground">{averageAdherence}%</span>
          </div>
          <p className="text-xs text-muted-foreground">Average adherence</p>
        </div>
      </CardHeader>
      <CardContent>
        <div className="h-[250px] mt-4">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="adherenceGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={CHART_COLORS.primary} stopOpacity={0.3} />
                  <stop offset="95%" stopColor={CHART_COLORS.primary} stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis
                dataKey="day"
                stroke="hsl(var(--muted-foreground))"
                fontSize={12}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                stroke="hsl(var(--muted-foreground))"
                fontSize={12}
                tickLine={false}
                axisLine={false}
                domain={[0, 100]}
                tickFormatter={(value) => `${value}%`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '8px',
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
                }}
                labelStyle={{ color: 'hsl(var(--foreground))' }}
                formatter={(value: number, name: string) => {
                  if (name === 'Adherence') {
                    return [`${value}%`, 'Adherence'];
                  }
                  if (name === 'scheduled') {
                    return [value, 'Scheduled'];
                  }
                  if (name === 'taken') {
                    return [value, 'Taken'];
                  }
                  return [value, name];
                }}
                labelFormatter={(label) => `${label}`}
              />
              <Area
                type="monotone"
                dataKey="adherence"
                stroke={CHART_COLORS.primary}
                strokeWidth={2}
                fill="url(#adherenceGradient)"
              />
              <Area
                type="monotone"
                dataKey="target"
                stroke={CHART_COLORS.muted}
                strokeWidth={1}
                strokeDasharray="5 5"
                fill="transparent"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        <div className="flex items-center justify-center gap-6 mt-4">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: CHART_COLORS.primary }} />
            <span className="text-sm text-muted-foreground">Adherence</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full border-2 border-dashed" style={{ borderColor: CHART_COLORS.muted }} />
            <span className="text-sm text-muted-foreground">Target (90%)</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
