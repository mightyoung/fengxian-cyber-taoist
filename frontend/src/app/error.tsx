'use client';

import { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';

interface ErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function Error({ error, reset }: ErrorProps) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error('Application error:', error);
  }, [error]);

  return (
    <div className="container mx-auto p-6 flex items-center justify-center min-h-[50vh]">
      <Card className="max-w-md w-full bg-slate-900/50 border-red-900/30">
        <CardContent className="pt-6">
          <div className="text-center space-y-4">
            {/* Error Icon */}
            <div className="flex justify-center">
              <div className="p-4 rounded-full bg-red-900/20">
                <AlertTriangle className="h-12 w-12 text-red-400" />
              </div>
            </div>

            {/* Error Message */}
            <div className="space-y-2">
              <h2 className="text-xl font-semibold text-slate-100">
                出现了一些问题
              </h2>
              <p className="text-slate-400 text-sm">
                {error.message || '应用程序遇到了一个意外错误'}
              </p>
              {error.digest && (
                <p className="text-xs text-slate-500 font-mono">
                  Error ID: {error.digest}
                </p>
              )}
            </div>

            {/* Actions */}
            <div className="flex gap-3 justify-center pt-4">
              <Button
                onClick={() => window.location.href = '/'}
                variant="outline"
                className="border-slate-700 text-slate-300 hover:bg-slate-800"
              >
                <Home className="h-4 w-4 mr-2" />
                返回首页
              </Button>
              <Button
                onClick={reset}
                className="bg-[#D4AF37] hover:bg-[#D4AF37]/90 text-slate-900"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                重试
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
