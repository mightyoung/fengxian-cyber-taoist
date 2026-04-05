'use client';

import { useQuery, useMutation } from '@tanstack/react-query';
import { divinationApi, reportApi } from '@/hooks/use-api';
import { Card, CardContent } from '@/components/ui/card';
import { Sparkles, Zap, ShieldAlert, Info, Download, Share2 } from 'lucide-react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useState } from 'react';
import type { VibePoster } from '@/types/api';

interface RealtimeVibeProps {
  chartId: string;
  className?: string;
}

export function RealtimeVibe({ chartId, className }: RealtimeVibeProps) {
  const { data, isLoading } = useQuery({
    queryKey: ['vibe', chartId],
    queryFn: () => divinationApi.getVibe(chartId),
    refetchInterval: 60000, // 1 minute
    enabled: !!chartId && chartId !== 'demo',
  });

  const [previewOpen, setPreviewOpen] = useState(false);
  const [posterData, setPosterData] = useState<(VibePoster & { svg?: string }) | null>(null);

  const posterMutation = useMutation({
    mutationFn: () => reportApi.getPoster(chartId),
    onSuccess: (res) => {
      if (res.success) {
        setPosterData(res.data);
        setPreviewOpen(true);
        toast.success('赛博灵符已显影');
      }
    }
  });

  if (chartId === 'demo') {
    return (
      <Card className="bg-slate-900/40 border-slate-800 border-dashed backdrop-blur-sm overflow-hidden">
        <CardContent className="p-6 text-center">
          <Sparkles className="h-8 w-8 text-slate-700 mx-auto mb-2" />
          <p className="text-sm text-slate-500 font-heading">起卦后即可开启实时气场监控</p>
        </CardContent>
      </Card>
    );
  }

  if (isLoading || !data?.success) {
    return (
      <div className="h-32 flex items-center justify-center border border-dashed rounded-xl border-slate-700">
        <div className="flex items-center gap-2 text-slate-500 animate-pulse">
          <Sparkles className="h-4 w-4" />
          <span className="text-sm">感应此时气场...</span>
        </div>
      </div>
    );
  }

  const vibe = data.data;
  const scoreColor = vibe.vibe_score > 70 ? 'text-emerald-400' : vibe.vibe_score < 40 ? 'text-rose-400' : 'text-amber-400';

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className={className}
    >
      <Card className="bg-slate-900/80 border-accent/20 backdrop-blur-sm overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-accent/50 to-transparent" />
        <CardContent className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-lg font-heading text-slate-100 flex items-center gap-2">
                <Zap className="h-4 w-4 text-accent" />
                实时赛博气象
              </h3>
              <p className="text-xs text-slate-500">{new Date(vibe.timestamp).toLocaleTimeString()} 气机更新</p>
            </div>
            <div className={`text-2xl font-bold font-mono ${scoreColor}`}>
              {Math.round(vibe.vibe_score * 100)}
            </div>
          </div>

          <div className="space-y-4">
            {/* Vibe description */}
            <div className="flex gap-2 text-sm text-slate-300">
              <Info className="h-4 w-4 text-accent/60 shrink-0 mt-0.5" />
              <p>{vibe.advice}</p>
            </div>

            {/* Instant Transforms */}
            <div className="flex flex-wrap gap-2">
              {vibe.instant_transforms.map((t: string, i: number) => (
                <span 
                  key={i} 
                  className="px-2 py-0.5 rounded bg-accent/10 border border-accent/20 text-[10px] text-accent font-medium"
                >
                  {t}
                </span>
              ))}
            </div>

            {/* Actions */}
            <div className="flex gap-2 pt-2">
              <Button 
                variant="outline" 
                size="sm" 
                className="flex-1 text-[10px] h-8 border-accent/20 hover:bg-accent/10"
                onClick={() => posterMutation.mutate()}
                disabled={posterMutation.isPending}
              >
                <Download className="h-3 w-3 mr-1" />
                生成灵符
              </Button>
              <Button variant="outline" size="sm" className="px-2 h-8 border-accent/20 hover:bg-accent/10">
                <Share2 className="h-3 w-3" />
              </Button>
            </div>

            {/* Warning if any */}
            {vibe.vibe_score < 0.4 && (
              <div className="p-2 rounded bg-rose-500/10 border border-rose-500/20 flex items-center gap-2 text-[11px] text-rose-400">
                <ShieldAlert className="h-3 w-3" />
                当前时段能量波动剧烈，建议持守本心。
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <Dialog open={previewOpen} onOpenChange={setPreviewOpen}>
        <DialogContent className="sm:max-w-[425px] bg-slate-950 border-accent/20">
          <DialogHeader>
            <DialogTitle className="text-accent font-heading">赛博灵符预览</DialogTitle>
          </DialogHeader>
          <div className="flex flex-col items-center justify-center p-4">
            {posterData?.svg && (
              <div 
                className="w-full aspect-[2/3] rounded-lg overflow-hidden shadow-2xl border border-accent/10"
                dangerouslySetInnerHTML={{ __html: posterData.svg }}
              />
            )}
            <div className="mt-6 flex gap-4 w-full">
              <Button className="flex-1 bg-accent text-slate-950 hover:bg-accent/90">
                <Download className="h-4 w-4 mr-2" />
                下载法相
              </Button>
              <Button variant="outline" className="flex-1 border-accent/20 text-accent">
                <Share2 className="h-4 w-4 mr-2" />
                转发因果
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </motion.div>
  );
}
