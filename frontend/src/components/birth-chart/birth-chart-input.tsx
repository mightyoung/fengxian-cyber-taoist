'use client';

import { useState, useCallback, memo } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BirthChartInput as BirthChartInputType } from '@/types/birth-chart';

interface BirthChartInputProps {
  onSubmit: (input: BirthChartInputType) => void;
  isLoading?: boolean;
  className?: string;
}

const currentYear = new Date().getFullYear();
const years = Array.from({ length: 120 }, (_, i) => currentYear - i);
const months = Array.from({ length: 12 }, (_, i) => i + 1);
const days = Array.from({ length: 31 }, (_, i) => i + 1);
const hours = Array.from({ length: 24 }, (_, i) => i);

export const BirthChartInput = memo(function BirthChartInput({
  onSubmit,
  isLoading = false,
  className,
}: BirthChartInputProps) {
  const [year, setYear] = useState<number>(1990);
  const [month, setMonth] = useState<number>(1);
  const [day, setDay] = useState<number>(1);
  const [hour, setHour] = useState<number>(0);
  const [gender, setGender] = useState<'male' | 'female'>('male');
  const [rawText, setRawText] = useState<string>('');
  const [useRawText, setUseRawText] = useState<boolean>(false);

  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    if (useRawText && rawText) {
      onSubmit({
        gender,
        raw_text: rawText,
      });
    } else {
      onSubmit({
        year,
        month,
        day,
        hour,
        gender,
      });
    }
  }, [year, month, day, hour, gender, rawText, useRawText, onSubmit]);

  return (
    <Card className={className}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-lg font-heading">出生信息</CardTitle>
        <div className="flex items-center gap-2">
          <span className="text-xs text-muted-foreground">粘贴命盘</span>
          <input 
            type="checkbox" 
            checked={useRawText} 
            onChange={(e) => setUseRawText(e.target.checked)}
            className="w-4 h-4 accent-accent"
          />
        </div>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {useRawText ? (
            <div className="space-y-2">
              <label htmlFor="rawText" className="text-sm font-medium text-slate-300">
                粘贴文墨天机排盘文本
              </label>
              <textarea
                id="rawText"
                value={rawText}
                onChange={(e) => setRawText(e.target.value)}
                placeholder="在此粘贴从文墨天机复制的命盘文本..."
                className="w-full h-32 p-3 rounded-md border border-slate-700 bg-slate-900/50 text-slate-100 text-xs font-mono focus:ring-1 focus:ring-accent outline-none"
              />
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-4">
              {/* Year */}
              <div className="space-y-2">
                <label htmlFor="year" className="text-sm font-medium">
                  年份
                </label>
                <select
                  id="year"
                  value={year}
                  onChange={(e) => setYear(Number(e.target.value))}
                  className="w-full h-10 px-3 rounded-md border border-slate-700 bg-slate-800 text-slate-100"
                >
                  {years.map((y) => (
                    <option key={y} value={y}>
                      {y}年
                    </option>
                  ))}
                </select>
              </div>

              {/* Month */}
              <div className="space-y-2">
                <label htmlFor="month" className="text-sm font-medium">
                  月份
                </label>
                <select
                  id="month"
                  value={month}
                  onChange={(e) => setMonth(Number(e.target.value))}
                  className="w-full h-10 px-3 rounded-md border border-slate-700 bg-slate-800 text-slate-100"
                >
                  {months.map((m) => (
                    <option key={m} value={m}>
                      {m}月
                    </option>
                  ))}
                </select>
              </div>

              {/* Day */}
              <div className="space-y-2">
                <label htmlFor="day" className="text-sm font-medium">
                  日期
                </label>
                <select
                  id="day"
                  value={day}
                  onChange={(e) => setDay(Number(e.target.value))}
                  className="w-full h-10 px-3 rounded-md border border-slate-700 bg-slate-800 text-slate-100"
                >
                  {days.map((d) => (
                    <option key={d} value={d}>
                      {d}日
                    </option>
                  ))}
                </select>
              </div>

              {/* Hour */}
              <div className="space-y-2">
                <label htmlFor="hour" className="text-sm font-medium">
                  时辰 (小时)
                </label>
                <select
                  id="hour"
                  value={hour}
                  onChange={(e) => setHour(Number(e.target.value))}
                  className="w-full h-10 px-3 rounded-md border border-slate-700 bg-slate-800 text-slate-100"
                >
                  {hours.map((h) => (
                    <option key={h} value={h}>
                      {h.toString().padStart(2, '0')}:00
                    </option>
                  ))}
                </select>
              </div>
            </div>
          )}

          {/* Gender - Outside the ternary or repeated if needed, but here better outside for simplicity */}
          <div className="space-y-2">
            <label className="text-sm font-medium">性别</label>
            <div className="flex gap-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="gender"
                  value="male"
                  checked={gender === 'male'}
                  onChange={() => setGender('male')}
                  className="accent-accent"
                />
                <span>男</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="gender"
                  value="female"
                  checked={gender === 'female'}
                  onChange={() => setGender('female')}
                  className="accent-accent"
                />
                <span>女</span>
              </label>
            </div>
          </div>

          {/* Submit */}
          <Button
            type="submit"
            disabled={isLoading}
            className="w-full"
          >
            {isLoading ? '排盘中...' : '生成命盘'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
});

BirthChartInput.displayName = 'BirthChartInput';
