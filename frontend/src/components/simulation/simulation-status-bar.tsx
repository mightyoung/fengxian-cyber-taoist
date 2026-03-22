'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { SimulationStatus } from '@/types/simulation';

interface SimulationStatusBarProps {
  progress: number;
  status: SimulationStatus;
  currentRound: number;
  totalRounds: number;
  className?: string;
}

const statusLabels: Record<SimulationStatus, string> = {
  [SimulationStatus.CREATED]: '已创建',
  [SimulationStatus.PREPARING]: '准备中',
  [SimulationStatus.READY]: '就绪',
  [SimulationStatus.RUNNING]: '运行中',
  [SimulationStatus.COMPLETED]: '已完成',
  [SimulationStatus.FAILED]: '失败',
  [SimulationStatus.PAUSED]: '已暂停',
};

const statusColors: Record<SimulationStatus, string> = {
  [SimulationStatus.CREATED]: 'bg-slate-500',
  [SimulationStatus.PREPARING]: 'bg-blue-500',
  [SimulationStatus.READY]: 'bg-green-500',
  [SimulationStatus.RUNNING]: 'bg-amber-500',
  [SimulationStatus.COMPLETED]: 'bg-emerald-500',
  [SimulationStatus.FAILED]: 'bg-red-500',
  [SimulationStatus.PAUSED]: 'bg-blue-500',
};

export function SimulationStatusBar({
  progress,
  status,
  currentRound,
  totalRounds,
  className,
}: SimulationStatusBarProps) {
  return (
    <div className={cn('space-y-2', className)}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span
            className={cn(
              'h-2 w-2 rounded-full',
              statusColors[status],
              status === SimulationStatus.RUNNING && 'animate-pulse'
            )}
          />
          <span className="text-sm font-medium text-slate-200">
            {statusLabels[status]}
          </span>
        </div>
        <span className="text-lg font-mono text-amber-400">{progress}%</span>
      </div>

      <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
        <motion.div
          className={cn('h-full', statusColors[status])}
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
        />
      </div>

      <div className="flex justify-between text-xs text-slate-400">
        <span>第 {currentRound} 轮</span>
        <span>共 {totalRounds} 轮</span>
      </div>
    </div>
  );
}
