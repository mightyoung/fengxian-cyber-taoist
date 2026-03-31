'use client';

import { useState, useCallback, useRef } from 'react';
import { ChatMessage } from '@/components/chat/chat-message';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { MessageCircle, Bot, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

// Demo agents
const demoAgents = [
  { id: '1', name: '张三', role: '科技博主' },
  { id: '2', name: '李四', role: '产品经理' },
  { id: '3', name: '王五', role: '投资分析师' },
];

export default function ChatRoutePage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedAgentId, setSelectedAgentId] = useState<string | undefined>(undefined);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSendMessage = useCallback(async (content: string) => {
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      content,
      role: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    // Simulate agent response
    setTimeout(() => {
      const agentMessage: ChatMessage = {
        id: `agent-${Date.now()}`,
        content: `这是模拟回复：关于"${content}"的分析。这个功能需要后端API支持。`,
        role: 'assistant',
        agentName: demoAgents.find(a => a.id === selectedAgentId)?.name || 'Agent',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, agentMessage]);
      setIsLoading(false);
    }, 1000);
  }, [selectedAgentId]);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-slate-100">智能交互</h1>
          <p className="text-slate-400">与模拟智能体对话</p>
        </div>
      </div>

      <div className="grid lg:grid-cols-4 gap-6">
        {/* Agent List */}
        <div className="lg:col-span-1">
          <Card className="bg-slate-800/50 border-slate-700/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-slate-100">选择智能体</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {demoAgents.map((agent) => (
                <button
                  key={agent.id}
                  onClick={() => setSelectedAgentId(agent.id)}
                  className={`w-full flex items-center gap-3 p-3 rounded-lg transition-colors ${
                    selectedAgentId === agent.id
                      ? 'bg-[#D4AF37]/20 border border-[#D4AF37]/30'
                      : 'bg-slate-900/50 hover:bg-slate-700/50'
                  }`}
                >
                  <div className="p-2 bg-slate-700 rounded-full">
                    <Bot className="h-4 w-4 text-slate-400" />
                  </div>
                  <div className="text-left">
                    <div className="text-sm font-medium text-slate-200">{agent.name}</div>
                    <div className="text-xs text-slate-500">{agent.role}</div>
                  </div>
                </button>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Chat Area */}
        <div className="lg:col-span-3">
          <Card className="bg-slate-800/50 border-slate-700/50 h-[600px]">
            <CardHeader className="border-b border-slate-700/50 pb-4">
              <CardTitle className="text-sm text-slate-100 flex items-center gap-2">
                <MessageCircle className="h-4 w-4 text-[#D4AF37]" />
                {selectedAgentId
                  ? `与 ${demoAgents.find(a => a.id === selectedAgentId)?.name} 对话`
                  : '选择一个智能体开始对话'}
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0 h-[calc(100%-60px)]">
              {selectedAgentId ? (
                <div className="flex flex-col h-full">
                  {/* Messages area */}
                  <div className="flex-1 overflow-auto p-4 space-y-4">
                    {messages.length === 0 ? (
                      <div className="flex flex-col items-center justify-center h-full text-center">
                        <Bot className="h-12 w-12 text-slate-700 mb-4" />
                        <p className="text-slate-400 text-sm">
                          开始与 {demoAgents.find(a => a.id === selectedAgentId)?.name} 对话
                        </p>
                      </div>
                    ) : (
                      messages.map((message) => (
                        <div
                          key={message.id}
                          className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                          <div
                            className={`max-w-[70%] rounded-lg p-3 ${
                              message.role === 'user'
                                ? 'bg-[#D4AF37] text-slate-900'
                                : 'bg-slate-700 text-slate-100'
                            }`}
                          >
                            <div className="text-sm">{message.content}</div>
                            <div className="text-xs mt-1 opacity-70">
                              {message.timestamp?.toLocaleTimeString()}
                            </div>
                          </div>
                        </div>
                      ))
                    )}
                  </div>

                  {/* Input area */}
                  <div className="p-4 border-t border-slate-700/50">
                    <div className="flex gap-2">
                      <input
                        ref={inputRef}
                        type="text"
                        placeholder="输入消息..."
                        className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-[#D4AF37]"
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            const target = e.target as HTMLInputElement;
                            if (target.value.trim()) {
                              handleSendMessage(target.value.trim());
                              target.value = '';
                            }
                          }
                        }}
                        disabled={isLoading}
                      />
                      <Button
                        onClick={() => {
                          const input = inputRef.current;
                          if (input?.value.trim()) {
                            handleSendMessage(input.value.trim());
                            input.value = '';
                          }
                        }}
                        disabled={isLoading}
                        className="bg-[#D4AF37] hover:bg-[#D4AF37]/90 text-slate-900"
                      >
                        发送
                      </Button>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-center">
                  <Bot className="h-12 w-12 text-slate-700 mb-4" />
                  <p className="text-slate-400 text-sm">
                    请从左侧选择一个智能体开始对话
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
