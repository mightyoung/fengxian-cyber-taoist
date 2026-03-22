'use client';

import { memo, useCallback } from 'react';
import { cn } from '@/lib/utils';
import { Palace } from '@/types/birth-chart';
import { StarBadge } from './star-badge';
import { TransformBadge } from './transform-badge';

interface PalaceCellProps {
  palace: Palace;
  isActive?: boolean;
  onClick?: (palace: Palace) => void;
  showStars?: boolean;
  showTransforms?: boolean;
  className?: string;
}

export const PalaceCell = memo(function PalaceCell({
  palace,
  isActive = false,
  onClick,
  showStars = true,
  showTransforms = true,
  className,
}: PalaceCellProps) {
  const handleClick = useCallback(() => {
    onClick?.(palace);
  }, [onClick, palace]);

  return (
    <div
      onClick={handleClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && handleClick()}
      className={cn(
        'relative bg-slate-800/50 border border-slate-700/50 rounded-lg p-2',
        'cursor-pointer transition-all duration-200',
        'hover:bg-slate-800/70 hover:border-slate-600/50',
        'focus:outline-none focus:ring-2 focus:ring-accent/50',
        isActive && 'ring-2 ring-accent bg-slate-800/80 border-accent/50',
        className
      )}
    >
      {/* 宫位名称 */}
      <div className="text-xs text-slate-400 font-heading mb-1 truncate">
        {palace.name}
      </div>

      {/* 天干 */}
      <div className="text-xs text-slate-500 font-mono mb-1">
        {palace.tiangan}
      </div>

      {/* 星曜列表 */}
      {showStars && palace.stars.length > 0 && (
        <div className="space-y-0.5">
          {palace.stars.slice(0, 3).map((star) => (
            <StarBadge key={star.name} star={star} size="sm" />
          ))}
          {palace.stars.length > 3 && (
            <span className="text-[10px] text-slate-500">
              +{palace.stars.length - 3}
            </span>
          )}
        </div>
      )}

      {/* 四化曜 */}
      {showTransforms && palace.transforms && palace.transforms.length > 0 && (
        <div className="absolute top-1 right-1 flex gap-0.5">
          {palace.transforms.map((t) => (
            <TransformBadge key={t.type} transform={t} size="xs" />
          ))}
        </div>
      )}

      {/* 大限/流年 indicator */}
      {(palace.daxian || palace.liunian) && (
        <div className="absolute bottom-1 right-1 flex gap-1">
          {palace.daxian && (
            <span className="text-[8px] px-1 rounded bg-accent/20 text-accent">
              大
            </span>
          )}
          {palace.liunian && (
            <span className="text-[8px] px-1 rounded bg-blue-500/20 text-blue-400">
              流
            </span>
          )}
        </div>
      )}
    </div>
  );
});

PalaceCell.displayName = 'PalaceCell';
