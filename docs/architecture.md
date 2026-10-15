# Architecture Specification: Commerce Insights

## 1. System Vision & Research Context

**Commerce Insights** is built to investigate and demonstrate database read performance and analytical query optimization on document-oriented databases (MongoDB). In traditional relational systems, analytical workloads often rely on star/snowflake schemas and extensive JOIN operations. In document databases, read performance depends on:
- Document nesting vs. referencing trade-offs
- Compound and partial index design
- Aggregation pipeline stage ordering (early `$match` and `$project` pruning)
- Memory usage limits in pipeline stages (e.g. `$sort` 100MB RAM limit)
- Execution plan inspection via `explain("executionStats")`

The architecture enforces strict separation of concerns, explicit contracts, and predictable data flow.

---

## 2. Tier Architecture & Boundaries

```
[ React Client (Vite + TS) ]
            |  ^
  HTTP/JSON |  | ResponseEnvelope<T> / ErrorEnvelope
            v  |
[ FastAPI Gateway (/api/v1) ]
      |             |
      v             v
[ Pydantic Core ]  [ Analytics Services ]
                          |
                   PyMongo Pool
                          |
                          v
               [ MongoDB Database Engine ]
```

### 2.1 Frontend Tier (`frontend/`)
- **Technology**: React 18, TypeScript (strict mode), Vite, Tailwind CSS.
- **Role**: Visualizes analytical aggregates, provides controls to compare indexed vs. unindexed queries, and inspects database execution execution plans (e.g. execution time, keys examined, docs examined).
- **Boundaries**:
  - Does NOT perform client-side calculation of mock statistics.
  - Interacts exclusively with the FastAPI backend through a typed API client (`src/services/apiClient.ts`).
  - Decoupled from backend implementation details; interacts solely via standardized response envelopes.

### 2.2 Backend Application Tier (`backend/app/`)
- **Technology**: Python 3.11+, FastAPI, Pydantic v2, PyMongo.
- **Role**: Coordinates analytical queries, executes aggregation pipelines, measures execution latency, and provides query plan explanation data.
- **Layers**:
  - `core/`: Immutable application settings (`config.py`), logging configuration, and global error handlers.
  - `db/`: Lifecycle management of the PyMongo client and database handle with connection pooling.
  - `schemas/`: Pure Pydantic v2 data models defining API request parameters, response bodies, and error structures.
  - `services/`: Encapsulated domain logic. Coordinates query execution against MongoDB collections.
  - `api/v1/`: HTTP route handlers. Thin layer responsible only for parameter parsing, dependency injection, service invocation, and HTTP response mapping.

### 2.3 Storage Tier (MongoDB)
- **Role**: Primary document datastore. Houses transactional entities (Orders, Products, Customers) and supports analytical aggregation pipelines.
- **Performance Criteria**:
  - Minimized collection scans (`COLLSCAN`) through tailored compound indexes.
  - Measuring index selectivity and index prefix matching.
  - Avoiding unnecessary `$lookup` operations through controlled denormalization of frequently analyzed attributes.

### 2.4 Tooling & Harness Tier (`scripts/`)
- **Role**: Standalone command-line tools for deterministic data generation (`seed_data.py`) and setup diagnostics (`verify_environment.py`).
- **Isolation**: Scripts import configuration and schemas directly or operate independently, avoiding unnecessary web framework overhead.

---

## 3. Communication & Data Flow

1. **Client Request**: Frontend initiates a typed GET or POST request to `/api/v1/...`.
2. **Gateway Validation**: FastAPI validates incoming path, query, and body parameters against Pydantic schemas.
3. **Dependency Injection**: Route handlers resolve the PyMongo database instance through FastAPI's `Depends(get_db)`.
4. **Service Execution**: The domain service dispatches an aggregation pipeline or query to MongoDB.
5. **Driver Pooling**: PyMongo uses its pre-warmed connection pool (`minPoolSize`, `maxPoolSize`), avoiding TCP handshake overhead.
6. **Result Normalization**: MongoDB BSON documents are converted into JSON-serializable Python dictionaries and validated via Pydantic response models.
7. **Envelope Packaging**: Response is encapsulated in a standard envelope `{ "data": ..., "meta": ... }` and returned with HTTP 200.

---

## 4. Architectural Invariants

- **No Secret Leakage**: Secrets and credentials are exclusively supplied via environment variables; never hardcoded or checked into version control.
- **Graceful Lifecycle**: Database connections are initialized during FastAPI startup and drained cleanly during shutdown using the modern `asynccontextmanager` lifespan protocol.
- **Failure Transparency**: Unhandled exceptions are caught by global exception handlers and rendered as structured JSON errors with unique request identifiers rather than stack traces.
