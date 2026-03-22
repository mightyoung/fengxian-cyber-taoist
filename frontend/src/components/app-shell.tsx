"use client";

import { TopNav } from "./top-nav";
import { Sidebar } from "./sidebar";
import { cn } from "@/lib/utils";

interface AppShellProps {
  children: React.ReactNode;
  className?: string;
  hideSidebar?: boolean;
}

export function AppShell({ children, className, hideSidebar = false }: AppShellProps) {
  return (
    <div className="flex min-h-screen flex-col">
      <TopNav />
      <div className="flex flex-1">
        {!hideSidebar && <Sidebar />}
        <main
          className={cn(
            "flex-1 overflow-auto",
            "bg-background",
            className
          )}
        >
          <div className="container mx-auto p-4 md:p-6 lg:p-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
