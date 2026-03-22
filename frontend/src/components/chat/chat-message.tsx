'use client';

import { memo } from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { ANIMATIONS } from '@/lib/animation';
import ReactMarkdown from 'react-markdown';

export type MessageRole = 'user' | 'assistant' | 'system';

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp?: Date;
  agentName?: string;
}

interface ChatMessageProps {
  message: ChatMessage;
  isLoading?: boolean;
}

const ROLE_STYLES: Record<MessageRole, { container: string; bubble: string; icon: string }> = {
  user: {
    container: 'justify-end',
    bubble: 'bg-[#D4AF37] text-slate-900',
    icon: '',
  },
  assistant: {
    container: 'justify-start',
    bubble: 'bg-slate-800 text-slate-100 border border-slate-700',
    icon: '',
  },
  system: {
    container: 'justify-center',
    bubble: 'bg-transparent text-slate-500 text-xs italic border-none',
    icon: '',
  },
};

function ChatMessageComponent({ message, isLoading }: ChatMessageProps) {
  const styles = ROLE_STYLES[message.role];
  const isSystem = message.role === 'system';

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: ANIMATIONS.micro.duration / 1000 }}
      className={cn('flex w-full', styles.container)}
    >
      <div
        className={cn(
          'max-w-[80%] px-4 py-2.5 rounded-2xl',
          styles.bubble,
          isSystem ? 'text-center' : 'rounded-br-sm'
        )}
      >
        {message.agentName && message.role === 'assistant' && (
          <div className="flex items-center gap-2 mb-1">
            <div className="w-5 h-5 rounded-full bg-[#D4AF37]/20 flex items-center justify-center">
              <span className="text-[10px] font-medium text-[#D4AF37]">
                {message.agentName.charAt(0)}
              </span>
            </div>
            <span className="text-xs font-medium text-slate-400">{message.agentName}</span>
          </div>
        )}

        <div className={cn('text-sm', isSystem ? 'text-center' : '')}>
          {isLoading ? (
            <div className="flex items-center gap-1">
              <span className="text-slate-500">Thinking</span>
              <span className="animate-pulse">...</span>
            </div>
          ) : isSystem ? (
            <span className="text-slate-500">{message.content}</span>
          ) : (
            <ReactMarkdown
              components={{
                p: ({ children }) => <p className="leading-relaxed">{children}</p>,
                a: ({ href, children }) => {
                  // Prevent XSS by only allowing safe protocols
                  const isSafe = href && (
                    href.startsWith('http://') ||
                    href.startsWith('https://') ||
                    href.startsWith('/') ||
                    href.startsWith('#')
                  );
                  if (!isSafe) return <span className="text-red-400">[链接]</span>;
                  return (
                    <a
                      href={href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-400 hover:underline"
                    >
                      {children}
                    </a>
                  );
                },
                code: ({ children, className }) => (
                  <code className={cn('bg-slate-950 px-1.5 py-0.5 rounded text-xs', className)}>
                    {children}
                  </code>
                ),
                pre: ({ children }) => (
                  <pre className="bg-slate-950 p-3 rounded-lg overflow-x-auto my-2">
                    {children}
                  </pre>
                ),
              }}
            >
              {message.content}
            </ReactMarkdown>
          )}
        </div>

        {message.timestamp && !isSystem && (
          <div className="mt-1 text-[10px] text-slate-500 text-right">
            {message.timestamp.toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </div>
        )}
      </div>
    </motion.div>
  );
}

export const ChatMessageMemoized = memo(ChatMessageComponent);
ChatMessageMemoized.displayName = 'ChatMessage';
