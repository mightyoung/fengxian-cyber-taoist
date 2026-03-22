'use client';

import { Skeleton } from '@/components/ui/skeleton';
import { Card } from '@/components/ui/card';

export default function Loading() {
  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header skeleton */}
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <Skeleton className="h-8 w-48 bg-slate-800" />
          <Skeleton className="h-4 w-64 bg-slate-800" />
        </div>
        <Skeleton className="h-10 w-32 bg-slate-800" />
      </div>

      {/* Content skeleton */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left sidebar skeleton */}
        <div className="lg:col-span-1 space-y-4">
          <Card className="p-4 bg-slate-900/50 border-slate-800">
            <Skeleton className="h-6 w-24 mb-4 bg-slate-800" />
            <div className="space-y-3">
              <Skeleton className="h-10 w-full bg-slate-800" />
              <Skeleton className="h-10 w-full bg-slate-800" />
              <Skeleton className="h-10 w-full bg-slate-800" />
            </div>
          </Card>
          <Card className="p-4 bg-slate-900/50 border-slate-800">
            <Skeleton className="h-6 w-32 mb-4 bg-slate-800" />
            <Skeleton className="h-20 w-full bg-slate-800" />
          </Card>
        </div>

        {/* Main content skeleton */}
        <div className="lg:col-span-2">
          <Card className="bg-slate-900/50 border-slate-800">
            <Card className="m-4 bg-slate-800/50">
              <div className="p-8">
                <Skeleton className="h-64 w-64 rounded-full mx-auto mb-4 bg-slate-700" />
                <Skeleton className="h-4 w-32 mx-auto bg-slate-700" />
              </div>
            </Card>
          </Card>
        </div>
      </div>
    </div>
  );
}
