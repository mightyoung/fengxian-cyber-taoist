'use client';

import { memo } from 'react';
import { cn } from '@/lib/utils';
import { COLORS } from '@/lib/colors';
import { Star, Wuxing } from '@/types/birth-chart';

interface StarBadgeProps {
  star: Star;
  size?: 'xs' | 'sm' | 'md' | 'lg';
  showGlow?: boolean;
  className?: string;
}

const sizeClasses = {
  xs: 'text-[8px] px-1 py-0',
  sm: 'text-[10px] px-1.5 py-0.5',
  md: 'text-xs px-2 py-1',
  lg: 'text-sm px-2.5 py-1',
};

function getStarColor(starName: string): string {
  return COLORS.stars[starName as keyof typeof COLORS.stars] || COLORS.accent.DEFAULT;
}

function getWuxingColor(wuxing: Wuxing): string {
  return COLORS.wuxing[wuxing] || COLORS.accent.DEFAULT;
}

export const StarBadge = memo(function StarBadge({
  star,
  size = 'sm',
  showGlow = false,
  className,
}: StarBadgeProps) {
  const starColor = getStarColor(star.name);
  const wuxingColor = getWuxingColor(star.wuxing);

  return (
    <span
      className={cn(
        'inline-flex items-center gap-0.5 rounded font-medium',
        'bg-slate-900/80 border border-slate-700/50',
        'transition-all duration-200',
        showGlow && 'animate-pulse',
        sizeClasses[size],
        className
      )}
      style={{
        color: starColor,
        borderColor: `${starColor}30`,
        boxShadow: showGlow ? `0 0 8px ${starColor}40` : undefined,
      }}
      title={`${star.name} (${star.wuxing})`}
    >
      {star.name}
      {star.level === 'major' && (
        <span className="text-[6px] opacity-60" aria-hidden="true">★</span>
      )}
      <span
        className="w-2 h-2 rounded-full ml-0.5"
        style={{ backgroundColor: wuxingColor }}
        title={star.wuxing}
      />
    </span>
  );
});

StarBadge.displayName = 'StarBadge';
