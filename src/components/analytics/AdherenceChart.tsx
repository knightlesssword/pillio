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

// Mock data for the last 7 days
const mockData = [
  { day: 'Mon', adherence: 85, target: 90 },
  { day: 'Tue', adherence: 90, target: 90 },
  { day: 'Wed', adherence: 78, target: 90 },
  { day: 'Thu', adherence: 95, target: 90 },
  { day: 'Fri', adherence: 88, target: 90 },
  { day: 'Sat', adherence: 92, target: 90 },
  { day: 'Sun', adherence: 87, target: 90 },
];

export default function AdherenceChart() {
  const averageAdherence = Math.round(
    mockData.reduce((acc, curr) => acc + curr.adherence, 0) / mockData.length
  );

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
            <AreaChart data={mockData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
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
                formatter={(value: number) => [`${value}%`, 'Adherence']}
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
