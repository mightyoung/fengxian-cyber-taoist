'use client';

import { memo, useState } from 'react';
import { Download, FileJson, FileText, File } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface ReportExportProps {
  reportId: string;
  className?: string;
}

type ExportFormat = 'pdf' | 'json' | 'markdown';

function ReportExport({ reportId, className }: ReportExportProps) {
  const [isExporting, setIsExporting] = useState(false);
  const [showMenu, setShowMenu] = useState(false);

  const handleExport = async (format: ExportFormat) => {
    setIsExporting(true);
    setShowMenu(false);

    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001/api';

      if (format === 'json') {
        const response = await fetch(`${API_BASE}/report/${reportId}`);
        const data = await response.json();

        if (data.success) {
          const blob = new Blob([JSON.stringify(data.data, null, 2)], {
            type: 'application/json',
          });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `report-${reportId}.json`;
          a.click();
          URL.revokeObjectURL(url);
        }
      } else if (format === 'markdown') {
        const response = await fetch(`${API_BASE}/report/${reportId}`);
        const data = await response.json();

        if (data.success && data.data.markdown_content) {
          const blob = new Blob([data.data.markdown_content], {
            type: 'text/markdown',
          });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `report-${reportId}.md`;
          a.click();
          URL.revokeObjectURL(url);
        }
      } else if (format === 'pdf') {
        window.open(`${API_BASE}/report/${reportId}/download`, '_blank');
      }
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className={cn('relative', className)}>
      <Button
        variant="outline"
        size="sm"
        className={cn(
          'gap-2 border-slate-700 text-slate-300 hover:text-slate-100 hover:bg-slate-800',
          'hover:border-slate-600 bg-slate-900/50'
        )}
        disabled={isExporting}
        onClick={() => setShowMenu(!showMenu)}
      >
        <Download className="h-4 w-4" />
        {isExporting ? 'Exporting...' : 'Export'}
      </Button>

      {showMenu && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setShowMenu(false)}
          />
          <div className="absolute right-0 mt-2 w-48 bg-slate-900 border border-slate-800 rounded-lg shadow-lg z-50 py-1">
            <button
              className="w-full px-4 py-2 text-left text-sm text-slate-300 hover:bg-slate-800 flex items-center gap-2"
              onClick={() => handleExport('markdown')}
            >
              <FileText className="h-4 w-4" />
              Export as Markdown
            </button>
            <button
              className="w-full px-4 py-2 text-left text-sm text-slate-300 hover:bg-slate-800 flex items-center gap-2"
              onClick={() => handleExport('json')}
            >
              <FileJson className="h-4 w-4" />
              Export as JSON
            </button>
            <div className="h-px bg-slate-800 my-1" />
            <button
              className="w-full px-4 py-2 text-left text-sm text-slate-300 hover:bg-slate-800 flex items-center gap-2"
              onClick={() => handleExport('pdf')}
            >
              <File className="h-4 w-4" />
              Export as PDF
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export const ReportExportMemoized = memo(ReportExport);
ReportExportMemoized.displayName = 'ReportExport';
