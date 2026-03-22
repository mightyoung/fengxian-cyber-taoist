'use client';

import { useState, useCallback, memo } from 'react';
import { motion } from 'framer-motion';
import { Heart, BellRing, User, Sparkles, AlertTriangle, Lightbulb, Clock, Star } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { divinationApi } from '@/hooks/use-api';

// Types matching the backend API response
type MarriageTiming = 'early' | 'normal' | 'late' | 'very_late';
type MarriageQuality = 'excellent' | 'good' | 'fair' | 'challenging' | 'difficult';
type PeachBlossomLevel = 'strong' | 'moderate' | 'weak' | 'none';

interface SpouseFeatures {
  star_influence: string;
  appearance: string;
  personality: string;
  career: string;
  age_difference: string;
}

interface RelationshipAnalysisData {
  marriage_timing: MarriageTiming;
  marriage_age_hint: number;
  marriage_quality: MarriageQuality;
  spouse_features: SpouseFeatures;
  peach_blossom: PeachBlossomLevel;
  peach_blossom_ages: number[];
  relationship_risks: string[];
  marriage_advice: string[];
}

// Mapping for display
const marriageTimingLabels: Record<MarriageTiming, { label: string; description: string }> = {
  early: { label: '早婚', description: '25岁前' },
  normal: { label: '正常婚龄', description: '25-32岁' },
  late: { label: '晚婚', description: '32-40岁' },
  very_late: { label: '晚婚', description: '40岁后' },
};

const marriageQualityLabels: Record<MarriageQuality, { label: string; color: string }> = {
  excellent: { label: '美满', color: 'text-green-400' },
  good: { label: '良好', color: 'text-emerald-400' },
  fair: { label: '一般', color: 'text-yellow-400' },
  challenging: { label: '有挑战', color: 'text-orange-400' },
  difficult: { label: '困难', color: 'text-red-400' },
};

const peachBlossomLabels: Record<PeachBlossomLevel, { label: string; color: string }> = {
  strong: { label: '旺', color: 'text-pink-400' },
  moderate: { label: '中', color: 'text-rose-400' },
  weak: { label: '弱', color: 'text-slate-400' },
  none: { label: '无', color: 'text-gray-500' },
};

export interface RelationshipAnalysisProps {
  chartData: Record<string, unknown>;
  timingTransforms?: Record<string, unknown> | null;
  className?: string;
}

