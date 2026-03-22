'use client';

import { useState, useCallback } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowLeft, Heart } from 'lucide-react';
import { RelationshipAnalysis } from '@/components/divination/RelationshipAnalysis';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { BirthChartInput } from '@/components/birth-chart/birth-chart-input';
import { BirthChartInput as BirthChartInputType, Palace } from '@/types/birth-chart';
import { divinationApi } from '@/hooks/use-api';

export default function RelationshipPage() {
  const [chartData, setChartData] = useState<Record<string, unknown> | null>(null);
  const [palaces, setPalaces] = useState<Palace[] | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerateChart = useCallback(async (input: BirthChartInputType) => {
    setIsLoading(true);
    setError(null);

    const result = await divinationApi.generateChart(input);

    if (result.error) {
      setError(result.error);
      setIsLoading(false);
      return;
    }

    if (result.data) {
      // Store chart data for relationship analysis
      const data = result.data as { palaces?: Palace[] } & Record<string, unknown>;
      setChartData(data as unknown as Record<string, unknown>);
      if (data.palaces) {
        setPalaces(data.palaces);
      }
    }
    setIsLoading(false);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-700/50 bg-slate-900/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <Link
              href="/"
              className="flex items-center gap-2 text-slate-400 hover:text-slate-100 transition-colors"
            >
              <ArrowLeft className="h-4 w-4" />
              返回首页
            </Link>
            <div className="flex-1" />
            <div className="flex items-center gap-2">
              <Heart className="h-5 w-5 text-pink-500" />
              <span className="font-heading font-semibold text-slate-100">姻缘分析</span>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {!chartData ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-2xl mx-auto space-y-8"
          >
            {/* Hero */}
            <div className="text-center space-y-4">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-pink-500/10 border border-pink-500/20 mb-4">
                <Heart className="h-4 w-4 text-pink-500" />
                <span className="text-sm text-pink-400">姻缘感情分析</span>
              </div>
              <h1 className="text-3xl font-heading font-bold text-slate-100">
                姻缘感情运势分析
              </h1>
              <p className="text-slate-400 max-w-lg mx-auto">
                输入您的出生信息，我们将基于紫微斗数命盘分析您的姻缘感情运势，
                包括婚姻早晚、配偶特征、桃花运势等。
              </p>
            </div>

            {/* Input Form */}
            <Card>
              <CardHeader>
                <CardTitle>出生信息</CardTitle>
              </CardHeader>
              <CardContent>
                <BirthChartInput onSubmit={handleGenerateChart} isLoading={isLoading} />
                {error && (
                  <div className="mt-4 p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
                    {error}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Features */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card className="bg-slate-800/50 border-slate-700/50">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="p-2 rounded-lg bg-pink-500/20">
                      <Heart className="h-4 w-4 text-pink-400" />
                    </div>
                    <span className="font-semibold text-slate-100">婚姻分析</span>
                  </div>
                  <p className="text-sm text-slate-400">
                    分析您的婚姻时间、建议婚龄和婚姻质量
                  </p>
                </CardContent>
              </Card>

              <Card className="bg-slate-800/50 border-slate-700/50">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="p-2 rounded-lg bg-rose-500/20">
                      <span className="text-lg">👤</span>
                    </div>
                    <span className="font-semibold text-slate-100">配偶特征</span>
                  </div>
                  <p className="text-sm text-slate-400">
                    预测未来配偶的外貌、性格和事业倾向
                  </p>
                </CardContent>
              </Card>

              <Card className="bg-slate-800/50 border-slate-700/50">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="p-2 rounded-lg bg-pink-500/20">
                      <span className="text-lg">🌸</span>
                    </div>
                    <span className="font-semibold text-slate-100">桃花运势</span>
                  </div>
                  <p className="text-sm text-slate-400">
                    分析您的桃花等级和桃花旺的年龄
                  </p>
                </CardContent>
              </Card>

              <Card className="bg-slate-800/50 border-slate-700/50">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="p-2 rounded-lg bg-[#D4AF37]/20">
                      <span className="text-lg">💡</span>
                    </div>
                    <span className="font-semibold text-slate-100">婚姻建议</span>
                  </div>
                  <p className="text-sm text-slate-400">
                    根据命盘给出针对性的婚姻建议
                  </p>
                </CardContent>
              </Card>
            </div>
          </motion.div>
        ) : (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="max-w-4xl mx-auto"
          >
            <RelationshipAnalysis chartData={chartData} />

            {/* Regenerate Button */}
            <div className="mt-8 text-center">
              <Button
                onClick={() => {
                  setChartData(null);
                  setPalaces(null);
                }}
                variant="outline"
                className="border-slate-600 text-slate-300 hover:bg-slate-800"
              >
                重新输入出生信息
              </Button>
            </div>
          </motion.div>
        )}
      </main>
    </div>
  );
}
