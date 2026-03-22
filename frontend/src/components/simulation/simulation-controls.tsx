'use client';

import { Play, Pause, Square, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { SimulationStatus } from '@/types/simulation';

interface SimulationControlsProps {
  status: SimulationStatus;
  onStart: () => void;
  onPause: () => void;
  onStop: () => void;
  isLoading?: boolean;
  className?: string;
}

export function SimulationControls({
  status,
  onStart,
  onPause,
  onStop,
  isLoading = false,
  className,
}: SimulationControlsProps) {
  const isRunning = status === SimulationStatus.RUNNING;
  const isPaused = status === SimulationStatus.PAUSED;
  const isPending = status === SimulationStatus.PENDING;
  const isCompleted = status === SimulationStatus.COMPLETED;
  const isFailed = status === SimulationStatus.FAILED;

  const canStart = isPending || isPaused || isFailed || isCompleted;
  const canPause = isRunning;
  const canStop = isRunning || isPaused;

  return (
    <div className={cn('flex items-center gap-2', className)}>
      {canStart && (
        <Button
          onClick={onStart}
          disabled={isLoading}
          className="gap-2 bg-emerald-600 hover:bg-emerald-700"
        >
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Play className="h-4 w-4" />
          )}
          开始
        </Button>
      )}

      {canPause && (
        <Button
          onClick={onPause}
          disabled={isLoading}
          className="gap-2 bg-amber-600 hover:bg-amber-700"
        >
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Pause className="h-4 w-4" />
          )}
          暂停
        </Button>
      )}

      {canStop && (
        <Button
          onClick={onStop}
          disabled={isLoading}
          variant="destructive"
          className="gap-2"
        >
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Square className="h-4 w-4" />
          )}
          停止
        </Button>
      )}
    </div>
  );
}
