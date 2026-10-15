import React from 'react';
import { CategoryPerformance } from '@/types/api';

interface CategoryBreakdownProps {
  categories: CategoryPerformance[];
}

export const CategoryBreakdown: React.FC<CategoryBreakdownProps> = ({ categories }) => {
  if (!categories || categories.length === 0) {
    return <div className="p-4 text-xs text-slate-400">No category metrics available.</div>;
  }

  const totalCatRevenue = categories.reduce((sum, c) => sum + c.revenue, 0);

  return (
    <div className="space-y-3">
      {categories.map((cat) => {
        const percentage = totalCatRevenue > 0 ? Math.round((cat.revenue / totalCatRevenue) * 100) : 0;
        return (
          <div key={cat.category} className="space-y-1">
            <div className="flex justify-between text-xs">
              <span className="font-medium text-slate-700">{cat.category}</span>
              <span className="font-mono text-slate-900 font-semibold">
                ${cat.revenue.toLocaleString(undefined, { maximumFractionDigits: 0 })}{' '}
                <span className="text-slate-400 font-normal">({percentage}%)</span>
              </span>
            </div>
            <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
              <div
                style={{ width: `${percentage}%` }}
                className="h-full bg-brand-600 rounded-full transition-all duration-500"
              />
            </div>
          </div>
        );
      })}
    </div>
  );
};
