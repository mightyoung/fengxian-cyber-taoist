'use client';

import { memo } from 'react';
import { motion } from 'framer-motion';
import { Users, MessageCircle, TrendingUp, Star } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useReportMetrics } from '@/hooks/use-report';
import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils';
import { ANIMATIONS } from '@/lib/animation';

interface ReportMetricsProps {
  reportId: string;
  className?: string;
}

function ReportMetrics({ reportId, className }: ReportMetricsProps) {
  const { data: metrics, isLoading } = useReportMetrics(reportId);

  if (isLoading) {
    return (
      <div className={cn('grid grid-cols-4 gap-4', className)}>
        {[1, 2, 3, 4].map((i) => (
          <Skeleton key={i} className="h-24 bg-slate-800" />
        ))}
      </div>
    );
  }

  if (!metrics) return null;

  const metricCards = [
    {
      title: 'Total Posts',
      value: metrics.totalPosts,
      icon: MessageCircle,
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/10',
    },
    {
      title: 'Engagement',
      value: metrics.totalEngagement,
      icon: TrendingUp,
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-500/10',
    },
    {
      title: 'Sentiment Score',
      value: `${(metrics.sentimentScore * 100).toFixed(0)}%`,
      icon: Star,
      color: 'text-amber-400',
      bgColor: 'bg-amber-500/10',
    },
    {
      title: 'Active Agents',
      value: metrics.topInfluencers.length,
      icon: Users,
      color: 'text-purple-400',
      bgColor: 'bg-purple-500/10',
    },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: ANIMATIONS.standard.duration / 1000 }}
      className={cn('grid grid-cols-2 md:grid-cols-4 gap-4', className)}
    >
      {metricCards.map((metric) => (
        <Card
          key={metric.title}
          className="bg-slate-900/50 border-slate-800 hover:border-slate-700 transition-colors"
        >
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-slate-400">
              {metric.title}
            </CardTitle>
            <div className={cn('p-2 rounded-lg', metric.bgColor)}>
              <metric.icon className={cn('h-4 w-4', metric.color)} />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-100">
              {typeof metric.value === 'number'
                ? metric.value.toLocaleString()
                : metric.value}
            </div>
          </CardContent>
        </Card>
      ))}

      {/* Top Influencers */}
      {metrics.topInfluencers.length > 0 && (
        <Card className="col-span-2 md:col-span-4 bg-slate-900/50 border-slate-800">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-slate-400">
              Top Influencers
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {metrics.topInfluencers.slice(0, 5).map((influencer, index) => (
                <div
                  key={index}
                  className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 rounded-full"
                >
                  <span className="text-sm text-slate-200">{influencer.name}</span>
                  <span className="text-xs text-slate-500">
                    {influencer.score.toFixed(1)}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </motion.div>
  );
}

export const ReportMetricsMemoized = memo(ReportMetrics);
ReportMetricsMemoized.displayName = 'ReportMetrics';
