import React from 'react';
import { SalesPoint } from '@/types/api';
import { TrendingUp } from 'lucide-react';

interface SalesChartProps {
  data: SalesPoint[];
}

export const SalesChart: React.FC<SalesChartProps> = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center text-slate-400">
        <TrendingUp className="h-8 w-8 mb-2 opacity-50" />
        <p className="text-sm">No sales trend data available</p>
      </div>
    );
  }

  const maxRevenue = Math.max(...data.map((d) => d.revenue), 1);

  const formatCurrency = (val: number) => {
    if (val >= 1_000_000) return `$${(val / 1_000_000).toFixed(1)}M`;
    if (val >= 1_000) return `$${(val / 1_000).toFixed(0)}k`;
    return `$${val.toFixed(0)}`;
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between text-xs text-slate-500">
        <span>Monthly Gross Sales (Real Aggregated Database Results)</span>
        <span className="font-mono">Peak: {formatCurrency(maxRevenue)}</span>
      </div>

      <div className="h-56 flex items-end gap-3 pt-6 pb-2 border-b border-slate-100">
        {data.map((point) => {
          const heightPercent = Math.max(Math.round((point.revenue / maxRevenue) * 100), 8);
          return (
            <div key={point.period} className="flex-1 flex flex-col items-center gap-2 group h-full justify-end">
              {/* Tooltip value */}
              <div className="opacity-0 group-hover:opacity-100 transition-opacity bg-slate-900 text-white text-[10px] rounded px-1.5 py-0.5 whitespace-nowrap pointer-events-none mb-1 font-mono">
                ${point.revenue.toLocaleString()} ({point.orders_count.toLocaleString()} orders)
              </div>

              {/* Bar */}
              <div
                style={{ height: `${heightPercent}%` }}
                className="w-full rounded-t-md bg-brand-500 group-hover:bg-brand-600 transition-all duration-300 relative"
              />

              {/* Label */}
              <span className="text-[11px] font-medium text-slate-500 whitespace-nowrap mt-1">
                {point.period}
              </span>
            </div>
          );
        })}
      </div>

      <div className="flex items-center justify-between text-xs text-slate-400 pt-1">
        <span>Aggregated by MongoDB $dateToString pipeline</span>
        <span>{data.reduce((acc, p) => acc + p.orders_count, 0).toLocaleString()} Total Orders in Trend</span>
      </div>
    </div>
  );
};
