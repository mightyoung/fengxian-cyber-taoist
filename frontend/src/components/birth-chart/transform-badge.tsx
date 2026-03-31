'use client';

import { memo } from 'react';
import { cn } from '@/lib/utils';
import { Transform, TransformType } from '@/types/birth-chart';

interface TransformBadgeProps {
  transform: Transform;
  size?: 'xs' | 'sm' | 'md';
  className?: string;
}

const sizeClasses = {
  xs: 'text-[8px] px-1 py-0',
  sm: 'text-[10px] px-1.5 py-0.5',
  md: 'text-xs px-2 py-1',
};

const transformColors: Record<TransformType, string> = {
  '化禄': '#10B981', // Green - prosperity
  '化权': '#EF4444', // Red - authority
  '化科': '#3B82F6', // Blue - knowledge
  '化忌': '#78716C', // Gray - obstacle
};

const transformDescriptions: Record<TransformType, string> = {
  '化禄': '禄',
  '化权': '权',
  '化科': '科',
  '化忌': '忌',
};

export const TransformBadge = memo(function TransformBadge({
  transform,
  size = 'xs',
  className,
}: TransformBadgeProps) {
  const color = transformColors[transform.type];
  const description = transformDescriptions[transform.type];

  return (
    <span
      className={cn(
        'inline-flex items-center justify-center rounded font-bold',
        'bg-slate-900/80 border',
        'transition-all duration-200',
        sizeClasses[size],
        className
      )}
      style={{
        color,
        borderColor: `${color}50`,
        boxShadow: `0 0 4px ${color}30`,
        minWidth: '16px',
        minHeight: '14px',
      }}
      title={`${transform.type} - ${transform.star}`}
    >
      {description}
    </span>
  );
});

TransformBadge.displayName = 'TransformBadge';
