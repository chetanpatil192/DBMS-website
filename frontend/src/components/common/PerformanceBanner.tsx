import React, { useState } from 'react';
import { Database, Server, Clock, ChevronDown, ChevronUp, Layers, CheckCircle } from 'lucide-react';
import { ResponseMeta } from '@/types/api';

interface PerformanceBannerProps {
  meta: ResponseMeta | null;
  queryLabel: string;
}

export const PerformanceBanner: React.FC<PerformanceBannerProps> = ({ meta, queryLabel }) => {
  const [expanded, setExpanded] = useState<boolean>(false);

  if (!meta) return null;

  const dbTime = meta.db_execution_time_ms ?? meta.execution_time_ms ?? 0;
  const apiOverhead = meta.api_overhead_ms ?? 0;
  const totalTime = meta.execution_time_ms ?? dbTime;
  const diag = meta.query_diagnostics;

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Title and context */}
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-100">
            <Database className="h-4 w-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-800">
                DBMS Read Performance Instrumentation
              </span>
              <span className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-mono text-slate-600">
                {queryLabel}
              </span>
            </div>
            <p className="text-[11px] text-slate-500 mt-0.5">
              Live measurement distinguishing MongoDB storage engine execution from web API serialization overhead.
            </p>
          </div>
        </div>

        {/* Latency Chips */}
        <div className="flex flex-wrap items-center gap-2">
          {/* DB Engine Time */}
          <div className="flex items-center gap-1.5 rounded-lg border border-emerald-200 bg-emerald-50/70 px-3 py-1.5 text-xs text-emerald-900 font-medium">
            <Database className="h-3.5 w-3.5 text-emerald-600" />
            <span className="text-[11px] text-emerald-700">MongoDB Query:</span>
            <span className="font-mono font-bold">{dbTime} ms</span>
          </div>

          {/* API Overhead */}
          <div className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs text-slate-800 font-medium">
            <Server className="h-3.5 w-3.5 text-slate-500" />
            <span className="text-[11px] text-slate-500">API Overhead:</span>
            <span className="font-mono font-semibold">{apiOverhead} ms</span>
          </div>

          {/* Total Time */}
          <div className="flex items-center gap-1.5 rounded-lg border border-indigo-200 bg-indigo-50/70 px-3 py-1.5 text-xs text-indigo-900 font-medium">
            <Clock className="h-3.5 w-3.5 text-indigo-600" />
            <span className="text-[11px] text-indigo-700">Total API:</span>
            <span className="font-mono font-bold">{totalTime} ms</span>
          </div>

          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-1 rounded-lg border border-slate-200 px-2.5 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-50 transition-colors"
          >
            DBMS Details {expanded ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
          </button>
        </div>
      </div>

      {/* Expanded Demo Architecture Insights */}
      {expanded && (
        <div className="mt-4 pt-4 border-t border-slate-100 grid grid-cols-1 md:grid-cols-3 gap-4 text-xs text-slate-600 bg-slate-50/60 p-3 rounded-lg">
          <div className="space-y-1">
            <span className="font-semibold text-slate-800 flex items-center gap-1.5">
              <Layers className="h-3.5 w-3.5 text-brand-600" /> Dataset Scale
            </span>
            <p className="text-slate-500">
              Evaluated over <strong className="text-slate-800">50,000 documents</strong> (44k orders, 5k customers, 1k products).
            </p>
          </div>

          <div className="space-y-1">
            <span className="font-semibold text-slate-800 flex items-center gap-1.5">
              <CheckCircle className="h-3.5 w-3.5 text-emerald-600" /> Indexing Strategy
            </span>
            <p className="text-slate-500 font-mono text-[11px]">
              {diag?.indexes_leveraged
                ? diag.indexes_leveraged.join(', ')
                : diag?.index_leveraged || 'Compound ESR Index'}
            </p>
          </div>

          <div className="space-y-1">
            <span className="font-semibold text-slate-800 flex items-center gap-1.5">
              <Database className="h-3.5 w-3.5 text-indigo-600" /> Pipeline Architecture
            </span>
            <p className="text-slate-500">
              Aggregated directly in MongoDB memory with `$match` pruning to prevent full collection scans (`COLLSCAN`).
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
