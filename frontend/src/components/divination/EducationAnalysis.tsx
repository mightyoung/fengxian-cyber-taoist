'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { BookOpen, GraduationCap, AlertTriangle, Lightbulb, Clock, Target, TrendingUp } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';

interface EducationAnalysisProps {
  chartData: Record<string, unknown>;
  timingTransforms?: Record<string, unknown> | null;
}

interface EducationData {
  learning_ability: 'excellent' | 'good' | 'fair' | 'weak' | 'very_weak';
  learning_score: number;
  education_level_hint: 'doctor' | 'master' | 'bachelor' | 'associate' | 'high_school';
  best_study_ages: number[];
  weak_subjects: string[];
  academic_risks: string[];
  study_tips: string[];
}

const LEARNING_ABILITY_LABELS = {
  excellent: '聪颖过人',
  good: '聪明伶俐',
  fair: '中等平平',
  weak: '学习吃力',
  very_weak: '难以学习',
};

const LEARNING_ABILITY_COLORS = {
  excellent: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
  good: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
  fair: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20',
  weak: 'bg-orange-500/10 text-orange-500 border-orange-500/20',
  very_weak: 'bg-red-500/10 text-red-500 border-red-500/20',
};

const EDUCATION_LEVEL_LABELS = {
  doctor: '博士及以上',
  master: '硕士',
  bachelor: '本科',
  associate: '大专',
  high_school: '高中及以下',
};

const EDUCATION_LEVEL_COLORS = {
  doctor: 'bg-purple-500/10 text-purple-500 border-purple-500/20',
  master: 'bg-indigo-500/10 text-indigo-500 border-indigo-500/20',
  bachelor: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
  associate: 'bg-cyan-500/10 text-cyan-500 border-cyan-500/20',
  high_school: 'bg-slate-500/10 text-slate-500 border-slate-500/20',
};

export async function analyzeEducation(
  chartData: Record<string, unknown>,
  timingTransforms?: Record<string, unknown> | null
): Promise<EducationData> {
  const response = await fetch('/api/divination/education/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chart: chartData,
      timing_transforms: timingTransforms,
    }),
  });

  if (!response.ok) {
    throw new Error('Failed to analyze education');
  }

  const result = await response.json();
  if (!result.success) {
    throw new Error(result.error || 'Analysis failed');
  }

  return result.data as EducationData;
}

export function EducationAnalysis({ chartData, timingTransforms }: EducationAnalysisProps) {
  const [data, setData] = useState<EducationData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await analyzeEducation(chartData, timingTransforms);
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : '分析失败');
    } finally {
      setLoading(false);
    }
  };

  if (!data && !loading) {
    return (
      <Card className="border-blue-500/20 bg-gradient-to-br from-blue-950/30 to-slate-900/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-blue-400">
            <BookOpen className="h-5 w-5" />
            学业分析
          </CardTitle>
          <CardDescription>分析命盘中的学业运势</CardDescription>
        </CardHeader>
        <CardContent>
          <Button
            onClick={handleAnalyze}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-500"
          >
            {loading ? '分析中...' : '开始学业分析'}
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (loading) {
    return (
      <Card className="border-blue-500/20 bg-gradient-to-br from-blue-950/30 to-slate-900/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-blue-400">
            <BookOpen className="h-5 w-5" />
            学业分析
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
            学业分析
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
        <Card className="border-blue-500/20 bg-gradient-to-br from-blue-950/30 to-slate-900/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-blue-400">
              <BookOpen className="h-5 w-5" />
              学业分析结果
            </CardTitle>
            <CardDescription>基于命盘信息分析学业运势</CardDescription>
          </CardHeader>
        </Card>
      </motion.div>

      {/* Learning Ability & Score */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card className="border-blue-500/20 bg-slate-900/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-blue-400">
              <Target className="h-5 w-5" />
              学习能力评估
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Badge
                  className={`text-sm px-3 py-1 ${LEARNING_ABILITY_COLORS[data.learning_ability]}`}
                >
                  {LEARNING_ABILITY_LABELS[data.learning_ability]}
                </Badge>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-3xl font-bold text-blue-400">{data.learning_score}</span>
                <span className="text-slate-400">/ 100</span>
              </div>
            </div>
            <div className="w-full bg-slate-800 rounded-full h-2">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${data.learning_score}%` }}
                transition={{ duration: 1, delay: 0.3 }}
                className="h-full bg-gradient-to-r from-blue-500 to-blue-400 rounded-full"
              />
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Education Level Prediction */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Card className="border-purple-500/20 bg-slate-900/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-purple-400">
              <GraduationCap className="h-5 w-5" />
              学历层次预测
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Badge
              className={`text-sm px-3 py-1.5 ${EDUCATION_LEVEL_COLORS[data.education_level_hint]}`}
            >
              {EDUCATION_LEVEL_LABELS[data.education_level_hint]}
            </Badge>
          </CardContent>
        </Card>
      </motion.div>

      {/* Best Study Ages */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <Card className="border-cyan-500/20 bg-slate-900/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-cyan-400">
              <Clock className="h-5 w-5" />
              最佳学习年龄
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {data.best_study_ages.map((age) => (
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

      {/* Weak Subjects */}
      {data.weak_subjects.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card className="border-orange-500/20 bg-slate-900/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-orange-400">
                <AlertTriangle className="h-5 w-5" />
                薄弱学科提醒
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {data.weak_subjects.map((subject) => (
                  <Badge
                    key={subject}
                    variant="outline"
                    className="border-orange-500/30 text-orange-400"
                  >
                    {subject}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Academic Risks */}
      {data.academic_risks.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card className="border-red-500/20 bg-slate-900/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-red-400">
                <TrendingUp className="h-5 w-5" />
                学业风险
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {data.academic_risks.map((risk, index) => (
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

      {/* Study Tips */}
      {data.study_tips.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <Card className="border-emerald-500/20 bg-slate-900/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-emerald-400">
                <Lightbulb className="h-5 w-5" />
                学习建议
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {data.study_tips.map((tip, index) => (
                  <li key={index} className="flex items-start gap-2 text-emerald-300">
                    <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-emerald-500 flex-shrink-0" />
                    {tip}
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

export default EducationAnalysis;
