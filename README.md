# Commerce Insights

> **A Full-Stack E-Commerce Analytics Platform Engineered for Database Read Performance & Query Optimization**
> *Developed for DBMS College Project Demonstration*

---

## 1. Project Overview & DBMS Concepts

**Commerce Insights** is an e-commerce analytics web platform designed to evaluate and demonstrate read performance, aggregation pipelines, and compound indexing strategies on **MongoDB** under a realistic **50,000-document dataset**.

### Key DBMS Principles Evaluated:
1. **Document Embedding vs. Relational Normalization**:
   - Order line items are embedded directly inside order documents, eliminating expensive relational multi-table `$lookup` JOIN operations for order summaries.
2. **Compound Index Optimization (The ESR Rule)**:
   - Indexes adhere to the **Equality, Sort, Range** design rule (e.g., `idx_order_status_date` indexing `{ status: 1, order_date: -1 }`), preventing full collection scans (`COLLSCAN`).
3. **Database-Side Aggregation Pipelines**:
   - Multi-stage pipelines (`$match` -> `$unwind` -> `$group` -> `$sort`) compute gross revenue, average order value (AOV), and monthly sales trends entirely within the database engine.
4. **Latency Decomposition**:
   - Every API response explicitly measures and distinguishes **MongoDB Database Engine Time** from **FastAPI Web Routing & Serialization Overhead**.

---

## 2. Technology Stack

- **Frontend**: React 18, TypeScript (Strict Mode), Vite, Tailwind CSS, Lucide Icons
- **Backend**: Python 3.11+, FastAPI, Pydantic v2, Uvicorn
- **Database**: MongoDB 8.0+
- **Database Driver**: PyMongo (with connection pooling)
- **Data Generation**: Faker (Deterministic, repeatable seed)
- **Testing**: Pytest (Backend), Vitest & React Testing Library (Frontend)

---

## 3. Database Schema & Index Design

### Collections & Counts (50,000 Total Documents)
| Collection | Document Count | Document Structure Highlights |
| :--- | :--- | :--- |
| **`customers`** | **5,000** | `customer_id`, `name`, `email`, `city`, `country`, `region`, `total_spent`, `order_count`, `created_at` |
| **`products`** | **1,000** | `product_id`, `sku`, `name`, `category`, `subcategory`, `price`, `stock_quantity` |
| **`orders`** | **44,000** | `order_id`, `customer_id`, `customer_name`, `customer_email`, `region`, `order_date`, `status`, `payment_method`, `total_amount`, `items: [{ product_id, name, category, quantity, unit_price, subtotal }]` |

### MongoDB Indexes
- `orders`:
  - `idx_order_id`: `{ order_id: 1 }` (Unique)
  - `idx_order_status_date`: `{ status: 1, order_date: -1 }` *(Compound index for revenue and monthly sales trend aggregation)*
  - `idx_order_date_desc`: `{ order_date: -1 }` *(Enables sub-5ms retrieval of recent transactions without in-memory sorting)*
- `customers`:
  - `idx_cust_id`: `{ customer_id: 1 }` (Unique)
  - `idx_cust_text_search`: `{ name: "text", email: "text" }` *(Fast full-text search across 5,000 records)*
  - `idx_cust_created`: `{ created_at: -1 }`
  - `idx_cust_spent`: `{ total_spent: -1 }`

---

## 4. Quick Setup & Run Guide

### Prerequisites
- Python `>= 3.11`
- Node.js `>= 20.x`
- Local MongoDB running on `localhost:27017`

### Step 1: Environment Setup
```bash
cp .env.example .env
cp .env.example backend/.env
cp .env.example frontend/.env
```

### Step 2: Seed the 50,000-Document Dataset
```bash
# Using the backend virtual environment
backend/.venv/bin/python scripts/seed_data.py
```
*Generates and seeds 50,000 documents into MongoDB and builds all indexes in ~4.7 seconds.*

### Step 3: Run the Application
The backend and frontend run concurrently on standard local ports:

```bash
# Terminal 1: FastAPI Backend (Port 8000)
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2: React Frontend (Port 5173)
cd frontend
npm run dev
```

Open your browser at **`http://localhost:5173`**.

---

## 5. Primary API Endpoints

All responses conform to the standard `ResponseEnvelope[T]` with detailed performance metadata:

| Endpoint | Method | Purpose | Sample Latency |
| :--- | :--- | :--- | :--- |
| **`/api/v1/health`** | `GET` | Health status and MongoDB ping latency | ~1.0 ms |
| **`/api/v1/analytics/dashboard`** | `GET` | Aggregated revenue, AOV, sales trend, recent orders | ~200 ms (aggregates 44k docs) |
| **`/api/v1/customers`** | `GET` | Paginated customer directory with search (`?search=...`) | ~12 ms (indexed scan) |
| **`/api/v1/docs`** | `GET` | Interactive Swagger / OpenAPI documentation | - |

### Response Envelope Format
```json
{
  "data": { ... },
  "meta": {
    "timestamp": "2026-10-15T12:30:28Z",
    "execution_time_ms": 201.34,
    "db_execution_time_ms": 201.25,
    "api_overhead_ms": 0.09,
    "query_diagnostics": {
      "orders_aggregated": 44000,
      "indexes_leveraged": ["idx_order_status_date", "idx_order_date_desc"],
      "db_engine_time_ms": 201.25
    }
  }
}
```

---

## 6. College Project Demonstration Walkthrough

When presenting this project to an evaluator or professor, follow these 5 steps:

1. **Show the System Health Indicator**:
   - Point to the live badge in the top navigation bar showing `Backend & DB Active (1.0ms)`. Explain that this is a real round-trip TCP ping against MongoDB.
2. **Present the Aggregated Analytics Dashboard**:
   - Highlight that the **Gross Revenue ($46.2M)**, **Total Orders (44,000)**, and **AOV ($1,264.29)** are calculated via multi-stage aggregation pipelines and not hardcoded.
   - Explain the **Monthly Revenue Trend Bar Chart**: The database dynamically grouped 44,000 orders using `$dateToString` format `%Y-%m`.
3. **Demonstrate the DBMS Read Performance Instrumentation Banner**:
   - Click **"DBMS Details"** on the performance banner.
   - Explain the latency breakdown: **MongoDB Query Time** (e.g. `201 ms`) vs. **API Overhead** (e.g. `0.1 ms`).
   - Mention the compound index `idx_order_status_date` that enabled the pipeline to skip cancelled orders without scanning all records.
4. **Demonstrate Customer Search & Pagination**:
   - Switch to the **"Customer Search & Directory"** tab.
   - Type a query like `"Smith"` or `"Miller"`.
   - Point out that search results are returned in **~12 ms** across 5,000 customer records due to the text index `idx_cust_text_search`.
   - Toggle sorting (e.g., "Total Spend: High to Low") to demonstrate indexed sorting on `total_spent: -1`.
5. **Show Automated Test Verification**:
   - Run backend tests: `cd backend && .venv/bin/pytest` (5 passed in 0.07s).
   - Run frontend tests: `cd frontend && npm test` (3 passed in 1.0s).
