'use client';

import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Star, ChevronDown, ChevronUp, Sparkles, Shield, Zap } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

// ============================================================================
// Types
// ============================================================================

interface StarData {
  name: string;
  type: '正曜' | '辅曜' | '煞曜' | '杂曜';
  location: string;
  brightness?: '旺' | '得' | '利' | '平' | '陷' | '庙';
}

interface PalaceData {
  stars: StarData[];
  main_star: string;
  auxiliary_stars?: string[];
  malefic_stars?: string[];
  transforms: Record<string, string>;
  strength: '强' | '中' | '弱';
  location: string;
}

interface PalaceStarMapProps {
  palaces: Record<string, PalaceData>;
  chartInfo?: {
    year: number;
    month: number;
    day: number;
    hour: number;
    gan: string;
    zhi: string;
    wuxing: string;
    gender: string;
  };
  onPalaceClick?: (palaceName: string, palaceData: PalaceData) => void;
  className?: string;
}

// ============================================================================
// Constants
// ============================================================================

const PALACE_ORDER = [
  '命宫', '兄弟宫', '夫妻宫', '子女宫',
  '财帛宫', '疾厄宫', '迁移宫', '官禄宫',
  '田宅宫', '福德宫', '父母宫', '奴仆宫'
];

const PALACE_POSITIONS: Record<string, { angle: number }> = {
  '命宫': { angle: 0 },
  '兄弟宫': { angle: 30 },
  '夫妻宫': { angle: 60 },
  '子女宫': { angle: 90 },
  '财帛宫': { angle: 120 },
  '疾厄宫': { angle: 150 },
  '迁移宫': { angle: 180 },
  '官禄宫': { angle: 210 },
  '田宅宫': { angle: 240 },
  '福德宫': { angle: 270 },
  '父母宫': { angle: 300 },
  '奴仆宫': { angle: 330 },
};

// Star type colors
const STAR_COLORS = {
  正曜: {
    bg: 'bg-amber-500/20',
    border: 'border-amber-500/50',
    text: 'text-amber-400',
    glow: 'shadow-amber-500/30',
  },
  辅曜: {
    bg: 'bg-emerald-500/20',
    border: 'border-emerald-500/50',
    text: 'text-emerald-400',
    glow: 'shadow-emerald-500/30',
  },
  煞曜: {
    bg: 'bg-red-500/20',
    border: 'border-red-500/50',
    text: 'text-red-400',
    glow: 'shadow-red-500/30',
  },
  杂曜: {
    bg: 'bg-slate-500/20',
    border: 'border-slate-500/50',
    text: 'text-slate-400',
    glow: 'shadow-slate-500/30',
  },
};

// Transform colors
const TRANSFORM_COLORS = {
  '化禄': { bg: 'bg-green-500/20', text: 'text-green-400', border: 'border-green-500' },
  '化权': { bg: 'bg-red-500/20', text: 'text-red-400', border: 'border-red-500' },
  '化科': { bg: 'bg-blue-500/20', text: 'text-blue-400', border: 'border-blue-500' },
  '化忌': { bg: 'bg-purple-500/20', text: 'text-purple-400', border: 'border-purple-500' },
};

// Strength colors
const STRENGTH_COLORS = {
  '强': 'text-emerald-400',
  '中': 'text-yellow-400',
  '弱': 'text-red-400',
};

// ============================================================================
// Components
// ============================================================================

function StarBadge({ name, type }: { name: string; type: StarData['type'] }) {
  const colors = STAR_COLORS[type] || STAR_COLORS['杂曜'];

  return (
    <motion.span
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      className={cn(
        'inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-xs font-medium',
        colors.bg,
        colors.border,
        'border',
        colors.text,
        'shadow-sm'
      )}
    >
      <Star className="w-3 h-3" />
      {name}
    </motion.span>
  );
}

function TransformBadge({ type }: { type: string; star: string }) {
  const colors = TRANSFORM_COLORS[type as keyof typeof TRANSFORM_COLORS];
  if (!colors) return null;

  return (
    <motion.span
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      className={cn(
        'inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-xs font-bold',
        colors.bg,
        colors.border,
        'border',
        colors.text
      )}
    >
      {type}
    </motion.span>
  );
}

