import React, { useEffect, useState } from 'react';
import { CustomerItem, PaginationMeta, ResponseMeta } from '@/types/api';
import { getCustomers } from '@/services/apiClient';
import { PerformanceBanner } from '@/components/common/PerformanceBanner';
import { Search, ChevronLeft, ChevronRight, X, AlertCircle } from 'lucide-react';

export const CustomerDirectory: React.FC = () => {
  const [customers, setCustomers] = useState<CustomerItem[]>([]);
  const [pagination, setPagination] = useState<PaginationMeta | null>(null);
  const [meta, setMeta] = useState<ResponseMeta | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [page, setPage] = useState<number>(1);
  const [pageSize] = useState<number>(10);
  const [searchInput, setSearchInput] = useState<string>('');
  const [activeSearch, setActiveSearch] = useState<string>('');
  const [sortBy, setSortBy] = useState<string>('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const fetchCustomerList = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getCustomers({
        page,
        pageSize,
        search: activeSearch,
        sortBy,
        sortOrder,
      });
      setCustomers(response.data);
      setMeta(response.meta);
      if (response.meta.pagination) {
        setPagination(response.meta.pagination);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to retrieve customers');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCustomerList();
  }, [page, activeSearch, sortBy, sortOrder]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    setActiveSearch(searchInput);
  };

  const handleClearSearch = () => {
    setSearchInput('');
    setActiveSearch('');
    setPage(1);
  };

  const handleSortChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    setPage(1);
    if (val === 'spent_desc') {
      setSortBy('total_spent');
      setSortOrder('desc');
    } else if (val === 'orders_desc') {
      setSortBy('order_count');
      setSortOrder('desc');
    } else if (val === 'name_asc') {
      setSortBy('name');
      setSortOrder('asc');
    } else {
      setSortBy('created_at');
      setSortOrder('desc');
    }
  };

  const formatDate = (isoString: string) => {
    try {
      return new Date(isoString).toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      });
    } catch {
      return isoString;
    }
  };

  return (
    <div className="space-y-4">
      {/* Search & Sort Toolbar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
        <form onSubmit={handleSearchSubmit} className="relative w-full sm:w-80">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search by name, email, or city..."
            className="w-full rounded-lg border border-slate-200 bg-white pl-9 pr-8 py-2 text-xs text-slate-900 placeholder-slate-400 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 transition-colors"
          />
          {searchInput && (
            <button
              type="button"
              onClick={handleClearSearch}
              className="absolute right-2.5 top-2.5 text-slate-400 hover:text-slate-600"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </form>

        <div className="flex items-center gap-2 self-end sm:self-auto">
          <span className="text-xs text-slate-500">Sort by:</span>
          <select
            onChange={handleSortChange}
            defaultValue="created_desc"
            className="rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs text-slate-700 focus:border-brand-500 focus:outline-none"
          >
            <option value="created_desc">Registration (Newest)</option>
            <option value="spent_desc">Total Spend (High to Low)</option>
            <option value="orders_desc">Order Count (High to Low)</option>
            <option value="name_asc">Name (A-Z)</option>
          </select>
        </div>
      </div>

      {/* Query Performance Banner */}
      <PerformanceBanner
        meta={meta}
        queryLabel={activeSearch ? `Customer Search: "${activeSearch}"` : 'Customer Paginated Index Scan'}
      />

      {/* Error state */}
      {error && (
        <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-xs text-rose-800 flex items-start gap-2">
          <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <span className="font-semibold block">Failed to load customers</span>
            <p className="mt-0.5">{error}</p>
          </div>
          <button
            onClick={fetchCustomerList}
            className="underline font-medium hover:text-rose-900 ml-2"
          >
            Retry
          </button>
        </div>
      )}

      {/* Table & States */}
      <div className="rounded-xl border border-slate-200 bg-white overflow-hidden shadow-sm">
        {loading ? (
          <div className="p-8 space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-10 bg-slate-100 rounded animate-pulse" />
            ))}
          </div>
        ) : customers.length === 0 ? (
          <div className="p-12 text-center">
            <Search className="h-8 w-8 text-slate-300 mx-auto mb-2" />
            <h4 className="text-sm font-semibold text-slate-900">No customers found</h4>
            <p className="text-xs text-slate-500 mt-1">
              {activeSearch
                ? `No records matching "${activeSearch}". Try broadening your search.`
                : 'No customer records available in the database.'}
            </p>
            {activeSearch && (
              <button
                onClick={handleClearSearch}
                className="mt-3 text-xs font-medium text-brand-600 hover:text-brand-700 underline"
              >
                Clear Search Filter
              </button>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 text-[11px] font-semibold text-slate-500 uppercase tracking-wider bg-slate-50/50">
                  <th className="py-3 px-4">Customer ID</th>
                  <th className="py-3 px-4">Customer</th>
                  <th className="py-3 px-4">Location</th>
                  <th className="py-3 px-4 text-center">Orders</th>
                  <th className="py-3 px-4 text-right">Total Spent</th>
                  <th className="py-3 px-4 text-right">Joined</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs">
                {customers.map((c) => (
                  <tr key={c.customer_id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3 px-4 font-mono font-medium text-slate-600">{c.customer_id}</td>
                    <td className="py-3 px-4">
                      <div className="font-semibold text-slate-900">{c.name}</div>
                      <div className="text-[11px] text-slate-400">{c.email}</div>
                    </td>
                    <td className="py-3 px-4 text-slate-600">
                      <div>{c.city}, {c.country}</div>
                      <span className="text-[10px] text-slate-400 uppercase tracking-wider">{c.region}</span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className="inline-block px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 font-semibold font-mono text-[11px]">
                        {c.order_count}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right font-semibold text-slate-900 font-mono">
                      ${c.total_spent.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </td>
                    <td className="py-3 px-4 text-right text-slate-500 whitespace-nowrap">
                      {formatDate(c.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Bar */}
        {pagination && pagination.total_items > 0 && (
          <div className="border-t border-slate-200 bg-slate-50/50 px-4 py-3 flex items-center justify-between text-xs text-slate-600">
            <div>
              Showing <span className="font-semibold font-mono">{(pagination.page - 1) * pagination.page_size + 1}</span> to{' '}
              <span className="font-semibold font-mono">
                {Math.min(pagination.page * pagination.page_size, pagination.total_items)}
              </span>{' '}
              of <span className="font-semibold font-mono">{pagination.total_items.toLocaleString()}</span> customers
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1 || loading}
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronLeft className="h-3.5 w-3.5" /> Prev
              </button>
              <span className="font-mono text-xs px-2">
                {pagination.page} / {pagination.total_pages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(pagination.total_pages, p + 1))}
                disabled={page >= pagination.total_pages || loading}
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                Next <ChevronRight className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
