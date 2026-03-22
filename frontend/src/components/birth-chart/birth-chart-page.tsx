'use client';

import { useState, useCallback, memo } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { PalaceGrid } from './palace-grid';
import { PalaceDetailSheet } from './palace-detail-sheet';
import { BirthChartInput } from './birth-chart-input';
import { Palace, BirthChartInput as BirthChartInputType } from '@/types/birth-chart';

interface BirthChartPageProps {
  chart?: {
    id: string;
    palaces: Palace[];
  } | null;
  isLoading?: boolean;
  onGenerateChart: (input: BirthChartInputType) => void;
  className?: string;
}

// Demo data for preview
const demoPalaces: Palace[] = [
  { id: '1', name: '命宫', tiangan: '庚辛', stars: [{ name: '紫微', wuxing: '土', level: 'major' }, { name: '天机', wuxing: '水', level: 'major' }], transforms: [{ type: '化禄', star: '禄存', wuxing: '土' }] },
  { id: '2', name: '父母宫', tiangan: '壬癸', stars: [{ name: '太阳', wuxing: '火', level: 'major' }] },
  { id: '3', name: '兄弟宫', tiangan: '甲乙', stars: [{ name: '武曲', wuxing: '金', level: 'major' }, { name: '天府', wuxing: '土', level: 'major' }] },
  { id: '4', name: '夫妻宫', tiangan: '丙丁', stars: [{ name: '太阴', wuxing: '水', level: 'major' }], transforms: [{ type: '化忌', star: '忌', wuxing: '水' }] },
  { id: '5', name: '子女宫', tiangan: '戊己', stars: [{ name: '贪狼', wuxing: '木', level: 'major' }] },
  { id: '6', name: '财帛宫', tiangan: '庚辛', stars: [{ name: '天同', wuxing: '水', level: 'major' }, { name: '天梁', wuxing: '土', level: 'major' }] },
  { id: '7', name: '疾厄宫', tiangan: '壬癸', stars: [{ name: '廉贞', wuxing: '火', level: 'major' }] },
  { id: '8', name: '迁移宫', tiangan: '甲乙', stars: [{ name: '巨门', wuxing: '土', level: 'major' }] },
  { id: '9', name: '仆役宫', tiangan: '丙丁', stars: [{ name: '天相', wuxing: '水', level: 'major' }] },
  { id: '10', name: '官禄宫', tiangan: '戊己', stars: [{ name: '七杀', wuxing: '金', level: 'major' }] },
  { id: '11', name: '田宅宫', tiangan: '庚辛', stars: [{ name: '破军', wuxing: '水', level: 'major' }] },
  { id: '12', name: '福德宫', tiangan: '壬癸', stars: [{ name: '天机', wuxing: '水', level: 'major' }, { name: '天梁', wuxing: '土', level: 'major' }], transforms: [{ type: '化科', star: '科', wuxing: '木' }] },
];

export const BirthChartPage = memo(function BirthChartPage({
  chart,
  isLoading = false,
  onGenerateChart,
  className,
}: BirthChartPageProps) {
  const [activePalace, setActivePalace] = useState<Palace | null>(null);
  const [sheetOpen, setSheetOpen] = useState(false);

  const handlePalaceClick = useCallback((palace: Palace) => {
    setActivePalace(palace);
    setSheetOpen(true);
  }, []);

  const handleSubmit = useCallback((input: BirthChartInputType) => {
    onGenerateChart(input);
  }, [onGenerateChart]);

  // Use demo data if no chart is provided
  const displayPalaces = chart?.palaces || demoPalaces;

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="text-center">
        <h1 className="text-2xl font-heading text-accent mb-2">
          紫微斗数命盘
        </h1>
        <p className="text-slate-400 text-sm">
          输入出生信息，生成您的命盘分析
        </p>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left - Input Form */}
        <div className="lg:col-span-1">
          <BirthChartInput onSubmit={handleSubmit} isLoading={isLoading} />

          {/* Quick Info */}
          <Card className="mt-4">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">命盘说明</CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-slate-400 space-y-2">
              <p>紫微斗数是中国传统命理术数，通过出生时间推算命运。</p>
              <p>命盘分为十二宫，每宫包含星曜、天干、四化等信息。</p>
            </CardContent>
          </Card>
        </div>

        {/* Right - Chart Display */}
        <div className="lg:col-span-2">
          {isLoading ? (
            <div className="flex items-center justify-center h-[500px]">
              <div className="text-center">
                <Skeleton className="h-96 w-96 rounded-full mx-auto mb-4" />
                <p className="text-slate-400">排盘中...</p>
              </div>
            </div>
          ) : (
            <Tabs defaultValue="chart" className="w-full">
              <TabsList className="mb-4">
                <TabsTrigger value="chart">命盘</TabsTrigger>
                <TabsTrigger value="stars">星曜</TabsTrigger>
                <TabsTrigger value="transforms">四化</TabsTrigger>
              </TabsList>

              <TabsContent value="chart">
                <div className="relative">
                  <PalaceGrid
                    palaces={displayPalaces}
                    onPalaceClick={handlePalaceClick}
                    activePalaceId={activePalace?.id}
                    showStars
                    showTransforms
                  />
                </div>
              </TabsContent>

              <TabsContent value="stars">
                <Card>
                  <CardHeader>
                    <CardTitle>十四主星</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-2">
                      {[
                        '紫微', '天机', '太阳', '武曲', '天同', '廉贞',
                        '天府', '太阴', '贪狼', '巨门', '天相', '天梁',
                        '七杀', '破军',
                      ].map((star) => (
                        <div
                          key={star}
                          className="flex items-center gap-2 p-2 rounded bg-slate-800/50"
                        >
                          <div
                            className="w-3 h-3 rounded-full"
                            style={{
                              backgroundColor: `var(--star-${star}, #D4AF37)`,
                            }}
                          />
                          <span>{star}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="transforms">
                <Card>
                  <CardHeader>
                    <CardTitle>四化曜</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center gap-4 p-3 rounded bg-slate-800/50">
                      <span className="text-green-500 font-bold">化禄</span>
                      <span className="text-slate-400 text-sm">禄存 - 财运、福气</span>
                    </div>
                    <div className="flex items-center gap-4 p-3 rounded bg-slate-800/50">
                      <span className="text-red-500 font-bold">化权</span>
                      <span className="text-slate-400 text-sm">权威、事业</span>
                    </div>
                    <div className="flex items-center gap-4 p-3 rounded bg-slate-800/50">
                      <span className="text-blue-500 font-bold">化科</span>
                      <span className="text-slate-400 text-sm">学业、功名</span>
                    </div>
                    <div className="flex items-center gap-4 p-3 rounded bg-slate-800/50">
                      <span className="text-gray-500 font-bold">化忌</span>
                      <span className="text-slate-400 text-sm">挑战、阻碍</span>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          )}
        </div>
      </div>

      {/* Palace Detail Sheet */}
      <PalaceDetailSheet
        palace={activePalace}
        open={sheetOpen}
        onOpenChange={setSheetOpen}
      />
    </div>
  );
});

BirthChartPage.displayName = 'BirthChartPage';
