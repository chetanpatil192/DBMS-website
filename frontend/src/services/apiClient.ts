/**
 * Type-safe HTTP client for interacting with Commerce Insights FastAPI backend.
 */

import {
  CustomerItem,
  DashboardMetrics,
  ErrorEnvelope,
  HealthCheckResponse,
  ResponseEnvelope,
} from '@/types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export class ApiClientError extends Error {
  public readonly code: string;
  public readonly status: number;
  public readonly details?: Record<string, unknown>;

  constructor(message: string, code: string, status: number, details?: Record<string, unknown>) {
    super(message);
    this.name = 'ApiClientError';
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

interface RequestOptions extends RequestInit {
  timeoutMs?: number;
}

export async function fetchApi<T>(endpoint: string, options: RequestOptions = {}): Promise<ResponseEnvelope<T>> {
  const { timeoutMs = 15000, ...fetchOptions } = options;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  const targetUrl = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${cleanEndpoint}`;

  try {
    const response = await fetch(targetUrl, {
      ...fetchOptions,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...fetchOptions.headers,
      },
    });

    clearTimeout(timeoutId);

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      if (data && 'error' in data) {
        const errorEnv = data as ErrorEnvelope;
        throw new ApiClientError(
          errorEnv.error.message || 'API request failed',
          errorEnv.error.code || 'HTTP_ERROR',
          response.status,
          errorEnv.error.details,
        );
      }
      throw new ApiClientError(
        response.statusText || 'Unexpected server error',
        'HTTP_ERROR',
        response.status,
      );
    }

    return data as ResponseEnvelope<T>;
  } catch (error: unknown) {
    clearTimeout(timeoutId);

    if (error instanceof ApiClientError) {
      throw error;
    }

    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new ApiClientError(
        `Request to '${targetUrl}' timed out after ${timeoutMs}ms`,
        'REQUEST_TIMEOUT',
        408,
      );
    }

    const message = error instanceof Error ? error.message : 'Network request failed';
    throw new ApiClientError(
      message,
      'NETWORK_FAILURE',
      0,
    );
  }
}

/**
 * Diagnostic helper to query the backend health endpoint.
 */
export async function getSystemHealth(): Promise<ResponseEnvelope<HealthCheckResponse>> {
  return fetchApi<HealthCheckResponse>('/health');
}

/**
 * Queries real-time dashboard metrics (KPIs, recent orders, sales trend, category performance).
 */
export async function getDashboardMetrics(): Promise<ResponseEnvelope<DashboardMetrics>> {
  return fetchApi<DashboardMetrics>('/analytics/dashboard');
}

/**
 * Queries paginated customers with search and sorting.
 */
export interface CustomerQueryParams {
  page?: number;
  pageSize?: number;
  search?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export async function getCustomers(params: CustomerQueryParams = {}): Promise<ResponseEnvelope<CustomerItem[]>> {
  const query = new URLSearchParams();
  if (params.page) query.set('page', params.page.toString());
  if (params.pageSize) query.set('page_size', params.pageSize.toString());
  if (params.search && params.search.trim()) query.set('search', params.search.trim());
  if (params.sortBy) query.set('sort_by', params.sortBy);
  if (params.sortOrder) query.set('sort_order', params.sortOrder);

  const queryString = query.toString();
  const endpoint = queryString ? `/customers?${queryString}` : '/customers';
  return fetchApi<CustomerItem[]>(endpoint);
}
