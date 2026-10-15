import React, { useEffect, useState } from 'react';
import {
  Users,
  ShoppingCart,
  DollarSign,
  TrendingUp,
  RefreshCw,
  AlertCircle,
  LayoutDashboard,
  UserCheck,
  BookOpen,
  Info,
} from 'lucide-react';
import { Header } from '@/components/common/Header';
import { Card } from '@/components/common/Card';
import { PerformanceBanner } from '@/components/common/PerformanceBanner';
import { StatCard } from '@/components/dashboard/StatCard';
import { SalesChart } from '@/components/dashboard/SalesChart';
import { RecentOrdersTable } from '@/components/dashboard/RecentOrdersTable';
import { CategoryBreakdown } from '@/components/dashboard/CategoryBreakdown';
import { CustomerDirectory } from '@/components/customers/CustomerDirectory';
import { getDashboardMetrics, getSystemHealth } from '@/services/apiClient';
import { DashboardMetrics, HealthCheckResponse, ResponseMeta } from '@/types/api';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'customers' | 'architecture'>('dashboard');
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [metricsMeta, setMetricsMeta] = useState<ResponseMeta | null>(null);
  const [health, setHealth] = useState<HealthCheckResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [healthRes, metricsRes] = await Promise.all([
        getSystemHealth().catch(() => null),
        getDashboardMetrics(),
      ]);

      if (healthRes) {
        setHealth(healthRes.data);
      }
      setMetrics(metricsRes.data);
      setMetricsMeta(metricsRes.meta);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Unable to connect to analytics API');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const connectionStatus = health?.database.connected
    ? 'healthy'
    : health
    ? 'degraded'
    : loading
    ? 'loading'
    : 'offline';

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-900">
      <Header
        status={connectionStatus}
        latencyMs={health?.database.latency_ms}
      />

      {/* Navigation Sub-header */}
      <div className="border-b border-slate-200 bg-white sticky top-0 z-10 shadow-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between">
          <nav className="flex space-x-6">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`flex items-center gap-2 py-3.5 text-xs font-semibold border-b-2 transition-colors ${
                activeTab === 'dashboard'
                  ? 'border-brand-600 text-brand-700'
                  : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              <LayoutDashboard className="h-4 w-4" />
              Analytics Dashboard
            </button>
            <button
              onClick={() => setActiveTab('customers')}
              className={`flex items-center gap-2 py-3.5 text-xs font-semibold border-b-2 transition-colors ${
                activeTab === 'customers'
                  ? 'border-brand-600 text-brand-700'
                  : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              <UserCheck className="h-4 w-4" />
              Customer Search & Directory
            </button>
            <button
              onClick={() => setActiveTab('architecture')}
              className={`flex items-center gap-2 py-3.5 text-xs font-semibold border-b-2 transition-colors ${
                activeTab === 'architecture'
                  ? 'border-brand-600 text-brand-700'
                  : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              <BookOpen className="h-4 w-4" />
              DBMS Architecture & Demo Notes
            </button>
          </nav>

          <div className="flex items-center gap-3">
            <button
              onClick={loadData}
              disabled={loading}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-200 rounded-md hover:bg-slate-50 disabled:opacity-50 transition-colors shadow-sm"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
              Refresh Data
            </button>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Error State Banner */}
        {error && (
          <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-xs text-rose-800 flex items-start justify-between">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-rose-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-sm">Database Analytics Unavailable</h4>
                <p className="mt-1">{error}</p>
                <p className="mt-1 text-slate-600">
                  Ensure MongoDB is running locally on port 27017 and the FastAPI backend service is active.
                </p>
              </div>
            </div>
            <button
              onClick={loadData}
              className="px-3 py-1.5 bg-rose-600 text-white rounded font-medium hover:bg-rose-700 transition-colors"
            >
              Retry
            </button>
          </div>
        )}

        {/* Tab 1: Dashboard Overview */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            {/* Live Performance Diagnostic Banner */}
            <PerformanceBanner
              meta={metricsMeta}
              queryLabel="Aggregated Analytical Dashboard (Multi-Collection Pipeline)"
            />

            {/* KPI Cards Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <StatCard
                title="Total Customers"
                value={loading ? '...' : (metrics?.total_customers.toLocaleString() ?? '0')}
                subtitle="5,000 synthetic indexed records"
                icon={<Users className="h-5 w-5 text-sky-600" />}
                iconBg="bg-sky-50"
              />
              <StatCard
                title="Total Orders"
                value={loading ? '...' : (metrics?.total_orders.toLocaleString() ?? '0')}
                subtitle="44,000 transaction documents"
                icon={<ShoppingCart className="h-5 w-5 text-indigo-600" />}
                iconBg="bg-indigo-50"
              />
              <StatCard
                title="Gross Revenue"
                value={
                  loading
                    ? '...'
                    : `$${metrics?.total_revenue.toLocaleString(undefined, {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      }) ?? '0.00'}`
                }
                subtitle="Calculated via MongoDB $group pipeline"
                icon={<DollarSign className="h-5 w-5 text-emerald-600" />}
                iconBg="bg-emerald-50"
              />
              <StatCard
                title="Average Order Value"
                value={
                  loading
                    ? '...'
                    : `$${metrics?.average_order_value.toLocaleString(undefined, {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      }) ?? '0.00'}`
                }
                subtitle="Mean basket size across orders"
                icon={<TrendingUp className="h-5 w-5 text-amber-600" />}
                iconBg="bg-amber-50"
              />
            </div>

            {/* Middle Section: Sales Trend & Category Breakdown */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <Card
                  title="Monthly Revenue Trend"
                  subtitle="MongoDB $dateToString pipeline grouping 44,000 orders into monthly buckets"
                >
                  {loading ? (
                    <div className="h-56 flex items-center justify-center text-xs text-slate-400">
                      Loading sales aggregation from database...
                    </div>
                  ) : (
                    <SalesChart data={metrics?.sales_trend || []} />
                  )}
                </Card>
              </div>

              <div>
                <Card
                  title="Revenue by Category"
                  subtitle="Top categories computed via $unwind on embedded items"
                >
                  {loading ? (
                    <div className="h-56 flex items-center justify-center text-xs text-slate-400">
                      Calculating category breakdown...
                    </div>
                  ) : (
                    <CategoryBreakdown categories={metrics?.category_performance || []} />
                  )}
                </Card>
              </div>
            </div>

            {/* Bottom Section: Recent Orders Table */}
            <Card
              title="Recent Orders"
              subtitle="Latest transactions retrieved via index scan on order_date DESC"
            >
              {loading ? (
                <div className="p-8 text-center text-xs text-slate-400">
                  Retrieving recent records from orders collection...
                </div>
              ) : (
                <RecentOrdersTable orders={metrics?.recent_orders || []} />
              )}
            </Card>
          </div>
        )}

        {/* Tab 2: Customer Directory */}
        {activeTab === 'customers' && (
          <div className="space-y-4">
            <CustomerDirectory />
          </div>
        )}

        {/* Tab 3: DBMS Architecture & Demo Guide */}
        {activeTab === 'architecture' && (
          <div className="space-y-6">
            <Card
              title="DBMS College Project Demonstration Guide"
              subtitle="Key architectural decisions, query optimization techniques, and presentation talking points"
            >
              <div className="space-y-6 text-sm text-slate-700 leading-relaxed">
                {/* Section 1 */}
                <div>
                  <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                    <Info className="h-4 w-4 text-brand-600" />
                    1. High-Volume Document Model (50,000 Records)
                  </h4>
                  <p className="mt-1 text-xs text-slate-600">
                    Unlike traditional relational databases that require foreign key joins across order, customer, and order-item tables,
                    Commerce Insights leverages MongoDB document embedding. Line items are directly embedded inside order documents, allowing single-read retrieval of complete orders without relational joins.
                  </p>
                  <div className="mt-2 grid grid-cols-3 gap-3 text-xs font-mono bg-slate-50 p-3 rounded-lg border border-slate-200">
                    <div><strong>customers:</strong> 5,000 docs</div>
                    <div><strong>products:</strong> 1,000 docs</div>
                    <div><strong>orders:</strong> 44,000 docs</div>
                  </div>
                </div>

                {/* Section 2 */}
                <div>
                  <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                    <Info className="h-4 w-4 text-brand-600" />
                    2. Query Optimization & Indexing Strategy
                  </h4>
                  <p className="mt-1 text-xs text-slate-600">
                    To demonstrate read performance, specific compound and specialized indexes were constructed:
                  </p>
                  <ul className="mt-2 list-disc list-inside space-y-1 text-xs text-slate-600">
                    <li>
                      <code className="bg-slate-100 px-1 py-0.5 rounded font-mono text-slate-800">idx_order_status_date (status: 1, order_date: -1)</code>:
                      Compound index following the ESR rule (Equality on status, Sort on order_date). Avoids collection scans (`COLLSCAN`) during revenue aggregation.
                    </li>
                    <li>
                      <code className="bg-slate-100 px-1 py-0.5 rounded font-mono text-slate-800">idx_cust_text_search (name: text, email: text)</code>:
                      Compound text index enabling sub-50ms search across 5,000 customer profiles.
                    </li>
                    <li>
                      <code className="bg-slate-100 px-1 py-0.5 rounded font-mono text-slate-800">idx_order_date_desc (order_date: -1)</code>:
                      Ensures the recent transactions query executes in &lt; 5ms without requiring an in-memory sort buffer.
                    </li>
                  </ul>
                </div>

                {/* Section 3 */}
                <div>
                  <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                    <Info className="h-4 w-4 text-brand-600" />
                    3. Server-Side Aggregation Pipelines
                  </h4>
                  <p className="mt-1 text-xs text-slate-600">
                    All analytics (gross revenue, category breakdown, monthly trends) are computed entirely on the MongoDB database engine using multi-stage aggregation pipelines:
                  </p>
                  <pre className="mt-2 p-3 bg-slate-900 text-slate-200 rounded-lg text-xs font-mono overflow-x-auto">
{`# Monthly Trend Aggregation Pipeline
[
  { "$match": { "status": { "$ne": "cancelled" } } },
  { "$group": {
      "_id": { "$dateToString": { "format": "%Y-%m", "date": "$order_date" } },
      "revenue": { "$sum": "$total_amount" },
      "orders_count": { "$sum": 1 }
  }},
  { "$sort": { "_id": 1 } }
]`}
                  </pre>
                </div>

                {/* Section 4 */}
                <div>
                  <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                    <Info className="h-4 w-4 text-brand-600" />
                    4. Latency Breakdown Architecture
                  </h4>
                  <p className="mt-1 text-xs text-slate-600">
                    The platform explicitly measures and separates <strong>MongoDB database engine execution time</strong> from <strong>FastAPI server routing and Pydantic serialization overhead</strong>, proving that the database query executes in milliseconds.
                  </p>
                </div>
              </div>
            </Card>
          </div>
        )}
      </main>
    </div>
  );
};
