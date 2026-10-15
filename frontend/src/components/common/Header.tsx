import React from 'react';
import { Database, Activity } from 'lucide-react';
import { Badge } from './Badge';

interface HeaderProps {
  status: 'loading' | 'healthy' | 'degraded' | 'offline';
  latencyMs?: number;
}

export const Header: React.FC<HeaderProps> = ({ status, latencyMs }) => {
  const getStatusBadge = () => {
    switch (status) {
      case 'healthy':
        return (
          <Badge variant="success" dot>
            Backend & DB Active {latencyMs !== undefined && `(${latencyMs}ms)`}
          </Badge>
        );
      case 'degraded':
        return (
          <Badge variant="warning" dot>
            Database Degraded
          </Badge>
        );
      case 'offline':
        return (
          <Badge variant="danger" dot>
            Backend Offline
          </Badge>
        );
      case 'loading':
      default:
        return (
          <Badge variant="neutral" dot>
            Checking Connectivity...
          </Badge>
        );
    }
  };

  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-700 text-white shadow-sm">
              <Database className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-lg font-bold tracking-tight text-slate-900">Commerce Insights</span>
                <span className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-slate-600">
                  Phase 1 Foundation
                </span>
              </div>
              <p className="text-xs text-slate-500">
                Database Read Performance & Analytical Query Optimization Platform
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-slate-400" />
              {getStatusBadge()}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
