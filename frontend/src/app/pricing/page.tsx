'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/hooks/use-auth';
import { useAuthApi } from '@/hooks/use-auth-api';
import { Button } from '@/components/ui/button';
import { Sparkles, Check, Crown } from 'lucide-react';
import { cn } from '@/lib/utils';

const tiers = [
  {
    id: 'free',
    name: '免费版',
    price: '¥0',
    period: '永久',
    description: '适合体验基础功能',
    features: [
      '命盘生成（每日1次）',
      '基础星曜解读',
      '十二宫简单分析',
      '姻缘基础分析',
    ],
    priceKey: null,
    highlighted: false,
    color: 'from-slate-500 to-slate-600',
  },
  {
    id: 'pro',
    name: 'Pro',
    price: '¥99',
    period: '/月',
    description: '适合深度研究紫微斗数',
    features: [
      '命盘生成（无限次）',
      '完整星曜深度解读',
      '四化全面分析',
      '姻缘完整分析',
      '流年运势预测',
      '报告生成',
    ],
    priceKey: 'pro_monthly',
    highlighted: true,
    color: 'from-[#D4AF37] to-[#B8960C]',
  },
  {
    id: 'premium',
    name: 'Premium',
    price: '¥299',
    period: '/月',
    description: '适合专业命理师及机构',
    features: [
      'Pro 全部功能',
      '多命盘对比分析',
      '因果链深度推演',
      'AI智能模拟预测',
      '优先客服支持',
      '专属数据导出',
    ],
    priceKey: 'premium_monthly',
    highlighted: false,
    color: 'from-purple-500 to-purple-600',
  },
];

export default function PricingPage() {
  const { user, loading: authLoading } = useAuth();
  const { createCheckoutSession } = useAuthApi();
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState('');

  async function handleSubscribe(priceKey: string | null) {
    if (!priceKey) return;
    if (!user) {
      window.location.href = '/auth/login?redirect=/pricing';
      return;
    }

    setError('');
    setLoading(priceKey);
    try {
      const result = await createCheckoutSession(
        priceKey,
        `${window.location.origin}/pricing?success=1`,
        `${window.location.origin}/pricing?canceled=1`
      );
      if (result.success && (result.data as { url?: string })?.url) {
        window.location.href = (result.data as { url: string }).url;
      } else {
        setError(result.error || '创建订单失败');
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : '创建订单失败');
    } finally {
      setLoading(null);
    }
  }

  return (
    <div className="min-h-[80vh] py-12">
      <div className="container max-w-5xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-12 space-y-4">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#D4AF37]/10 border border-[#D4AF37]/20 mb-4">
            <Crown className="h-4 w-4 text-[#D4AF37]" />
            <span className="text-sm text-[#D4AF37]">订阅计划</span>
          </div>
          <h1 className="text-4xl font-heading font-bold text-slate-100">
            选择您的订阅计划
          </h1>
          <p className="text-lg text-slate-400 max-w-2xl mx-auto">
            解锁完整紫微斗数分析能力，探索命运的无限可能
          </p>
        </div>

        {/* Success / Canceled messages */}
        {typeof window !== 'undefined' && new URLSearchParams(window.location.search).get('success') && (
          <div className="mb-8 rounded-lg bg-green-500/10 border border-green-500/20 px-4 py-3 text-sm text-green-400 text-center">
            订阅成功！感谢您的支持。
          </div>
        )}
        {typeof window !== 'undefined' && new URLSearchParams(window.location.search).get('canceled') && (
          <div className="mb-8 rounded-lg bg-yellow-500/10 border border-yellow-500/20 px-4 py-3 text-sm text-yellow-400 text-center">
            订单已取消，您可以继续浏览。
          </div>
        )}

        {error && (
          <div className="mb-8 rounded-lg bg-destructive/10 border border-destructive/20 px-4 py-3 text-sm text-destructive text-center">
            {error}
          </div>
        )}

        {/* Tier Cards */}
        <div className={cn(
          "grid grid-cols-1 md:grid-cols-3 gap-6",
        )}>
          {tiers.map((tier) => (
            <div
              key={tier.id}
              className={cn(
                "relative rounded-2xl border p-6 flex flex-col",
                tier.highlighted
                  ? "border-[#D4AF37]/50 bg-gradient-to-b from-[#D4AF37]/10 to-slate-900/80"
                  : "border-slate-700/50 bg-slate-800/30"
              )}
            >
              {tier.highlighted && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <span className="px-3 py-1 text-xs font-medium rounded-full bg-[#D4AF37] text-slate-900">
                    推荐
                  </span>
                </div>
              )}

              {/* Tier header */}
              <div className="mb-6">
                <div className={cn(
                  "inline-flex p-2 rounded-lg bg-gradient-to-br mb-3",
                  tier.color
                )}>
                  <Sparkles className="h-5 w-5 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-slate-100">{tier.name}</h3>
                <p className="text-sm text-slate-400 mt-1">{tier.description}</p>
              </div>

              {/* Price */}
              <div className="mb-6">
                <span className="text-3xl font-bold text-slate-100">{tier.price}</span>
                <span className="text-slate-400 ml-1">{tier.period}</span>
              </div>

              {/* Features */}
              <ul className="space-y-3 mb-8 flex-1">
                {tier.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-2 text-sm text-slate-300">
                    <Check className="h-4 w-4 text-[#D4AF37] mt-0.5 flex-shrink-0" />
                    {feature}
                  </li>
                ))}
              </ul>

              {/* CTA */}
              {tier.priceKey ? (
                <Button
                  onClick={() => handleSubscribe(tier.priceKey)}
                  disabled={loading === tier.priceKey || (authLoading && !user)}
                  className={cn(
                    "w-full",
                    tier.highlighted
                      ? "bg-[#D4AF37] hover:bg-[#D4AF37]/90 text-slate-900"
                      : ""
                  )}
                >
                  {loading === tier.priceKey ? '跳转中...' : user ? '立即订阅' : '登录后订阅'}
                </Button>
              ) : (
                <Button variant="outline" asChild className="w-full">
                  <Link href={user ? '/' : '/auth/login'}>
                    {user ? '当前方案' : '登录了解'}
                  </Link>
                </Button>
              )}
            </div>
          ))}
        </div>

        {/* Footer note */}
        <p className="text-center text-sm text-slate-500 mt-8">
          订阅后随时可取消，按月计费，安全便捷
        </p>
      </div>
    </div>
  );
}
