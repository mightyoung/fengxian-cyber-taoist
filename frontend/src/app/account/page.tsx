'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/hooks/use-auth';
import { useAuthApi } from '@/hooks/use-auth-api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowLeft, Crown, CreditCard, AlertCircle, Check } from 'lucide-react';
import { cn } from '@/lib/utils';

type SubscriptionTier = 'free' | 'pro' | 'premium';
type SubscriptionStatus = 'active' | 'cancelled' | 'expired' | 'pending';

interface SubscriptionData {
  tier: SubscriptionTier;
  status: SubscriptionStatus;
  stripe_customer_id: string | null;
  stripe_subscription_id: string | null;
  starts_at: string;
  expires_at: string | null;
  cancelled_at: string | null;
}

const tierColors: Record<SubscriptionTier, string> = {
  free: 'bg-slate-700/50 text-slate-400',
  pro: 'bg-[#D4AF37]/20 text-[#D4AF37]',
  premium: 'bg-purple-500/20 text-purple-400',
};

const tierLabels: Record<SubscriptionTier, string> = {
  free: '免费版',
  pro: 'Pro',
  premium: 'Premium',
};

const statusLabels: Record<SubscriptionStatus, string> = {
  active: '有效',
  cancelled: '已取消',
  expired: '已过期',
  pending: '待激活',
};

const featureGroups = [
  {
    tier: 'pro',
    name: 'Pro',
    price: '¥99/月',
    features: [
      '命盘生成（无限次）',
      '完整星曜深度解读',
      '四化全面分析',
      '姻缘完整分析',
      '流年运势预测',
      '报告生成',
    ],
  },
  {
    tier: 'premium',
    name: 'Premium',
    price: '¥299/月',
    features: [
      'Pro 全部功能',
      '多命盘对比分析',
      '因果链深度推演',
      'AI智能模拟预测',
      '优先客服支持',
      '专属数据导出',
    ],
  },
];

