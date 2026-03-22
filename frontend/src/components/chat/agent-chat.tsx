'use client';

import { memo, useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageCircle, X, Users, Bot } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { ChatInputMemoized } from './chat-input';
import { ChatMessageMemoized, type ChatMessage } from './chat-message';
import { cn } from '@/lib/utils';
import { ANIMATIONS } from '@/lib/animation';

interface AgentChatProps {
  messages: ChatMessage[];
  onSendMessage: (message: string) => void;
  isLoading?: boolean;
  agents?: { id: string; name: string }[];
  selectedAgentId?: string;
  onAgentSelect?: (agentId: string) => void;
  className?: string;
}

function AgentChat({
  messages,
  onSendMessage,
  isLoading = false,
  agents = [],
  selectedAgentId,
  onAgentSelect,
  className,
}: AgentChatProps) {
  const [isOpen, setIsOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <>
      {/* Toggle Button */}
      <Button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-lg',
          'bg-[#D4AF37] hover:bg-[#D4AF37]/90 text-slate-900',
          'transition-all duration-300 z-50',
          isOpen && 'rotate-90'
        )}
      >
        {isOpen ? (
          <X className="h-6 w-6" />
        ) : (
          <MessageCircle className="h-6 w-6" />
        )}
      </Button>

      {/* Chat Panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ duration: ANIMATIONS.standard.duration / 1000 }}
            className={cn(
              'fixed bottom-24 right-6 w-[380px] h-[500px] rounded-xl',
              'bg-slate-950 border border-slate-800 shadow-2xl',
              'flex flex-col overflow-hidden z-50',
              className
            )}
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-slate-800">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-[#D4AF37]/10 rounded-lg">
                  <Bot className="h-5 w-5 text-[#D4AF37]" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-slate-100">Agent Chat</h3>
                  <p className="text-xs text-slate-500">
                    {messages.length} messages
                  </p>
                </div>
              </div>
            </div>

            {/* Agent Selector */}
            {agents.length > 0 && (
              <div className="px-4 py-2 border-b border-slate-800">
                <div className="flex items-center gap-2 mb-2">
                  <Users className="h-3 w-3 text-slate-500" />
                  <span className="text-xs text-slate-500">Select Agent</span>
                </div>
                <div className="flex gap-1 flex-wrap">
                  {agents.map((agent) => (
                    <button
                      key={agent.id}
                      onClick={() => onAgentSelect?.(agent.id)}
                      className={cn(
                        'px-2 py-1 rounded-full text-xs transition-colors',
                        selectedAgentId === agent.id
                          ? 'bg-[#D4AF37] text-slate-900'
                          : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                      )}
                    >
                      {agent.name}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Messages */}
            <ScrollArea className="flex-1 p-4">
              <div className="space-y-4">
                {messages.length === 0 ? (
                  <div className="text-center py-8">
                    <Bot className="h-12 w-12 text-slate-700 mx-auto mb-4" />
                    <p className="text-slate-400 text-sm">
                      Start a conversation with the simulation agents
                    </p>
                  </div>
                ) : (
                  messages.map((message, index) => (
                    <ChatMessageMemoized
                      key={message.id}
                      message={message}
                      isLoading={isLoading && index === messages.length - 1}
                    />
                  ))
                )}
                <div ref={messagesEndRef} />
              </div>
            </ScrollArea>

            {/* Input */}
            <div className="p-4 border-t border-slate-800">
              <ChatInputMemoized
                onSend={onSendMessage}
                isLoading={isLoading}
                placeholder="Ask the agents..."
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

export const AgentChatMemoized = memo(AgentChat);
AgentChatMemoized.displayName = 'AgentChat';
