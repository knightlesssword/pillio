import React, { useEffect, useState } from 'react';
import PageHeader from '@/components/common/PageHeader';
import AdherenceChart from '@/components/analytics/AdherenceChart';
import MedicineAdherenceCard from '@/components/analytics/MedicineAdherenceCard';
import { Card, CardContent } from '@/components/ui/card';
import { BarChart3, TrendingUp, Calendar } from 'lucide-react';
import { remindersApi } from '@/lib/reminders-api';
import type { AdherenceStats, DayStreak, DailyAdherenceData, MedicineAdherenceResponse } from '@/lib/reminders-api';

export default function ReportsPage() {
  const [adherenceStats, setAdherenceStats] = useState<AdherenceStats | null>(null);
  const [dayStreak, setDayStreak] = useState<DayStreak | null>(null);
  const [dailyAdherence, setDailyAdherence] = useState<DailyAdherenceData[]>([]);
  const [medicineAdherence, setMedicineAdherence] = useState<MedicineAdherenceResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Calculate date range (last 30 days)
  const endDate = new Date().toISOString().split('T')[0];
  const startDate = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      setError(null);

      try {
        // Fetch all data in parallel
        const [statsRes, streakRes, dailyRes, medicineRes] = await Promise.all([
          remindersApi.getAdherenceStats(startDate, endDate),
          remindersApi.getAdherenceStreak(),
          remindersApi.getDailyAdherence(7),
          remindersApi.getMedicineAdherence(startDate, endDate),
        ]);

        setAdherenceStats(statsRes.data);
        setDayStreak(streakRes.data);
        setDailyAdherence(dailyRes.data);
        setMedicineAdherence(medicineRes.data);
      } catch (err) {
        console.error('Error fetching reports data:', err);
        setError('Failed to load reports data. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [startDate, endDate]);

  if (error) {
    return (
      <div className="space-y-6">
        <PageHeader title="Reports" description="Analytics and insights about your medication adherence" />
        <Card className="p-8 text-center">
          <div className="flex flex-col items-center justify-center">
            <div className="w-12 h-12 rounded-xl bg-destructive/10 flex items-center justify-center mb-3">
              <BarChart3 className="h-6 w-6 text-destructive" />
            </div>
            <p className="text-destructive font-medium">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90"
            >
              Retry
            </button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Reports" description="Analytics and insights about your medication adherence" />

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-6 text-center">
            <div className="w-12 h-12 rounded-xl bg-success/10 flex items-center justify-center mx-auto mb-3">
              <TrendingUp className="h-6 w-6 text-success" />
            </div>
            {isLoading ? (
              <>
                <div className="h-8 w-16 bg-muted rounded animate-pulse mx-auto mb-2"></div>
                <div className="h-4 w-24 bg-muted rounded animate-pulse mx-auto"></div>
              </>
            ) : (
              <>
                <p className="text-3xl font-bold text-foreground">
                  {adherenceStats?.adherence_rate || 0}%
                </p>
                <p className="text-sm text-muted-foreground">Overall Adherence</p>
              </>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6 text-center">
            <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mx-auto mb-3">
              <Calendar className="h-6 w-6 text-primary" />
            </div>
            {isLoading ? (
              <>
                <div className="h-8 w-16 bg-muted rounded animate-pulse mx-auto mb-2"></div>
                <div className="h-4 w-24 bg-muted rounded animate-pulse mx-auto"></div>
              </>
            ) : (
              <>
                <p className="text-3xl font-bold text-foreground">
                  {dayStreak?.current_streak || 0}
                </p>
                <p className="text-sm text-muted-foreground">Day Streak</p>
              </>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6 text-center">
            <div className="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center mx-auto mb-3">
              <BarChart3 className="h-6 w-6 text-accent" />
            </div>
            {isLoading ? (
              <>
                <div className="h-8 w-16 bg-muted rounded animate-pulse mx-auto mb-2"></div>
                <div className="h-4 w-24 bg-muted rounded animate-pulse mx-auto"></div>
              </>
            ) : (
              <>
                <p className="text-3xl font-bold text-foreground">
                  {adherenceStats?.taken || 0}
                </p>
                <p className="text-sm text-muted-foreground">Doses Taken (30 days)</p>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <AdherenceChart data={dailyAdherence} isLoading={isLoading} />
        </div>
        <div>
          <MedicineAdherenceCard data={medicineAdherence} isLoading={isLoading} />
        </div>
      </div>

      {/* Additional Stats */}
      {!isLoading && adherenceStats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-foreground">{adherenceStats.total_scheduled}</p>
              <p className="text-sm text-muted-foreground">Total Scheduled</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-success">{adherenceStats.taken}</p>
              <p className="text-sm text-muted-foreground">Taken</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-warning">{adherenceStats.skipped}</p>
              <p className="text-sm text-muted-foreground">Skipped</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-destructive">{adherenceStats.missed}</p>
              <p className="text-sm text-muted-foreground">Missed</p>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
