import React from 'react';
import { OrderSummary } from '@/types/api';
import { Badge, BadgeVariant } from '@/components/common/Badge';

interface RecentOrdersTableProps {
  orders: OrderSummary[];
}

const statusVariantMap: Record<string, BadgeVariant> = {
  completed: 'success',
  shipped: 'info',
  pending: 'warning',
  cancelled: 'danger',
};

export const RecentOrdersTable: React.FC<RecentOrdersTableProps> = ({ orders }) => {
  if (!orders || orders.length === 0) {
    return (
      <div className="p-8 text-center text-sm text-slate-500">
        No recent orders recorded in the database.
      </div>
    );
  }

  const formatDate = (isoString: string) => {
    try {
      const d = new Date(isoString);
      return d.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return isoString;
    }
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b border-slate-200 text-[11px] font-semibold text-slate-500 uppercase tracking-wider bg-slate-50/50">
            <th className="py-3 px-4">Order ID</th>
            <th className="py-3 px-4">Customer</th>
            <th className="py-3 px-4">Date</th>
            <th className="py-3 px-4">Items</th>
            <th className="py-3 px-4">Total</th>
            <th className="py-3 px-4">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 text-xs">
          {orders.map((ord) => (
            <tr key={ord.order_id} className="hover:bg-slate-50/70 transition-colors">
              <td className="py-3 px-4 font-mono font-medium text-slate-700">{ord.order_id}</td>
              <td className="py-3 px-4">
                <div className="font-medium text-slate-900">{ord.customer_name}</div>
                <div className="text-[11px] text-slate-400">{ord.customer_email}</div>
              </td>
              <td className="py-3 px-4 text-slate-500 whitespace-nowrap">{formatDate(ord.order_date)}</td>
              <td className="py-3 px-4 text-slate-600">{ord.items_count} item{ord.items_count > 1 ? 's' : ''}</td>
              <td className="py-3 px-4 font-semibold text-slate-900 font-mono">
                ${ord.total_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
              </td>
              <td className="py-3 px-4">
                <Badge variant={statusVariantMap[ord.status] || 'neutral'} size="sm" dot>
                  {ord.status}
                </Badge>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
