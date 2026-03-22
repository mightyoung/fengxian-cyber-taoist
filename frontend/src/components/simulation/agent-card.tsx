'use client';

import { memo } from 'react';
import { motion } from 'framer-motion';
import { Agent, AgentStatus } from '@/types/agent';
import { cn } from '@/lib/utils';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';

interface AgentCardProps {
  agent: Agent;
  onSelect?: (agent: Agent) => void;
  isSelected?: boolean;
}

const STATUS_CONFIG: Record<AgentStatus, { label: string; color: string }> = {
  [AgentStatus.IDLE]: { label: '空闲', color: 'bg-slate-500' },
  [AgentStatus.RUNNING]: { label: '运行中', color: 'bg-amber-500 animate-pulse' },
  [AgentStatus.COMPLETED]: { label: '已完成', color: 'bg-emerald-500' },
  [AgentStatus.FAILED]: { label: '失败', color: 'bg-red-500' },
};

export const AgentCard = memo(function AgentCard({ agent, onSelect, isSelected }: AgentCardProps) {
  const statusConfig = STATUS_CONFIG[agent.status];

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={() => onSelect?.(agent)}
    >
      <Card
        className={cn(
          'bg-slate-800/50 border-slate-700/50 cursor-pointer',
          'transition-all duration-200',
          isSelected && 'ring-2 ring-amber-400 bg-slate-800/80',
          'hover:bg-slate-800/70 hover:border-slate-600/50'
        )}
      >
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Avatar className="h-10 w-10 border-2 border-slate-600">
                <AvatarImage src={agent.avatar} />
                <AvatarFallback className="bg-slate-700 text-slate-200">
                  {agent.name.slice(0, 2)}
                </AvatarFallback>
              </Avatar>
              <div>
                <CardTitle className="text-sm text-slate-100">
                  {agent.name}
                </CardTitle>
                <CardDescription className="text-xs text-slate-400">
                  {agent.role}
                </CardDescription>
              </div>
            </div>
            <Badge
              variant="secondary"
              className={cn('text-white border-0', statusConfig.color)}
            >
              {statusConfig.label}
            </Badge>
          </div>
        </CardHeader>

        <CardContent className="space-y-3">
          {/* Activity indicator */}
          <div className="space-y-1">
            <div className="flex justify-between text-xs text-slate-400">
              <span>活跃度</span>
              <span>{agent.activity}%</span>
            </div>
            <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-amber-400 to-amber-500/50"
                initial={{ width: 0 }}
                animate={{ width: `${agent.activity}%` }}
                transition={{ duration: 0.8, ease: 'easeOut' }}
              />
            </div>
          </div>

          {/* Statistics */}
          <div className="grid grid-cols-3 gap-2 text-center">
            <div className="bg-slate-900/50 rounded px-2 py-1">
              <div className="text-lg font-mono text-amber-400">{agent.tweets}</div>
              <div className="text-[10px] text-slate-500">推文</div>
            </div>
            <div className="bg-slate-900/50 rounded px-2 py-1">
              <div className="text-lg font-mono text-blue-400">{agent.mentions}</div>
              <div className="text-[10px] text-slate-500">提及</div>
            </div>
            <div className="bg-slate-900/50 rounded px-2 py-1">
              <div className="text-lg font-mono text-emerald-400">{agent.engagements}</div>
              <div className="text-[10px] text-slate-500">互动</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
});

AgentCard.displayName = 'AgentCard';
