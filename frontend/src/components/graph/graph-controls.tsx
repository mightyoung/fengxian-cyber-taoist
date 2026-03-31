'use client';

import { memo, useCallback } from 'react';
import { useReactFlow } from '@xyflow/react';
import {
  ZoomIn,
  ZoomOut,
  Maximize2,
  RotateCcw,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface GraphControlsProps {
  className?: string;
}

function GraphControls({ className }: GraphControlsProps) {
  const { zoomIn, zoomOut, fitView, setCenter } = useReactFlow();

  const handleZoomIn = useCallback(() => {
    zoomIn({ duration: 200 });
  }, [zoomIn]);

  const handleZoomOut = useCallback(() => {
    zoomOut({ duration: 200 });
  }, [zoomOut]);

  const handleFitView = useCallback(() => {
    fitView({ duration: 200, padding: 0.2 });
  }, [fitView]);

  const handleCenter = useCallback(() => {
    setCenter(0, 0, { zoom: 1, duration: 200 });
  }, [setCenter]);

  return (
    <div
      className={cn(
        'flex flex-col gap-2 p-2 bg-[#0F172A]/90 backdrop-blur-sm rounded-lg border border-slate-700',
        className
      )}
    >
      <Button
        variant="ghost"
        size="icon"
        onClick={handleZoomIn}
        className="h-8 w-8 text-slate-300 hover:text-slate-100 hover:bg-slate-800"
        title="Zoom In"
      >
        <ZoomIn className="h-4 w-4" />
      </Button>

      <Button
        variant="ghost"
        size="icon"
        onClick={handleZoomOut}
        className="h-8 w-8 text-slate-300 hover:text-slate-100 hover:bg-slate-800"
        title="Zoom Out"
      >
        <ZoomOut className="h-4 w-4" />
      </Button>

      <div className="h-px bg-slate-700 mx-1" />

      <Button
        variant="ghost"
        size="icon"
        onClick={handleFitView}
        className="h-8 w-8 text-slate-300 hover:text-slate-100 hover:bg-slate-800"
        title="Fit View"
      >
        <Maximize2 className="h-4 w-4" />
      </Button>

      <Button
        variant="ghost"
        size="icon"
        onClick={handleCenter}
        className="h-8 w-8 text-slate-300 hover:text-slate-100 hover:bg-slate-800"
        title="Reset View"
      >
        <RotateCcw className="h-4 w-4" />
      </Button>
    </div>
  );
}

export const GraphControlsMemoized = memo(GraphControls);
GraphControlsMemoized.displayName = 'GraphControls';
