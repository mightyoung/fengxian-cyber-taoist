'use client';

import { motion } from 'framer-motion';
import { TimelineEvent } from '@/types/agent';
import { TimelineEventCard } from './timeline-event-card';
import { cn } from '@/lib/utils';

interface SimulationTimelineProps {
  events: TimelineEvent[];
  isRunning: boolean;
  className?: string;
}

export function SimulationTimeline({
  events,
  isRunning,
  className,
}: SimulationTimelineProps) {
  return (
    <div className={cn('relative', className)}>
      {/* Timeline axis */}
      <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gradient-to-b from-amber-400 via-amber-400/50 to-slate-700" />

      {/* Events list */}
      <div className="space-y-4 pl-12">
        {events.map((event, index) => (
          <motion.div
            key={event.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{
              duration: 0.3,
              delay: index * 0.05,
              ease: [0.25, 0.46, 0.45, 0.94],
            }}
          >
            <TimelineEventCard
              event={event}
              isLive={isRunning && index === events.length - 1}
            />
          </motion.div>
        ))}
      </div>

      {/* Live indicator */}
      {isRunning && (
        <div className="absolute left-4 -top-2 w-3 h-3 rounded-full bg-amber-400 animate-pulse shadow-lg shadow-amber-400/50" />
      )}
    </div>
  );
}
