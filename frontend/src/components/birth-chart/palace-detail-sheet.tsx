'use client';

import { memo } from 'react';
import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Palace } from '@/types/birth-chart';
import { StarBadge } from './star-badge';
import { TransformBadge } from './transform-badge';

interface PalaceDetailSheetProps {
  palace: Palace | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  className?: string;
}

const palaceDescriptions: Record<string, string> = {
  '命宫': '代表本人先天命格、生命活力',
  '父母宫': '代表父母关系、家庭背景',
  '兄弟宫': '代表兄弟姐妹、合作关系',
  '夫妻宫': '代表婚姻感情、配偶情况',
  '子女宫': '代表子女缘分、晚辈关系',
  '财帛宫': '代表财运、收入状况',
  '疾厄宫': '代表健康状况、疾病',
  '迁移宫': '代表外出发展、旅行运势',
  '仆役宫': '代表下属、朋友关系',
  '官禄宫': '代表事业发展、职业运势',
  '田宅宫': '代表房产、不动产',
  '福德宫': '代表福气、享受、精神层面',
};

export const PalaceDetailSheet = memo(function PalaceDetailSheet({
  palace,
  open,
  onOpenChange,
  className,
}: PalaceDetailSheetProps) {
  if (!palace) return null;

  const description = palaceDescriptions[palace.name] || '';

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="w-[400px] sm:w-[540px] overflow-y-auto">
        <SheetHeader>
          <SheetTitle className="font-heading text-xl">
            {palace.name}
          </SheetTitle>
        </SheetHeader>

        <div className="mt-6 space-y-6">
          {/* Basic Info */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">基本信息</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex justify-between">
                <span className="text-slate-400">天干</span>
                <span className="font-mono">{palace.tiangan}</span>
              </div>
              {description && (
                <div className="text-sm text-slate-400 pt-2 border-t border-slate-700">
                  {description}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Stars */}
          {palace.stars.length > 0 && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">星曜 ({palace.stars.length})</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {palace.stars.map((star) => (
                    <StarBadge
                      key={star.name}
                      star={star}
                      size="md"
                      showGlow={star.level === 'major'}
                    />
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Transforms */}
          {palace.transforms && palace.transforms.length > 0 && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">四化曜</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {palace.transforms.map((transform) => (
                    <div
                      key={transform.type}
                      className="flex items-center justify-between"
                    >
                      <TransformBadge transform={transform} size="sm" />
                      <span className="text-sm text-slate-400">
                        {transform.star}
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Period Info */}
          {(palace.daxian || palace.liunian) && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">运势</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {palace.daxian && (
                  <div className="flex items-center justify-between">
                    <Badge variant="outline" className="border-accent text-accent">
                      大限
                    </Badge>
                    <span>{palace.daxian}</span>
                  </div>
                )}
                {palace.liunian && (
                  <div className="flex items-center justify-between">
                    <Badge variant="outline" className="border-blue-500 text-blue-400">
                      流年
                    </Badge>
                    <span>{palace.liunian}</span>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
});

PalaceDetailSheet.displayName = 'PalaceDetailSheet';
