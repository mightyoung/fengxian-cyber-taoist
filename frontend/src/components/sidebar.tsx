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
  ChevronLeft,
  ChevronRight,
  Heart,
} from "lucide-react";
import { useState } from "react";

const sidebarItems = [
  {
    title: "首页",
    href: "/",
    icon: LayoutGrid,
  },
  {
    title: "命盘分析",
    href: "/birth-chart",
    icon: LayoutGrid,
    description: "紫微斗数命盘",
    tag: "主线",
  },
  {
    title: "姻缘分析",
    href: "/divination/relationship",
    icon: Heart,
    description: "姻缘感情分析",
    tag: "主线",
  },
  {
    title: "预测报告",
    href: "/report",
    icon: FileText,
    description: "AI 分析报告",
  },
  {
    title: "智能模拟",
    href: "/simulation",
    icon: Sparkles,
    description: "多智能体模拟",
  },
  {
    title: "知识图谱",
    href: "/graph",
    icon: Users,
    description: "实体关系网络",
  },
  {
    title: "智能交互",
    href: "/chat",
    icon: MessageCircle,
    description: "与智能体对话",
  },
];

interface SidebarProps {
  className?: string;
}

export function Sidebar({ className }: SidebarProps) {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={cn(
        "relative flex flex-col border-r border-border bg-card transition-all duration-300",
        collapsed ? "w-16" : "w-64",
        className
      )}
    >
      {/* Collapse toggle button */}
      <Button
        variant="ghost"
        size="icon"
        className="absolute -right-3 top-6 z-10 h-6 w-6 rounded-full border border-border bg-background shadow-sm"
        onClick={() => setCollapsed(!collapsed)}
      >
        {collapsed ? (
          <ChevronRight className="h-3 w-3" />
        ) : (
          <ChevronLeft className="h-3 w-3" />
        )}
      </Button>

      {/* Navigation items */}
      <nav className="flex-1 space-y-1 p-2">
        {sidebarItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href ||
            (item.href !== "/" && pathname.startsWith(item.href));

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 transition-all hover:bg-accent/10",
                isActive
                  ? "bg-accent/10 text-accent"
                  : "text-muted-foreground hover:text-foreground",
                collapsed && "justify-center px-2"
              )}
              title={collapsed ? item.title : undefined}
            >
              <Icon className={cn("h-5 w-5 shrink-0", isActive && "text-accent")} />
              {!collapsed && (
                <div className="flex flex-col">
                  <div className="flex items-center gap-1.5">
                    <span className="text-sm font-medium">{item.title}</span>
                    {item.tag === '主线' && (
                      <span className="text-xs px-1 py-0.5 rounded bg-[#D4AF37]/20 text-[#D4AF37]">主</span>
                    )}
                  </div>
                  {item.description && (
                    <span className="text-xs text-muted-foreground">
                      {item.description}
                    </span>
                  )}
                </div>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      {!collapsed && (
        <div className="border-t border-border p-4">
          <p className="text-xs text-muted-foreground text-center">
            FengxianCyberTaoist v0.1.0
          </p>
        </div>
      )}
    </aside>
  );
}
