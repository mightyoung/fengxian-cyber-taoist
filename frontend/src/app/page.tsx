'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { Sparkles, LayoutGrid, Users, FileText, MessageCircle, ArrowRight, Heart } from 'lucide-react';

const features = [
  {
    title: '命盘分析',
    description: '紫微斗数命盘分析，解读您的命运轨迹',
    href: '/birth-chart',
    icon: LayoutGrid,
    color: 'from-purple-500 to-purple-600',
  },
  {
    title: '姻缘分析',
    description: '姻缘感情分析，解读您的婚姻运势',
    href: '/divination/relationship',
    icon: Heart,
    color: 'from-pink-500 to-rose-600',
  },
  {
    title: '智能模拟',
    description: '多智能体社会模拟，预测未来发展',
    href: '/simulation',
    icon: Sparkles,
    color: 'from-amber-500 to-amber-600',
  },
  {
    title: '知识图谱',
    description: '实体关系网络，可视化知识结构',
    href: '/graph',
    icon: Users,
    color: 'from-emerald-500 to-emerald-600',
  },
  {
    title: '预测报告',
    description: 'AI 生成的深度预测分析报告',
    href: '/report',
    icon: FileText,
    color: 'from-blue-500 to-blue-600',
  },
  {
    title: '智能交互',
    description: '与模拟智能体实时对话互动',
    href: '/chat',
    icon: MessageCircle,
    color: 'from-pink-500 to-pink-600',
  },
];

export default function Home() {
  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center space-y-4 py-12"
      >
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#D4AF37]/10 border border-[#D4AF37]/20 mb-4">
          <Sparkles className="h-4 w-4 text-[#D4AF37]" />
          <span className="text-sm text-[#D4AF37]">AI 命理预测平台</span>
        </div>
        <h1 className="text-4xl md:text-5xl font-heading font-bold text-slate-100">
          欢迎使用 <span className="text-[#D4AF37]">FengxianCyberTaoist</span>
        </h1>
        <p className="text-lg text-slate-400 max-w-2xl mx-auto">
          融合紫微斗数与多智能体社会模拟的 AI 预测平台，通过深度学习与智能推演，为您揭示命运轨迹与未来发展趋势。
        </p>
      </motion.div>

      {/* Features Grid */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
      >
        {features.map((feature, index) => {
          const Icon = feature.icon;
          return (
            <Link key={feature.href} href={feature.href}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.1 * index }}
                className="group relative overflow-hidden rounded-xl bg-slate-800/50 border border-slate-700/50 p-6 hover:border-[#D4AF37]/30 transition-all duration-300"
              >
                {/* Gradient Background */}
                <div className={`absolute inset-0 bg-gradient-to-br ${feature.color} opacity-0 group-hover:opacity-5 transition-opacity duration-300`} />

                {/* Icon */}
                <div className={`inline-flex p-3 rounded-lg bg-gradient-to-br ${feature.color} mb-4`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>

                {/* Content */}
                <h3 className="text-lg font-semibold text-slate-100 mb-2 group-hover:text-[#D4AF37] transition-colors">
                  {feature.title}
                </h3>
                <p className="text-sm text-slate-400 mb-4">
                  {feature.description}
                </p>

                {/* Arrow */}
                <div className="flex items-center text-[#D4AF37] text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                  进入
                  <ArrowRight className="h-4 w-4 ml-1 group-hover:translate-x-1 transition-transform" />
                </div>
              </motion.div>
            </Link>
          );
        })}
      </motion.div>

      {/* Quick Start Section */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.5 }}
        className="bg-gradient-to-r from-slate-800/80 to-slate-900/80 rounded-xl border border-slate-700/50 p-8 text-center"
      >
        <h2 className="text-2xl font-heading font-semibold text-slate-100 mb-4">
          快速开始
        </h2>
        <p className="text-slate-400 mb-6 max-w-xl mx-auto">
          输入您的出生信息，即刻生成命盘分析。或者上传文档，开始构建知识图谱并运行模拟预测。
        </p>
        <div className="flex justify-center gap-4">
          <Link
            href="/birth-chart"
            className="inline-flex items-center gap-2 px-6 py-3 bg-[#D4AF37] hover:bg-[#D4AF37]/90 text-slate-900 font-medium rounded-lg transition-colors"
          >
            <LayoutGrid className="h-4 w-4" />
            生成命盘
          </Link>
          <Link
            href="/simulation"
            className="inline-flex items-center gap-2 px-6 py-3 bg-slate-700 hover:bg-slate-600 text-slate-100 font-medium rounded-lg transition-colors"
          >
            <Sparkles className="h-4 w-4" />
            开始模拟
          </Link>
        </div>
      </motion.div>
    </div>
  );
}