export default function AccountPage() {
  const { user, loading: authLoading } = useAuth();
  const { getSubscription, cancelSubscription } = useAuthApi();
  const [subscription, setSubscription] = useState<SubscriptionData | null>(null);
  const [subLoading, setSubLoading] = useState(true);
  const [cancelling, setCancelling] = useState(false);
  const [cancelSuccess, setCancelSuccess] = useState(false);
  const [error, setError] = useState('');

  // Redirect if not logged in
  useEffect(() => {
    if (!authLoading && !user && typeof window !== 'undefined') {
      window.location.href = '/auth/login?redirect=/account';
    }
  }, [authLoading, user]);

  // Load subscription data
  useEffect(() => {
    if (user) {
      getSubscription()
        .then((res) => {
          if (res.success && res.data) {
            setSubscription(res.data as SubscriptionData);
          }
        })
        .catch(() => {})
        .finally(() => setSubLoading(false));
    }
  }, [user, getSubscription]);

  async function handleCancel() {
    setError('');
    setCancelling(true);
    try {
      const result = await cancelSubscription();
      if (result.success) {
        setCancelSuccess(true);
        setSubscription((prev) =>
          prev ? { ...prev, status: 'cancelled' } : null
        );
      } else {
        setError(result.error || '取消订阅失败');
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : '取消订阅失败');
    } finally {
      setCancelling(false);
    }
  }

  // Loading state
  if (authLoading || !user) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center">
        <div className="text-slate-400">加载中...</div>
      </div>
    );
  }

  const isPaidUser = subscription?.tier === 'pro' || subscription?.tier === 'premium';
  const isActive = subscription?.status === 'active';

  return (
    <div className="min-h-[80vh] py-8">
      <div className="container max-w-3xl mx-auto px-4 space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Link href="/">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-slate-100">账户管理</h1>
            <p className="text-sm text-muted-foreground">管理您的订阅和账户信息</p>
          </div>
        </div>

        {/* Current Plan */}
        <Card className="bg-slate-800/50 border-slate-700/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-slate-100">
              <Crown className="h-5 w-5 text-[#D4AF37]" />
              当前方案
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {subLoading ? (
              <div className="text-slate-400">加载中...</div>
            ) : subscription ? (
              <>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className={cn(
                      "text-sm px-3 py-1 rounded-full font-medium",
                      tierColors[subscription.tier]
                    )}>
                      {tierLabels[subscription.tier]}
                    </span>
                    <span className="text-slate-400 text-sm">
                      状态: {statusLabels[subscription.status]}
                    </span>
                  </div>
                  {!isPaidUser && (
                    <Link href="/pricing">
                      <Button size="sm" className="bg-[#D4AF37] hover:bg-[#D4AF37]/90 text-slate-900">
                        升级
                      </Button>
                    </Link>
                  )}
                </div>

                {subscription.expires_at && (
                  <p className="text-sm text-slate-400">
                    {subscription.status === 'cancelled'
                      ? `将于 ${new Date(subscription.expires_at).toLocaleDateString('zh-CN')} 到期`
                      : `到期时间: ${new Date(subscription.expires_at).toLocaleDateString('zh-CN')}`}
                  </p>
                )}

                {error && (
                  <div className="flex items-center gap-2 text-sm text-red-400">
                    <AlertCircle className="h-4 w-4" />
                    {error}
                  </div>
                )}

                {cancelSuccess && (
                  <div className="flex items-center gap-2 text-sm text-green-400">
                    <Check className="h-4 w-4" />
                    订阅已取消
                  </div>
                )}

                {/* Cancel button for active paid subscribers */}
                {isPaidUser && isActive && !cancelSuccess && (
                  <div className="pt-4 border-t border-slate-700">
                    <p className="text-sm text-slate-400 mb-3">
                      取消订阅后，您将继续使用到本期结束
                    </p>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleCancel}
                      disabled={cancelling}
                      className="border-red-500/30 text-red-400 hover:bg-red-500/10"
                    >
                      {cancelling ? '处理中...' : '取消订阅'}
                    </Button>
                  </div>
                )}
              </>
            ) : (
              <div className="text-slate-400">无法加载订阅信息</div>
            )}
          </CardContent>
        </Card>

        {/* Available Plans */}
        {!isPaidUser && (
          <div>
            <h2 className="text-lg font-semibold text-slate-100 mb-4">升级方案</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {featureGroups.map((group) => (
                <Card
                  key={group.tier}
                  className={cn(
                    "bg-slate-800/50 border-slate-700/50",
                    group.tier === 'pro' && "border-[#D4AF37]/30"
                  )}
                >
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <span className={cn(
                        "text-sm px-2 py-1 rounded font-medium",
                        tierColors[group.tier as SubscriptionTier]
                      )}>
                        {group.name}
                      </span>
                      <span className="text-lg font-bold text-slate-100">{group.price}</span>
                    </div>
                    <ul className="space-y-2 mb-4">
                      {group.features.map((f) => (
                        <li key={f} className="flex items-start gap-2 text-sm text-slate-300">
                          <Check className="h-4 w-4 text-[#D4AF37] mt-0.5 flex-shrink-0" />
                          {f}
                        </li>
                      ))}
                    </ul>
                    <Link href="/pricing" className="block">
                      <Button
                        size="sm"
                        className={cn(
                          "w-full",
                          group.tier === 'pro'
                            ? "bg-[#D4AF37] hover:bg-[#D4AF37]/90 text-slate-900"
                            : ""
                        )}
                      >
                        立即订阅
                      </Button>
                    </Link>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Account Info */}
        <Card className="bg-slate-800/50 border-slate-700/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-slate-100">
              <CreditCard className="h-5 w-5 text-slate-400" />
              账户信息
            </CardTitle>
          </CardHeader>
          <CardContent>
            {user && (
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-400">邮箱</span>
                  <span className="text-slate-200">{user.email}</span>
                </div>
                {user.nickname && (
                  <div className="flex justify-between">
                    <span className="text-slate-400">昵称</span>
                    <span className="text-slate-200">{user.nickname}</span>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
