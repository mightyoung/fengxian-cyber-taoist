'use client';

import { memo, useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading?: boolean;
  placeholder?: string;
  className?: string;
}

function ChatInput({
  onSend,
  isLoading = false,
  placeholder = 'Type your message...',
  className,
}: ChatInputProps) {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    if (message.trim() && !isLoading) {
      onSend(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [message]);

  return (
    <div className={cn('flex items-end gap-2', className)}>
      <div className="flex-1 relative">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={isLoading}
          rows={1}
          className={cn(
            'w-full resize-none rounded-lg border border-slate-700',
            'bg-slate-900 px-4 py-3 text-sm text-slate-100 placeholder:text-slate-500',
            'focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 focus:border-[#D4AF37]',
            'disabled:opacity-50 disabled:cursor-not-allowed',
            'min-h-[44px] max-h-[120px]'
          )}
        />
      </div>

      <Button
        onClick={handleSend}
        disabled={!message.trim() || isLoading}
        size="icon"
        className={cn(
          'h-11 w-11 shrink-0 rounded-lg',
          'bg-[#D4AF37] text-slate-900 hover:bg-[#D4AF37]/90',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          'transition-all duration-200'
        )}
      >
        {isLoading ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <Send className="h-4 w-4" />
        )}
      </Button>
    </div>
  );
}

export const ChatInputMemoized = memo(ChatInput);
ChatInputMemoized.displayName = 'ChatInput';