export const RelationshipAnalysis = memo(function RelationshipAnalysis({
  chartData,
  timingTransforms,
  className,
}: RelationshipAnalysisProps) {
  const [analysis, setAnalysis] = useState<RelationshipAnalysisData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    const result = await divinationApi.analyzeRelationship(chartData, timingTransforms || undefined);

    if (result.error) {
      setError(result.error);
      setIsLoading(false);
      return;
    }

    if (result.data) {
      setAnalysis(result.data as RelationshipAnalysisData);
    }
    setIsLoading(false);
  }, [chartData, timingTransforms]);

  if (!analysis && !isLoading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Heart className="h-5 w-5 text-pink-500" />
            姻缘分析
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-slate-400">
            基于命盘中的夫妻宫、桃花星曜等进行分析，解读您的姻缘感情运势。
          </p>
          <button
            onClick={handleAnalyze}
            disabled={isLoading}
            className="w-full py-3 px-4 bg-gradient-to-r from-pink-500 to-rose-500 hover:from-pink-600 hover:to-rose-600 text-white font-medium rounded-lg transition-all duration-200 disabled:opacity-50"
          >
            开始姻缘分析
          </button>
        </CardContent>
      </Card>
    );
  }

  if (isLoading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Heart className="h-5 w-5 text-pink-500" />
            姻缘分析
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Heart className="h-5 w-5 text-pink-500" />
            姻缘分析
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
            {error}
          </div>
          <button
            onClick={handleAnalyze}
            className="w-full py-3 px-4 bg-gradient-to-r from-pink-500 to-rose-500 hover:from-pink-600 hover:to-rose-600 text-white font-medium rounded-lg transition-all duration-200"
          >
            重试
          </button>
        </CardContent>
      </Card>
    );
  }

  if (!analysis) return null;

  const timing = marriageTimingLabels[analysis.marriage_timing];
  const quality = marriageQualityLabels[analysis.marriage_quality];
  const peach = peachBlossomLabels[analysis.peach_blossom];

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h2 className="text-2xl font-heading font-bold text-slate-100 flex items-center justify-center gap-2">
          <Heart className="h-6 w-6 text-pink-500" />
          姻缘感情分析
        </h2>
        <p className="text-slate-400 text-sm mt-2">
          基于命盘分析您的婚姻运势与感情走向
        </p>
      </motion.div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Marriage Timing */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="bg-gradient-to-br from-pink-500/10 to-rose-500/10 border-pink-500/20">
            <CardContent className="pt-6">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 rounded-lg bg-pink-500/20">
                  <Clock className="h-5 w-5 text-pink-400" />
                </div>
                <span className="text-sm text-slate-400">婚姻时间</span>
              </div>
              <p className="text-2xl font-bold text-pink-400">{timing.label}</p>
              <p className="text-sm text-slate-500 mt-1">{timing.description}</p>
            </CardContent>
          </Card>
        </motion.div>

        {/* Marriage Age */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="bg-gradient-to-br from-rose-500/10 to-pink-500/10 border-rose-500/20">
            <CardContent className="pt-6">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 rounded-lg bg-rose-500/20">
                  <BellRing className="h-5 w-5 text-rose-400" />
                </div>
                <span className="text-sm text-slate-400">建议婚龄</span>
              </div>
              <p className="text-2xl font-bold text-rose-400">
                {analysis.marriage_age_hint}岁
              </p>
              <p className="text-sm text-slate-500 mt-1">最佳结婚年龄</p>
            </CardContent>
          </Card>
        </motion.div>

        {/* Marriage Quality */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card className="bg-gradient-to-br from-emerald-500/10 to-pink-500/10 border-emerald-500/20">
            <CardContent className="pt-6">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 rounded-lg bg-emerald-500/20">
                  <Sparkles className="h-5 w-5 text-emerald-400" />
                </div>
                <span className="text-sm text-slate-400">婚姻质量</span>
              </div>
              <p className={`text-2xl font-bold ${quality.color}`}>
                {quality.label}
              </p>
              <p className="text-sm text-slate-500 mt-1">婚后生活预期</p>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Detailed Analysis Tabs */}
      <Tabs defaultValue="spouse" className="w-full">
        <TabsList className="mb-4">
          <TabsTrigger value="spouse">配偶特征</TabsTrigger>
          <TabsTrigger value="peach">桃花运势</TabsTrigger>
          <TabsTrigger value="risks">感情风险</TabsTrigger>
          <TabsTrigger value="advice">婚姻建议</TabsTrigger>
        </TabsList>

        {/* Spouse Features */}
        <TabsContent value="spouse">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <User className="h-5 w-5 text-pink-500" />
                配偶特征
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 rounded-lg bg-slate-800/50 space-y-3">
                  <div className="flex items-center gap-2">
                    <Star className="h-4 w-4 text-[#D4AF37]" />
                    <span className="text-sm text-slate-400">主星影响</span>
                  </div>
                  <p className="text-lg font-semibold text-slate-100">
                    {analysis.spouse_features.star_influence}
                  </p>
                </div>

                <div className="p-4 rounded-lg bg-slate-800/50 space-y-3">
                  <div className="flex items-center gap-2">
                    <User className="h-4 w-4 text-pink-400" />
                    <span className="text-sm text-slate-400">外貌特征</span>
                  </div>
                  <p className="text-lg font-semibold text-slate-100">
                    {analysis.spouse_features.appearance}
                  </p>
                </div>

                <div className="p-4 rounded-lg bg-slate-800/50 space-y-3">
                  <div className="flex items-center gap-2">
                    <Heart className="h-4 w-4 text-rose-400" />
                    <span className="text-sm text-slate-400">性格特点</span>
                  </div>
                  <p className="text-lg font-semibold text-slate-100">
                    {analysis.spouse_features.personality}
                  </p>
                </div>

                <div className="p-4 rounded-lg bg-slate-800/50 space-y-3">
                  <div className="flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-emerald-400" />
                    <span className="text-sm text-slate-400">事业倾向</span>
                  </div>
                  <p className="text-lg font-semibold text-slate-100">
                    {analysis.spouse_features.career}
                  </p>
                </div>
              </div>

              <div className="mt-4 p-4 rounded-lg bg-pink-500/10 border border-pink-500/20">
                <div className="flex items-center gap-2 mb-2">
                  <BellRing className="h-4 w-4 text-pink-400" />
                  <span className="text-sm text-pink-400">年龄差</span>
                </div>
                <p className="text-slate-100">
                  {analysis.spouse_features.age_difference}
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Peach Blossom */}
        <TabsContent value="peach">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Sparkles className="h-5 w-5 text-pink-500" />
                桃花运势
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-4 rounded-lg bg-gradient-to-r from-pink-500/20 to-rose-500/20 border border-pink-500/20">
                <div>
                  <p className="text-sm text-slate-400">桃花等级</p>
                  <p className={`text-3xl font-bold ${peach.color} mt-1`}>
                    {peach.label}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-slate-400">桃花旺的年龄</p>
                  <p className="text-lg font-semibold text-slate-100 mt-1">
                    {analysis.peach_blossom_ages.length > 0
                      ? analysis.peach_blossom_ages.join('、')
                      : '无特定年份'}
                  </p>
                </div>
              </div>

              <div className="p-4 rounded-lg bg-slate-800/50">
                <p className="text-sm text-slate-400 mb-2">桃花等级说明</p>
                {analysis.peach_blossom === 'strong' && (
                  <p className="text-slate-200">
                    桃花旺盛，人缘极佳，异性缘非常好，适合从事需要社交的工作。
                  </p>
                )}
                {analysis.peach_blossom === 'moderate' && (
                  <p className="text-slate-200">
                    桃花适中，有一定的异性缘，感情生活较为平稳。
                  </p>
                )}
                {analysis.peach_blossom === 'weak' && (
                  <p className="text-slate-200">
                    桃花较弱，感情进展较慢，专心事业发展更佳。
                  </p>
                )}
                {analysis.peach_blossom === 'none' && (
                  <p className="text-slate-200">
                    桃花平淡，感情缘分较浅，不宜强求。
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Relationship Risks */}
        <TabsContent value="risks">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <AlertTriangle className="h-5 w-5 text-orange-500" />
                感情风险
              </CardTitle>
            </CardHeader>
            <CardContent>
              {analysis.relationship_risks.length > 0 ? (
                <div className="space-y-3">
                  {analysis.relationship_risks.map((risk, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="flex items-start gap-3 p-4 rounded-lg bg-orange-500/10 border border-orange-500/20"
                    >
                      <AlertTriangle className="h-5 w-5 text-orange-400 mt-0.5" />
                      <p className="text-slate-200">{risk}</p>
                    </motion.div>
                  ))}
                </div>
              ) : (
                <div className="p-6 text-center">
                  <div className="inline-flex p-3 rounded-full bg-emerald-500/20 mb-3">
                    <Sparkles className="h-6 w-6 text-emerald-400" />
                  </div>
                  <p className="text-emerald-400 font-medium">感情顺利</p>
                  <p className="text-slate-400 text-sm mt-1">
                    您的命盘显示感情运势平稳，无明显风险
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Marriage Advice */}
        <TabsContent value="advice">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Lightbulb className="h-5 w-5 text-[#D4AF37]" />
                婚姻建议
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {analysis.marriage_advice.map((advice, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-start gap-3 p-4 rounded-lg bg-[#D4AF37]/10 border border-[#D4AF37]/20"
                  >
                    <Lightbulb className="h-5 w-5 text-[#D4AF37] mt-0.5" />
                    <p className="text-slate-200">{advice}</p>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
});

RelationshipAnalysis.displayName = 'RelationshipAnalysis';
