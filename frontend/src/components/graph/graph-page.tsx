'use client';

import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { KnowledgeGraph } from '@/components/graph';
import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Info, Building2, User, MapPin, Calendar, Lightbulb } from 'lucide-react';
import { useGraphData } from '@/hooks/use-graph';
import { cn } from '@/lib/utils';
import { ANIMATIONS } from '@/lib/animation';

interface GraphPageProps {
  graphId: string;
  className?: string;
}

const NODE_TYPE_ICONS: Record<string, React.ElementType> = {
  person: User,
  organization: Building2,
  location: MapPin,
  event: Calendar,
  concept: Lightbulb,
};

const NODE_TYPE_COLORS: Record<string, string> = {
  person: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  organization: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  location: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  event: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  concept: 'bg-pink-500/20 text-pink-400 border-pink-500/30',
};

export default function GraphPage({ graphId, className }: GraphPageProps) {
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const { data: graphData } = useGraphData(graphId);

  const selectedNode = graphData?.nodes.find((n) => n.id === selectedNodeId);

  const handleNodeClick = useCallback((nodeId: string) => {
    setSelectedNodeId(nodeId);
    setIsSidebarOpen(true);
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: ANIMATIONS.standard.duration / 1000 }}
      className={cn('w-full h-full flex', className)}
    >
      {/* Main Graph Area */}
      <div className="flex-1 h-full">
        <KnowledgeGraph
          graphId={graphId}
          onNodeClick={handleNodeClick}
          className="w-full h-full"
        />
      </div>

      {/* Sidebar */}
      <Sheet open={isSidebarOpen} onOpenChange={setIsSidebarOpen}>
        <SheetContent className="w-[400px] bg-slate-950 border-slate-800 p-0">
          <SheetHeader className="p-4 border-b border-slate-800">
            <SheetTitle className="text-slate-100 flex items-center gap-2">
              <Info className="h-4 w-4 text-[#D4AF37]" />
              Node Details
            </SheetTitle>
          </SheetHeader>

          <ScrollArea className="h-[calc(100vh-65px)]">
            {selectedNode ? (
              <div className="p-4 space-y-6">
                {/* Node Header */}
                <div className="space-y-2">
                  <div className="flex items-center gap-3">
                    {(() => {
                      const Icon = NODE_TYPE_ICONS[selectedNode.type] || Info;
                      return (
                        <div
                          className={cn(
                            'p-2 rounded-lg border',
                            NODE_TYPE_COLORS[selectedNode.type] || 'bg-slate-800 text-slate-400 border-slate-700'
                          )}
                        >
                          <Icon className="h-5 w-5" />
                        </div>
                      );
                    })()}
                    <div>
                      <h2 className="text-lg font-semibold text-slate-100">
                        {selectedNode.label}
                      </h2>
                      <Badge
                        variant="outline"
                        className={cn(
                          'mt-1',
                          NODE_TYPE_COLORS[selectedNode.type] || 'border-slate-700 text-slate-400'
                        )}
                      >
                        {selectedNode.type}
                      </Badge>
                    </div>
                  </div>
                </div>

                {/* Description */}
                {selectedNode.description && (
                  <div className="space-y-2">
                    <h3 className="text-sm font-medium text-slate-400">Description</h3>
                    <p className="text-sm text-slate-300 leading-relaxed">
                      {selectedNode.description}
                    </p>
                  </div>
                )}

                {/* Properties */}
                {selectedNode.properties && Object.keys(selectedNode.properties).length > 0 && (
                  <div className="space-y-2">
                    <h3 className="text-sm font-medium text-slate-400">Properties</h3>
                    <div className="space-y-2">
                      {Object.entries(selectedNode.properties).map(([key, value]) => (
                        <div
                          key={key}
                          className="flex justify-between items-center py-2 px-3 bg-slate-900/50 rounded-lg"
                        >
                          <span className="text-sm text-slate-400">{key}</span>
                          <span className="text-sm text-slate-200">
                            {typeof value === 'object'
                              ? JSON.stringify(value)
                              : String(value)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Related Nodes */}
                {graphData && (
                  <div className="space-y-2">
                    <h3 className="text-sm font-medium text-slate-400">Connections</h3>
                    <div className="space-y-1">
                      {graphData.edges
                        .filter(
                          (e) => e.source === selectedNode.id || e.target === selectedNode.id
                        )
                        .map((edge) => {
                          const isSource = edge.source === selectedNode.id;
                          const connectedNodeId = isSource ? edge.target : edge.source;
                          const connectedNode = graphData.nodes.find(
                            (n) => n.id === connectedNodeId
                          );

                          return (
                            <button
                              key={edge.id}
                              onClick={() => handleNodeClick(connectedNodeId)}
                              className="w-full flex items-center justify-between p-3 bg-slate-900/50 hover:bg-slate-800 rounded-lg transition-colors"
                            >
                              <div className="flex items-center gap-2">
                                {isSource ? (
                                  <span className="text-xs text-slate-500">→</span>
                                ) : (
                                  <span className="text-xs text-slate-500">←</span>
                                )}
                                <span className="text-sm text-slate-200">
                                  {connectedNode?.label || connectedNodeId}
                                </span>
                              </div>
                              <span className="text-xs text-slate-500">{edge.label}</span>
                            </button>
                          );
                        })}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="p-8 text-center">
                <Info className="h-12 w-12 text-slate-600 mx-auto mb-4" />
                <p className="text-slate-400">Select a node to view details</p>
              </div>
            )}
          </ScrollArea>
        </SheetContent>
      </Sheet>
    </motion.div>
  );
}
