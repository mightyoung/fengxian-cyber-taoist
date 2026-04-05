"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  LayoutGrid,
  Sparkles,
  Users,
  FileText,
  MessageCircle,
  Menu,
  X,
  LogOut,
  Heart,
  BookOpen,
} from "lucide-react";
import { useState } from "react";
import { ThemeToggle } from "./theme-toggle";
import { useAuth } from "@/hooks/use-auth";

// Divination (主线) 优先，Swarm/其他降为次级
const navItems = [
  {
    title: "命盘",
    href: "/birth-chart",
    icon: LayoutGrid,
    tag: "主线",
  },
  {
    title: "姻缘",
    href: "/divination/relationship",
    icon: Heart,
    tag: "主线",
  },
  {
    title: "报告",
    href: "/report",
    icon: FileText,
  },
  {
    title: "中心",
    href: "/insights",
    icon: BookOpen,
    tag: "新",
  },
  {
    title: "模拟",
    href: "/simulation",
    icon: Sparkles,
  },
  {
    title: "图谱",
    href: "/graph",
    icon: Users,
  },
  {
    title: "交互",
    href: "/chat",
    icon: MessageCircle,
  },
];

export function TopNav() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { user, loading, logout } = useAuth();

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between px-4">
        {/* Logo */}
        <Link href="/" className="flex items-center space-x-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent">
            <Sparkles className="h-5 w-5 text-accent-foreground" />
          </div>
          <span className="font-heading text-xl font-bold">FengxianCyberTaoist</span>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center space-x-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-md transition-colors",
                  isActive
                    ? "bg-accent/10 text-accent"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted"
                )}
              >
                <Icon className="h-4 w-4" />
                {item.title}
                {item.tag === '主线' && (
                  <span className="ml-1 text-xs px-1.5 py-0.5 rounded bg-[#D4AF37]/20 text-[#D4AF37]">主</span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Right side actions */}
        <div className="flex items-center gap-2">
          {!loading && (
            user ? (
              <>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground hidden sm:inline">
                    {user.nickname || user.email}
                  </span>
                  <span className={cn(
                    "text-xs px-1.5 py-0.5 rounded font-medium",
                    user.subscription_tier === 'premium' && "bg-purple-500/20 text-purple-400",
                    user.subscription_tier === 'pro' && "bg-[#D4AF37]/20 text-[#D4AF37]",
                    user.subscription_tier === 'free' && "bg-slate-700/50 text-slate-400",
                  )}>
                    {user.subscription_tier === 'premium' ? 'Premium' : user.subscription_tier === 'pro' ? 'Pro' : 'Free'}
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <Button variant="ghost" size="sm" asChild className="hidden sm:inline-flex">
                    {user.subscription_tier === 'free' ? (
                      <Link href="/pricing">升级</Link>
                    ) : (
                      <Link href="/account">管理订阅</Link>
                    )}
                  </Button>
                  <Button variant="ghost" size="sm" onClick={logout} className="gap-1.5">
                    <LogOut className="h-4 w-4" />
                    <span className="hidden sm:inline">退出</span>
                  </Button>
                </div>
              </>
            ) : (
              <>
                <Link href="/auth/login">
                <Button variant="ghost" size="sm">登录</Button>
                </Link>
                <Link href="/auth/register">
                <Button variant="default" size="sm">注册</Button>
                </Link>
              </>
            )
          )}
          <ThemeToggle />
          <Button variant="ghost" size="icon" className="md:hidden" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
        </div>
      </div>

      {/* Mobile Navigation */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-border">
          <nav className="container px-4 py-4 flex flex-col space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname.startsWith(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={cn(
                    "flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors",
                    isActive
                      ? "bg-accent/10 text-accent"
                      : "text-muted-foreground hover:text-foreground hover:bg-muted"
                  )}
                >
                  <Icon className="h-4 w-4" />
                  {item.title}
                </Link>
              );
            })}
            {!loading && (
              user ? (
                <button
                  onClick={() => { logout(); setMobileMenuOpen(false); }}
                  className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md text-muted-foreground hover:text-foreground hover:bg-muted w-full"
                >
                  <LogOut className="h-4 w-4" />
                  退出 ({user.nickname || user.email})
                </button>
              ) : (
                <>
                  <Link href="/auth/login" onClick={() => setMobileMenuOpen(false)} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md text-muted-foreground hover:text-foreground hover:bg-muted">
                    登录
                  </Link>
                  <Link href="/auth/register" onClick={() => setMobileMenuOpen(false)} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md text-muted-foreground hover:text-foreground hover:bg-muted">
                    注册
                  </Link>
                </>
              )
            )}
          </nav>
        </div>
      )}
    </header>
  );
}
