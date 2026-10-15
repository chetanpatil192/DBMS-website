# Database Guidelines & Local MongoDB Setup: Commerce Insights

## 1. Supported MongoDB Versions & Environment Requirements

- **Recommended Version**: MongoDB `8.0` (Community or Enterprise).
- **Minimum Supported Version**: MongoDB `6.0`.
- **Driver**: `pymongo >= 4.8.0`.

---

## 2. Local Setup & Service Verification

Do not assume MongoDB is running automatically. Follow these instructions to verify or start the service on your development machine.

### 2.1 macOS (via Homebrew)
If MongoDB was installed using Homebrew:
```bash
# Check if MongoDB service is active
brew services list | grep mongodb

# If stopped, start the service:
brew services start mongodb/brew/mongodb-community
# or for specific 8.0 formula:
brew services start mongodb-community@8.0

# Verify listening port (default: 27017)
lsof -i :27017
```

### 2.2 Direct Binary Execution (Without Background Service)
To run a temporary standalone instance without a system daemon:
```bash
# Create local data directory
mkdir -p /tmp/commerce_insights_db

# Start mongod process
mongod --dbpath /tmp/commerce_insights_db --port 27017 --bind_ip 127.0.0.1
```

### 2.3 Verification via mongosh CLI
Once `mongod` is running, verify network accessibility:
```bash
mongosh "mongodb://localhost:27017" --eval "db.runCommand({ ping: 1 })"
```
Expected output:
```json
{ "ok": 1 }
```

---

## 3. Connection Pooling & PyMongo Driver Tuning

To achieve optimal analytical throughput and avoid connection thrashing during parallel query benchmarks, the backend configures PyMongo's pool with the following parameters:

```python
from pymongo import MongoClient

client = MongoClient(
    host="mongodb://localhost:27017",
    minPoolSize=10,               # Maintain minimum warm connections
    maxPoolSize=50,               # Upper bound under concurrent analytical requests
    serverSelectionTimeoutMS=5000,# Fail quickly if database is unreachable
    socketTimeoutMS=30000,        # Analytical queries may take longer than CRUD operations
    connectTimeoutMS=5000,
    retryWrites=True,
    retryReads=True,
)
```

### Driver Lifespan Management
In FastAPI, never create a new `MongoClient` per HTTP request. The client must be created once during application startup and disposed during shutdown using FastAPI's `lifespan` context manager.

---

## 4. Analytical Schema Design Principles

Commerce Insights models three primary collections:
1. `customers`: User demographic profiles, acquisition channel, creation timestamp.
2. `products`: Catalog items, nested category taxonomy, pricing, inventory.
3. `orders`: High-volume transactional records containing customer references, status, order timestamps, and an embedded array of line items (`items: [{ product_id, sku, quantity, unit_price }]`).

### Read Performance Optimizations:
- **Embedded Line Items**: Orders embed line items directly to avoid expensive multi-collection `$lookup` joins for single-order summaries.
- **Selective Denormalization**: High-frequency analytical attributes (e.g. `category_slug`, `customer_region`) are embedded in the order document to accelerate dimensional aggregations.
- **The ESR Rule (Equality, Sort, Range)**: When constructing compound indexes for analytical filters:
  1. Equality fields first (e.g. `status: "delivered"`, `region: "US-West"`)
  2. Sort fields second (e.g. `order_date: -1`)
  3. Range fields last (e.g. `total_amount: { $gte: 100 }`)

---

## 5. Profiling & Execution Plan Diagnostics

In Phase 3 and Phase 6, the platform compares query execution metrics using MongoDB's explain capability:

```javascript
db.orders.explain("executionStats").aggregate([
  { $match: { status: "completed", order_date: { $gte: ISODate("2024-01-01") } } },
  { $group: { _id: "$customer_id", total_spent: { $sum: "$total_amount" } } }
])
```

### Key Metrics Monitored:
- **`totalDocsExamined`**: Number of documents loaded into memory.
- **`totalKeysExamined`**: Number of index keys traversed. A ratio of `totalDocsExamined / nReturned` close to 1 indicates high index selectivity.
- **`executionStages`**: Identifying whether queries execute via `IXSCAN` (Index Scan) or fall back to an unindexed `COLLSCAN` (Collection Scan).
- **`sortStage`**: Ensuring sorts are satisfied by indexes rather than expensive in-memory sort buffers (`SORT` stage with memory usage warnings).
