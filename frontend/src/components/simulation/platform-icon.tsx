'use client';

import { Twitter, MessageCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Platform } from '@/types/agent';

interface PlatformIconProps {
  platform: Platform;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

const sizeClasses = {
  sm: 'h-3 w-3',
  md: 'h-4 w-4',
  lg: 'h-5 w-5',
};

const platformStyles = {
  twitter: {
    bg: 'bg-sky-500/20',
    text: 'text-sky-400',
    icon: Twitter,
  },
  reddit: {
    bg: 'bg-orange-500/20',
    text: 'text-orange-400',
    icon: MessageCircle,
  },
};

export function PlatformIcon({ platform, className, size = 'md' }: PlatformIconProps) {
  const style = platformStyles[platform];
  const Icon = style.icon;

  return (
    <div
      className={cn(
        'flex items-center justify-center rounded-md',
        style.bg,
        style.text,
        sizeClasses[size],
        className
      )}
    >
      <Icon className={sizeClasses[size]} />
    </div>
  );
}
