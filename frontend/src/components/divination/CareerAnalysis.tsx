'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Briefcase, TrendingUp, AlertTriangle, Lightbulb, Clock, Star, Target, Zap } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';

export interface CareerAnalysisProps {
  chartData: Record<string, unknown>;
  timingTransforms?: Record<string, unknown> | null;
}

interface CareerData {
  career_level: 'excellent' | 'good' | 'fair' | 'challenging' | 'weak';
  career_score: number;
  career_direction: Array<'official' | 'business' | 'creative' | 'technical' | 'service' | 'financial'>;
  best_palace: string;
  career_peak_ages: number[];
  potential_risks: string[];
  recommendations: string[];
}

const CAREER_LEVEL_LABELS = {
  excellent: '事业辉煌',
  good: '事业顺利',
  fair: '事业平稳',
  challenging: '事业挑战',
  weak: '事业薄弱',
};

const CAREER_LEVEL_COLORS = {
  excellent: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
  good: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
  fair: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20',
  challenging: 'bg-orange-500/10 text-orange-500 border-orange-500/20',
  weak: 'bg-red-500/10 text-red-500 border-red-500/20',
};

const CAREER_DIRECTION_LABELS = {
  official: '公务/管理',
  business: '商业/贸易',
  creative: '创意/艺术',
  technical: '技术/专业',
  service: '服务/教育',
  financial: '金融/投资',
};

const CAREER_DIRECTION_COLORS = {
  official: 'bg-purple-500/10 text-purple-500 border-purple-500/20',
  business: 'bg-amber-500/10 text-amber-500 border-amber-500/20',
  creative: 'bg-pink-500/10 text-pink-500 border-pink-500/20',
  technical: 'bg-cyan-500/10 text-cyan-500 border-cyan-500/20',
  service: 'bg-green-500/10 text-green-500 border-green-500/20',
  financial: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
};

const CAREER_DIRECTION_ICONS = {
  official: Target,
  business: TrendingUp,
  creative: Star,
  technical: Zap,
  service: Lightbulb,
  financial: Briefcase,
};

export async function analyzeCareer(
  chartData: Record<string, unknown>,
  timingTransforms?: Record<string, unknown> | null
): Promise<CareerData> {
  const response = await fetch('/api/divination/career/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chart: chartData,
      timing_transforms: timingTransforms,
    }),
  });

  if (!response.ok) {
    throw new Error('Failed to analyze career');
  }

  const result = await response.json();
  if (!result.success) {
    throw new Error(result.error || 'Analysis failed');
  }

  return result.data as CareerData;
}

export function CareerAnalysis({ chartData, timingTransforms }: CareerAnalysisProps) {
  const [data, setData] = useState<CareerData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await analyzeCareer(chartData, timingTransforms);
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : '分析失败');
    } finally {
      setLoading(false);
    }
  };

  if (!data && !loading) {
    return (
      <Card className="border-amber-500/20 bg-gradient-to-br from-amber-950/30 to-slate-900/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-amber-400">
            <Briefcase className="h-5 w-5" />
            事业分析
          </CardTitle>
          <CardDescription>分析命盘中的事业运势</CardDescription>
        </CardHeader>
        <CardContent>
          <Button
            onClick={handleAnalyze}
            disabled={loading}
            className="bg-amber-600 hover:bg-amber-500"
          >
            {loading ? '分析中...' : '开始事业分析'}
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (loading) {
    return (
      <Card className="border-amber-500/20 bg-gradient-to-br from-amber-950/30 to-slate-900/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-amber-400">
            <Briefcase className="h-5 w-5" />
            事业分析
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-24 w-full" />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="border-red-500/20 bg-gradient-to-br from-red-950/30 to-slate-900/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-red-400">
            <AlertTriangle className="h-5 w-5" />
            事业分析
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-red-400">{error}</p>
          <Button onClick={handleAnalyze} className="mt-4">
            重试
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (!data) return null;

  return (
    <div className="space-y-6">
      {/* Header Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <Card className="border-amber-500/20 bg-gradient-to-br from-amber-950/30 to-slate-900/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-amber-400">
              <Briefcase className="h-5 w-5" />
              事业分析结果
            </CardTitle>
            <CardDescription>基于命盘信息分析事业运势</CardDescription>
          </CardHeader>
        </Card>
      </motion.div>

      {/* Career Level & Score */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card className="border-amber-500/20 bg-slate-900/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-amber-400">
              <TrendingUp className="h-5 w-5" />
              事业等级评估
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Badge
                  className={`text-sm px-3 py-1 ${CAREER_LEVEL_COLORS[data.career_level]}`}
                >
                  {CAREER_LEVEL_LABELS[data.career_level]}
                </Badge>
                <span className="text-slate-400 text-sm">
                  最强宫位: {data.best_palace}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-3xl font-bold text-amber-400">{data.career_score}</span>
                <span className="text-slate-400">/ 100</span>
              </div>
            </div>
            <div className="w-full bg-slate-800 rounded-full h-2">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${data.career_score}%` }}
                transition={{ duration: 1, delay: 0.3 }}
                className="h-full bg-gradient-to-r from-amber-500 to-amber-400 rounded-full"
              />
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Career Direction */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Card className="border-purple-500/20 bg-slate-900/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-purple-400">
              <Star className="h-5 w-5" />
              事业发展方向
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3">
              {data.career_direction.map((direction) => {
                const Icon = CAREER_DIRECTION_ICONS[direction];
                return (
                  <Badge
                    key={direction}
                    className={`text-sm px-3 py-1.5 ${CAREER_DIRECTION_COLORS[direction]}`}
                  >
                    <Icon className="h-4 w-4 mr-1.5" />
                    {CAREER_DIRECTION_LABELS[direction]}
                  </Badge>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Career Peak Ages */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <Card className="border-cyan-500/20 bg-slate-900/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-cyan-400">
              <Clock className="h-5 w-5" />
              事业高峰期年龄
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {data.career_peak_ages.map((age) => (
                <Badge
                  key={age}
                  variant="outline"
                  className="border-cyan-500/30 text-cyan-400 px-3 py-1"
                >
                  {age}岁
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Potential Risks */}
      {data.potential_risks.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card className="border-red-500/20 bg-slate-900/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-red-400">
                <AlertTriangle className="h-5 w-5" />
                潜在事业风险
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {data.potential_risks.map((risk, index) => (
                  <li key={index} className="flex items-start gap-2 text-red-300">
                    <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-red-500 flex-shrink-0" />
                    {risk}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Career Recommendations */}
      {data.recommendations.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card className="border-emerald-500/20 bg-slate-900/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-emerald-400">
                <Lightbulb className="h-5 w-5" />
                事业建议
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {data.recommendations.map((recommendation, index) => (
                  <li key={index} className="flex items-start gap-2 text-emerald-300">
                    <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-emerald-500 flex-shrink-0" />
                    {recommendation}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </div>
  );
}

export default CareerAnalysis;