function PalaceNode({
  palaceName,
  palaceData,
  isExpanded,
  onToggle,
  onClick,
  radius,
  centerX,
  centerY,
}: {
  palaceName: string;
  palaceData: PalaceData;
  isExpanded: boolean;
  onToggle: () => void;
  onClick?: () => void;
  radius: number;
  centerX: number;
  centerY: number;
}) {
  const position = PALACE_POSITIONS[palaceName];
  if (!position) return null;

  const angleRad = (position.angle - 90) * (Math.PI / 180);
  const x = centerX + radius * Math.cos(angleRad);
  const y = centerY + radius * Math.sin(angleRad);

  const allStars = [
    ...palaceData.stars.map(s => ({ name: s.name, type: s.type })),
    ...(palaceData.auxiliary_stars || []).map(name => ({ name, type: '辅曜' as const })),
    ...(palaceData.malefic_stars || []).map(name => ({ name, type: '煞曜' as const })),
  ];

  const transforms = Object.entries(palaceData.transforms);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: position.angle / 360 }}
      className="absolute"
      style={{
        left: `${x}px`,
        top: `${y}px`,
        transform: 'translate(-50%, -50%)',
      }}
    >
      <motion.div
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        className={cn(
          'relative cursor-pointer',
          'bg-slate-900/80 backdrop-blur-sm',
          'border border-slate-700/50',
          'rounded-xl p-3 min-w-[140px]',
          'shadow-lg shadow-black/20',
          'transition-all duration-200'
        )}
        onClick={() => {
          onToggle();
          onClick?.();
        }}
      >
        {/* Palace Header */}
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-semibold text-slate-200">{palaceName}</h3>
          <div className="flex items-center gap-2">
            <span
              className={cn(
                'text-xs font-bold',
                STRENGTH_COLORS[palaceData.strength]
              )}
            >
              {palaceData.strength}
            </span>
            {isExpanded ? (
              <ChevronUp className="w-4 h-4 text-slate-400" />
            ) : (
              <ChevronDown className="w-4 h-4 text-slate-400" />
            )}
          </div>
        </div>

        {/* Location */}
        <div className="text-xs text-slate-500 mb-2">{palaceData.location}</div>

        {/* Stars Preview */}
        <div className="flex flex-wrap gap-1 mb-2">
          {palaceData.stars.slice(0, 2).map((star, idx) => (
            <StarBadge key={`${star.name}-${idx}`} name={star.name} type={star.type} />
          ))}
          {allStars.length > 2 && !isExpanded && (
            <span className="text-xs text-slate-500">+{allStars.length - 2}</span>
          )}
        </div>

        {/* Transforms Preview */}
        {transforms.length > 0 && !isExpanded && (
          <div className="flex flex-wrap gap-1">
            {transforms.slice(0, 2).map(([type, star]) => (
              <TransformBadge key={type} type={type} star={star} />
            ))}
          </div>
        )}

        {/* Expanded Content */}
        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="overflow-hidden"
            >
              <div className="pt-3 border-t border-slate-700/50 mt-2 space-y-3">
                {/* All Stars */}
                <div>
                  <div className="text-xs text-slate-500 mb-1.5">星曜</div>
                  <div className="flex flex-wrap gap-1">
                    {allStars.map((star, idx) => (
                      <StarBadge key={`${star.name}-${idx}`} name={star.name} type={star.type} />
                    ))}
                  </div>
                </div>

                {/* All Transforms */}
                {transforms.length > 0 && (
                  <div>
                    <div className="text-xs text-slate-500 mb-1.5">四化</div>
                    <div className="flex flex-wrap gap-1">
                      {transforms.map(([type, star]) => (
                        <div key={type} className="flex items-center gap-1">
                          <TransformBadge type={type} star={star} />
                          <span className="text-xs text-slate-400">于{star}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Main Star Details */}
                <div>
                  <div className="text-xs text-slate-500 mb-1.5">主星</div>
                  <div className="text-sm text-slate-300">{palaceData.main_star}</div>
                </div>

                {/* Brightness */}
                {palaceData.stars[0]?.brightness && (
                  <div>
                    <div className="text-xs text-slate-500 mb-1.5">亮度</div>
                    <Badge variant="outline" className="text-slate-300">
                      {palaceData.stars[0].brightness}
                    </Badge>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </motion.div>
  );
}

// ============================================================================
// Main Component
// ============================================================================

export function PalaceStarMap({
  palaces,
  chartInfo,
  onPalaceClick,
  className,
}: PalaceStarMapProps) {
  const [expandedPalace, setExpandedPalace] = useState<string | null>(null);

  const togglePalace = (name: string) => {
    setExpandedPalace(prev => prev === name ? null : name);
  };

  // Calculate layout dimensions
  const size = 600;
  const centerX = size / 2;
  const centerY = size / 2;
  const radius = size * 0.38;

  // Get all transforms for legend
  const allTransforms = useMemo(() => {
    const transforms: Record<string, string[]> = {};
    Object.values(palaces).forEach(palace => {
      Object.entries(palace.transforms).forEach(([type, star]) => {
        if (!transforms[type]) transforms[type] = [];
        if (!transforms[type].includes(star)) transforms[type].push(star);
      });
    });
    return transforms;
  }, [palaces]);

  return (
    <div className={cn('relative', className)}>
      {/* Header */}
      {chartInfo && (
        <Card className="mb-4 bg-slate-900/80 border-slate-700/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-amber-400" />
              命盘信息
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-4 text-sm">
              <div>
                <span className="text-slate-500">出生:</span>
                <span className="text-slate-200 ml-2">
                  {chartInfo.year}年{chartInfo.month}月{chartInfo.day}日 {chartInfo.hour}时
                </span>
              </div>
              <div>
                <span className="text-slate-500">天干地支:</span>
                <span className="text-slate-200 ml-2">{chartInfo.gan}{chartInfo.zhi}</span>
              </div>
              <div>
                <span className="text-slate-500">五行:</span>
                <span className="text-slate-200 ml-2">{chartInfo.wuxing}</span>
              </div>
              <div>
                <span className="text-slate-500">性别:</span>
                <span className="text-slate-200 ml-2">{chartInfo.gender}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Star Map Container */}
      <div className="relative mx-auto" style={{ width: size, height: size }}>
        {/* Background Circle */}
        <svg
          className="absolute inset-0"
          width={size}
          height={size}
          viewBox={`0 0 ${size} ${size}`}
        >
          {/* Outer ring */}
          <circle
            cx={centerX}
            cy={centerY}
            r={radius + 60}
            fill="none"
            stroke="rgb(51, 65, 85)"
            strokeWidth="1"
            strokeDasharray="4 4"
            opacity="0.5"
          />
          {/* Main ring */}
          <circle
            cx={centerX}
            cy={centerY}
            r={radius + 20}
            fill="none"
            stroke="rgb(51, 65, 85)"
            strokeWidth="2"
            opacity="0.8"
          />
          {/* Inner ring */}
          <circle
            cx={centerX}
            cy={centerY}
            r={radius - 20}
            fill="none"
            stroke="rgb(51, 65, 85)"
            strokeWidth="1"
            opacity="0.5"
          />
          {/* Center decoration */}
          <circle
            cx={centerX}
            cy={centerY}
            r="40"
            fill="rgb(15, 23, 42)"
            stroke="rgb(51, 65, 85)"
            strokeWidth="2"
          />
          <text
            x={centerX}
            y={centerY - 8}
            textAnchor="middle"
            className="fill-slate-400 text-xs"
          >
            命宫
          </text>
          <text
            x={centerX}
            y={centerY + 8}
            textAnchor="middle"
            className="fill-amber-400 text-sm font-semibold"
          >
            {palaces['命宫']?.main_star || '天机'}
          </text>

          {/* Connection lines */}
          {PALACE_ORDER.map(name => {
            const pos = PALACE_POSITIONS[name];
            if (!pos) return null;
            const angleRad = (pos.angle - 90) * (Math.PI / 180);
            const x1 = centerX + (radius - 15) * Math.cos(angleRad);
            const y1 = centerY + (radius - 15) * Math.sin(angleRad);
            const x2 = centerX + (radius + 25) * Math.cos(angleRad);
            const y2 = centerY + (radius + 25) * Math.sin(angleRad);
            return (
              <line
                key={name}
                x1={x1}
                y1={y1}
                x2={x2}
                y2={y2}
                stroke="rgb(71, 85, 105)"
                strokeWidth="1"
                opacity="0.6"
              />
            );
          })}
        </svg>

        {/* Palace Nodes */}
        {PALACE_ORDER.map(name => {
          const palaceData = palaces[name];
          if (!palaceData) return null;
          return (
            <PalaceNode
              key={name}
              palaceName={name}
              palaceData={palaceData}
              isExpanded={expandedPalace === name}
              onToggle={() => togglePalace(name)}
              onClick={() => onPalaceClick?.(name, palaceData)}
              radius={radius + 40}
              centerX={centerX}
              centerY={centerY}
            />
          );
        })}
      </div>

      {/* Legend */}
      <Card className="mt-4 bg-slate-900/80 border-slate-700/50">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-2">
            <Shield className="w-4 h-4 text-slate-400" />
            图例说明
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-6">
            {/* Star Types */}
            <div className="space-y-2">
              <div className="text-xs text-slate-500 font-medium">星曜类型</div>
              <div className="flex flex-wrap gap-2">
                {Object.entries(STAR_COLORS).map(([type, colors]) => (
                  <div key={type} className="flex items-center gap-1.5">
                    <span
                      className={cn(
                        'w-3 h-3 rounded',
                        colors.bg,
                        colors.border,
                        'border'
                      )}
                    />
                    <span className="text-xs text-slate-400">{type}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Transforms */}
            <div className="space-y-2">
              <div className="text-xs text-slate-500 font-medium">四化标记</div>
              <div className="flex flex-wrap gap-2">
                {Object.entries(TRANSFORM_COLORS).map(([type, colors]) => (
                  <div key={type} className="flex items-center gap-1.5">
                    <span
                      className={cn(
                        'w-3 h-3 rounded',
                        colors.bg,
                        colors.border,
                        'border'
                      )}
                    />
                    <span className="text-xs text-slate-400">{type}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Palace Strength */}
            <div className="space-y-2">
              <div className="text-xs text-slate-500 font-medium">宫位强弱</div>
              <div className="flex flex-wrap gap-2">
                {Object.entries(STRENGTH_COLORS).map(([strength, colorClass]) => (
                  <div key={strength} className="flex items-center gap-1.5">
                    <span className={cn('text-sm font-bold', colorClass)}>{strength}</span>
                    <span className="text-xs text-slate-400">
                      {strength === '强' ? '旺盛' : strength === '中' ? '中等' : '薄弱'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Transforms Summary */}
      {Object.keys(allTransforms).length > 0 && (
        <Card className="mt-4 bg-slate-900/80 border-slate-700/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Zap className="w-4 h-4 text-amber-400" />
              四化汇总
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3">
              {Object.entries(allTransforms).map(([type, stars]) => (
                <div key={type} className="flex items-center gap-2">
                  <Badge
                    variant="outline"
                    className={cn(
                      'font-bold',
                      TRANSFORM_COLORS[type as keyof typeof TRANSFORM_COLORS]?.text
                    )}
                  >
                    {type}
                  </Badge>
                  <span className="text-sm text-slate-400">{stars.join('、')}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

// ============================================================================
// Utility Functions
// ============================================================================

export function extractPalaceStars(palaces: Record<string, PalaceData>) {
  const result: Record<string, { major: string[]; minor: string[]; malefic: string[] }> = {};

  Object.entries(palaces).forEach(([palaceName, palaceData]) => {
    result[palaceName] = {
      major: palaceData.stars.map(s => s.name),
      minor: palaceData.auxiliary_stars || [],
      malefic: palaceData.malefic_stars || [],
    };
  });

  return result;
}

export function getPalaceSummary(palaces: Record<string, PalaceData>) {
  const totalStars = Object.values(palaces).reduce(
    (acc, p) => acc + p.stars.length + (p.auxiliary_stars?.length || 0) + (p.malefic_stars?.length || 0),
    0
  );
  const totalTransforms = Object.values(palaces).reduce(
    (acc, p) => acc + Object.keys(p.transforms).length,
    0
  );

  return {
    totalPalaces: Object.keys(palaces).length,
    totalStars,
    totalTransforms,
    majorPalaces: PALACE_ORDER.filter(name => palaces[name]?.stars.length >= 2),
  };
}

export type { PalaceStarMapProps, PalaceData, StarData };
