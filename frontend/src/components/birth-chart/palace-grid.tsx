'use client';

import { memo, useCallback } from 'react';
import { Palace } from '@/types/birth-chart';
import { PalaceCell } from './palace-cell';

interface PalaceGridProps {
  palaces: Palace[];
  onPalaceClick?: (palace: Palace) => void;
  activePalaceId?: string;
  showStars?: boolean;
  showTransforms?: boolean;
  className?: string;
}

/**
 * PalaceGrid - 3x4 grid layout for 12 palace birth chart
 *
 * Layout (viewed from top):
 * | 1  | 2  | 3  | 4  |
 * | 12 |         | 5  |
 * | 11 |         | 6  |
 * | 10 | 9  | 8  | 7  |
 *
 * In our data, palaces are ordered: 命宫, 父母宫, 兄弟宫, 夫妻宫, 子女宫,
 * 财帛宫, 疾厄宫, 迁移宫, 仆役宫, 官禄宫, 田宅宫, 福德宫
 *
 * The standard display order for the grid is:
 * Row 1: 命宫, 父母宫, 兄弟宫, 夫妻宫
 * Row 2: 田宅宫, 官禄宫, 仆役宫, 子女宫
 * Row 3: 福德宫, 疾厄宫, 迁移宫, 财帛宫
 */

// Reorder palaces for standard display (clockwise from top-left)
function getDisplayOrder(palaces: Palace[]): Palace[] {
  const order = [
    '命宫', '父母宫', '兄弟宫', '夫妻宫',
    '田宅宫', '官禄宫', '仆役宫', '子女宫',
    '福德宫', '疾厄宫', '迁移宫', '财帛宫',
  ];

  const palaceMap = new Map(palaces.map(p => [p.name, p]));
  return order
    .map(name => palaceMap.get(name))
    .filter((p): p is Palace => p !== undefined);
}

export const PalaceGrid = memo(function PalaceGrid({
  palaces,
  onPalaceClick,
  activePalaceId,
  showStars = true,
  showTransforms = true,
  className,
}: PalaceGridProps) {
  const handlePalaceClick = useCallback((palace: Palace) => {
    onPalaceClick?.(palace);
  }, [onPalaceClick]);

  const displayPalaces = getDisplayOrder(palaces);

  return (
    <div
      className={`relative ${className || ''}`}
    >
      {/* 3x4 grid layout */}
      <div className="grid grid-cols-4 gap-1 w-full aspect-square max-w-2xl mx-auto">
        {displayPalaces.map((palace) => (
          <PalaceCell
            key={palace.id}
            palace={palace}
            isActive={palace.id === activePalaceId}
            onClick={handlePalaceClick}
            showStars={showStars}
            showTransforms={showTransforms}
            className="h-full min-h-[80px]"
          />
        ))}
      </div>

      {/* Center decoration */}
      <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none">
        <div className="w-16 h-16 rounded-full border-2 border-accent/30 flex items-center justify-center">
          <span className="text-accent/50 text-xs font-heading">中</span>
        </div>
      </div>
    </div>
  );
});

PalaceGrid.displayName = 'PalaceGrid';
