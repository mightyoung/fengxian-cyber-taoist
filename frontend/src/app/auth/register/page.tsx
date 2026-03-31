'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/use-auth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Sparkles } from 'lucide-react';

export default function RegisterPage() {
  const router = useRouter();
  const { register } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [nickname, setNickname] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    if (password.length < 6) {
      setError('密码长度至少6位');
      return;
    }
    setLoading(true);
    try {
      await register(email, password, nickname || undefined);
      router.push('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : '注册失败');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-[80vh] items-center justify-center">
      <div className="w-full max-w-sm space-y-6">
        <div className="text-center space-y-2">
          <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-accent mb-4">
            <Sparkles className="h-6 w-6 text-accent-foreground" />
          </div>
          <h1 className="text-2xl font-heading font-bold text-slate-100">创建账户</h1>
          <p className="text-sm text-muted-foreground">开始您的命理探索之旅</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="rounded-md bg-destructive/10 border border-destructive/20 px-4 py-3 text-sm text-destructive">
              {error}
            </div>
          )}
          <div className="space-y-2">
            <label htmlFor="nickname" className="text-sm font-medium text-slate-200">昵称（选填）</label>
            <Input
              id="nickname"
              type="text"
              placeholder="您的昵称"
              value={nickname}
              onChange={e => setNickname(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <label htmlFor="email" className="text-sm font-medium text-slate-200">邮箱</label>
            <Input
              id="email"
              type="email"
              placeholder="your@email.com"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="space-y-2">
            <label htmlFor="password" className="text-sm font-medium text-slate-200">密码</label>
            <Input
              id="password"
              type="password"
              placeholder="至少6位"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
              minLength={6}
            />
          </div>
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? '注册中...' : '注册'}
          </Button>
        </form>

        <p className="text-center text-sm text-muted-foreground">
          已有账户？{' '}
          <Link href="/auth/login" className="text-accent hover:underline font-medium">
            立即登录
          </Link>
        </p>
      </div>
    </div>
  );
}
