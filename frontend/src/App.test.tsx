import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { App } from './App';

// Mock apiClient calls
vi.mock('@/services/apiClient', () => ({
  getSystemHealth: vi.fn().mockResolvedValue({
    data: {
      status: 'healthy',
      service: 'Commerce Insights Test API',
      version: '0.1.0',
      environment: 'testing',
      database: {
        connected: true,
        latency_ms: 1.2,
        database: 'commerce_insights',
      },
    },
    meta: {
      timestamp: '2026-10-15T12:00:00Z',
      execution_time_ms: 2.1,
    },
  }),
  getDashboardMetrics: vi.fn().mockResolvedValue({
    data: {
      total_customers: 5000,
      total_orders: 44000,
      total_revenue: 46242837.62,
      average_order_value: 1264.29,
      recent_orders: [
        {
          order_id: 'ord_00000001',
          customer_id: 'cust_000001',
          customer_name: 'Jane Doe',
          customer_email: 'jane@example.com',
          region: 'North America',
          order_date: '2026-10-15T10:00:00Z',
          status: 'completed',
          payment_method: 'credit_card',
          total_amount: 250.0,
          items_count: 2,
        },
      ],
      sales_trend: [
        {
          period: '2026-05',
          revenue: 7500000.0,
          orders_count: 7000,
        },
      ],
      category_performance: [
        {
          category: 'Electronics',
          revenue: 9800000.0,
          orders_count: 18000,
        },
      ],
    },
    meta: {
      timestamp: '2026-10-15T12:00:00Z',
      execution_time_ms: 45.2,
    },
  }),
  getCustomers: vi.fn().mockResolvedValue({
    data: [],
    meta: {
      timestamp: '2026-10-15T12:00:00Z',
      execution_time_ms: 10.0,
      pagination: {
        page: 1,
        page_size: 10,
        total_items: 0,
        total_pages: 0,
      },
    },
  }),
}));

describe('Commerce Insights App', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders application branding and header', async () => {
    render(<App />);
    expect(screen.getByText('Commerce Insights')).toBeInTheDocument();
    expect(await screen.findByText(/Backend & DB Active/i)).toBeInTheDocument();
  });

  it('renders real dashboard KPI metrics from the API', async () => {
    render(<App />);
    expect(await screen.findByText('5,000')).toBeInTheDocument();
    expect(screen.getByText('44,000')).toBeInTheDocument();
    expect(screen.getByText('$46,242,837.62')).toBeInTheDocument();
    expect(screen.getByText('$1,264.29')).toBeInTheDocument();
  });

  it('renders sales trend chart and recent orders table', async () => {
    render(<App />);
    expect(await screen.findByText('Monthly Revenue Trend')).toBeInTheDocument();
    expect(screen.getByText('Recent Orders')).toBeInTheDocument();
    expect(screen.getByText('Jane Doe')).toBeInTheDocument();
    expect(screen.getByText('ord_00000001')).toBeInTheDocument();
  });
});
