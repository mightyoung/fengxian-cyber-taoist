'use client';

import Link from 'next/link';
import type { ComponentType } from 'react';
import { motion } from 'framer-motion';
import { Sparkles, LayoutGrid, Users, MessageCircle, ArrowRight, Heart, Zap, BookOpen } from 'lucide-react';
import { RealtimeVibe } from '@/components/birth-chart/realtime-vibe';
import { useBirthChartStore } from '@/stores/birthChartStore';

type FeatureItem = {
  title: string;
  description: string;
  href: string;
  icon: ComponentType<{ className?: string }>;
  color: string;
  tag?: string;
};

// 将“智能模拟”提升为核心功能
const coreFeatures = [
  {
    title: '智能推演',
    description: '多智能体社会模拟，因果扰动预演未来发展',
    href: '/simulation',
    icon: Sparkles,
    color: 'from-amber-500 to-amber-600',
    tag: '核心',
  },
  {
    title: '命盘分析',
    description: '紫微斗数命盘分析，解读您的命运轨迹',
    href: '/birth-chart',
    icon: LayoutGrid,
    color: 'from-purple-500 to-purple-600',
    tag: '主线',
  },
];

const assistantFeatures = [
  {
    title: '内容中心',
    description: '统一回看命盘、报告和历史结果，支持继续上次分析',
    href: '/insights',
    icon: BookOpen,
    color: 'from-slate-400 to-slate-600',
  },
  {
    title: '姻缘分析',
    description: '姻缘感情分析，解读您的婚姻运势',
    href: '/divination/relationship',
    icon: Heart,
    color: 'from-pink-500 to-rose-600',
  },
  {
    title: '知识图谱',
    description: '实体关系网络，可视化知识结构',
    href: '/graph',
    icon: Users,
    color: 'from-emerald-500 to-emerald-600',
  },
  {
    title: '赛博咨询',
    description: '与赛博道长对话，解惑命理与模拟因果',
    href: '/chat',
    icon: MessageCircle,
    color: 'from-cyan-500 to-cyan-600',
  },
];

function FeatureCard({ feature, delay }: { feature: FeatureItem; delay: number }) {
  const Icon = feature.icon;
  return (
    <Link href={feature.href}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay }}
        className="group relative overflow-hidden rounded-xl bg-slate-800/50 border border-slate-700/50 p-6 hover:border-[#D4AF37]/30 transition-all duration-300 h-full"
      >
        <div className={`absolute inset-0 bg-gradient-to-br ${feature.color} opacity-0 group-hover:opacity-5 transition-opacity duration-300`} />
        <div className="flex justify-between items-start mb-4">
          <div className={`inline-flex p-3 rounded-lg bg-gradient-to-br ${feature.color}`}>
            <Icon className="h-6 w-6 text-white" />
          </div>
          {feature.tag && (
            <span className="text-[10px] px-2 py-0.5 rounded bg-accent/20 text-accent border border-accent/20 font-bold uppercase tracking-wider">
              {feature.tag}
            </span>
          )}
        </div>
        <h3 className="text-lg font-semibold text-slate-100 mb-2 group-hover:text-[#D4AF37] transition-colors">
          {feature.title}
        </h3>
        <p className="text-sm text-slate-400 mb-4">
          {feature.description}
        </p>
        <div className="flex items-center text-[#D4AF37] text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity">
          进入推演
          <ArrowRight className="h-4 w-4 ml-1 group-hover:translate-x-1 transition-transform" />
        </div>
      </motion.div>
    </Link>
  );
}

export default function Home() {
  const { currentChart } = useBirthChartStore();

  return (
    <div className="space-y-12 pb-20">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center space-y-4 py-8"
      >
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#D4AF37]/10 border border-[#D4AF37]/20 mb-4">
          <Zap className="h-4 w-4 text-[#D4AF37]" />
          <span className="text-sm text-[#D4AF37] font-medium">凤仙郡赛博道士 · 天人合一</span>
        </div>
        <h1 className="text-4xl md:text-6xl font-heading font-bold text-slate-100 tracking-tight">
          洞悉因果，<span className="text-[#D4AF37]">模拟未来</span>
        </h1>
        <p className="text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed">
          全球首款融合紫微斗数与多智能体 Swarm 引擎的预测平台。
          不仅仅是算命，更是在数字孪生世界中为您预演人生的每一次博弈。
        </p>
      </motion.div>

      {/* Main Grid: Vibe + Core Features */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Realtime Vibe - Always visible if chart exists, or demo */}
        <div className="lg:col-span-1">
          <div className="sticky top-24 space-y-4">
            <h2 className="text-sm font-bold text-slate-500 uppercase tracking-widest px-1">当前气场</h2>
            <RealtimeVibe chartId={currentChart?.id || 'demo'} className="w-full" />
            <div className="p-4 rounded-xl border border-dashed border-slate-700 text-xs text-slate-500 leading-relaxed">
              提示：实时气场基于流分飞化技术，每分钟感应一次天地能量对您的瞬时扰动。
            </div>
          </div>
        </div>

        {/* Core & Assistant Features */}
        <div className="lg:col-span-2 space-y-8">
          <div className="space-y-4">
            <h2 className="text-sm font-bold text-slate-500 uppercase tracking-widest px-1">核心推演</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {coreFeatures.map((f, i) => <FeatureCard key={f.href} feature={f} delay={0.1 * i} />)}
            </div>
          </div>

          <div className="space-y-4">
            <h2 className="text-sm font-bold text-slate-500 uppercase tracking-widest px-1">辅助工具</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {assistantFeatures.map((f, i) => <FeatureCard key={f.href} feature={f} delay={0.2 + 0.05 * i} />)}
            </div>
          </div>
        </div>
      </div>

      {/* Stats / Call to Action */}
      <motion.div
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        className="rounded-2xl bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50 p-10 text-center relative overflow-hidden"
      >
        <div className="absolute top-0 right-0 w-64 h-64 bg-accent/5 rounded-full blur-3xl -mr-32 -mt-32" />
        <h2 className="text-2xl font-heading font-semibold text-slate-100 mb-4">
          因果已显，请速起卦
        </h2>
        <p className="text-slate-400 mb-8 max-w-xl mx-auto">
          已有 45,000+ 道友在此推演命运。加入凤仙郡，开启你的赛博修行之旅。
        </p>
        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <Link
            href="/birth-chart"
            className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-[#D4AF37] hover:bg-[#D4AF37]/90 text-slate-900 font-bold rounded-xl transition-all hover:scale-105 active:scale-95"
          >
            <LayoutGrid className="h-5 w-5" />
            一键起卦
          </Link>
          <Link
            href="/simulation"
            className="inline-flex items-center justify-center gap-2 px-8 py-4 border border-slate-700 hover:border-accent/50 text-slate-200 font-bold rounded-xl transition-all"
          >
            <Sparkles className="h-5 w-5 text-accent" />
            发起模拟
          </Link>
        </div>
      </motion.div>
    </div>
  );
}
