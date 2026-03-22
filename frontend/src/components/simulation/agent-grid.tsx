'use client';

import { memo } from 'react';
import { Agent } from '@/types/agent';
import { AgentCard } from './agent-card';
import { cn } from '@/lib/utils';

interface AgentGridProps {
  agents: Agent[];
  selectedAgentId?: string;
  onSelectAgent?: (agent: Agent) => void;
  className?: string;
}

export const AgentGrid = memo(function AgentGrid({
  agents,
  selectedAgentId,
  onSelectAgent,
  className,
}: AgentGridProps) {
  return (
    <div
      className={cn(
        'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4',
        className
      )}
    >
      {agents.map((agent) => (
        <AgentCard
          key={agent.id}
          agent={agent}
          isSelected={agent.id === selectedAgentId}
          onSelect={onSelectAgent}
        />
      ))}
    </div>
  );
});
