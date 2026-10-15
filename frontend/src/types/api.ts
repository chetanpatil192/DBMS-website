/**
 * TypeScript contracts mirroring backend API schemas and response envelopes.
 */

export interface PaginationMeta {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
}

export interface QueryProfiling {
  stage?: string;
  index_name?: string;
  docs_examined?: number;
  keys_examined?: number;
  in_memory_sort?: boolean;
  [key: string]: unknown;
}

export interface QueryDiagnostics {
  target_collections?: string[];
  collection?: string;
  orders_aggregated?: number;
  customers_counted?: number;
  indexes_leveraged?: string[];
  index_leveraged?: string;
  matched_documents?: number;
  search_filter_applied?: boolean;
  db_engine_time_ms?: number;
  [key: string]: unknown;
}

export interface ResponseMeta {
  timestamp: string;
  execution_time_ms?: number;
  db_execution_time_ms?: number;
  api_overhead_ms?: number;
  query_diagnostics?: QueryDiagnostics;
  pagination?: PaginationMeta;
  profiling?: QueryProfiling;
}

export interface ResponseEnvelope<T> {
  data: T;
  meta: ResponseMeta;
}

export interface ErrorDetail {
  code: string;
  message: string;
  details?: Record<string, unknown>;
  timestamp: string;
}

export interface ErrorEnvelope {
  error: ErrorDetail;
}

export interface DatabaseHealth {
  connected: boolean;
  latency_ms: number;
  database?: string;
  error?: string;
}

export interface HealthCheckResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  service: string;
  version: string;
  environment: string;
  database: DatabaseHealth;
}

export interface OrderSummary {
  order_id: string;
  customer_id: string;
  customer_name: string;
  customer_email: string;
  region: string;
  order_date: string;
  status: string;
  payment_method: string;
  total_amount: number;
  items_count: number;
}

export interface SalesPoint {
  period: string;
  revenue: number;
  orders_count: number;
}

export interface CategoryPerformance {
  category: string;
  revenue: number;
  orders_count: number;
}

export interface DashboardMetrics {
  total_customers: number;
  total_orders: number;
  total_revenue: number;
  average_order_value: number;
  recent_orders: OrderSummary[];
  sales_trend: SalesPoint[];
  category_performance: CategoryPerformance[];
}

export interface CustomerItem {
  customer_id: string;
  name: string;
  email: string;
  phone?: string;
  city: string;
  country: string;
  region: string;
  total_spent: number;
  order_count: number;
  created_at: string;
}
