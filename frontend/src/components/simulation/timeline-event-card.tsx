'use client';

import { memo } from 'react';
import { TimelineEvent } from '@/types/agent';
import { PlatformIcon } from './platform-icon';
import { cn } from '@/lib/utils';

interface TimelineEventCardProps {
  event: TimelineEvent;
  isLive?: boolean;
}

function TimelineEventCardComponent({ event, isLive }: TimelineEventCardProps) {
  return (
    <div
      className={cn(
        'relative bg-slate-800/80 border border-slate-700/50 rounded-lg p-4',
        'transition-all duration-200',
        isLive && 'ring-2 ring-amber-400/50 bg-slate-800'
      )}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <PlatformIcon platform={event.platform} size="sm" />
          <span className="text-xs text-slate-400 font-mono">
            {event.timestamp.toLocaleTimeString()}
          </span>
        </div>
        {isLive && (
          <span className="text-[10px] text-amber-400 font-medium animate-pulse">
            LIVE
          </span>
        )}
      </div>

      <p className="text-sm text-slate-200">{event.content || event.action}</p>
    </div>
  );
}

export const TimelineEventCard = memo(TimelineEventCardComponent);
TimelineEventCard.displayName = 'TimelineEventCard';
