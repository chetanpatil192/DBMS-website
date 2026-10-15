# API Conventions & Standards: Commerce Insights

## 1. Versioning Strategy

All public application APIs must be prefixed with an explicit major version identifier:
```
/api/v1/
```
- **Major Version Bump (`/api/v2/`)**: Reserved for breaking contract changes, such as removing fields, altering envelope schemas, or fundamentally modifying filter semantics.
- **Additive Changes**: Non-breaking additions (e.g., adding an optional field to an existing response schema) are introduced within the active version (`v1`).

---

## 2. Resource Naming & URI Design

- **Plural Nouns for Collections**: Use plural nouns for endpoints representing collections:
  - `GET /api/v1/analytics/orders`
  - `GET /api/v1/analytics/products`
  - `GET /api/v1/benchmarks`
- **Kebab-Case Paths**: URIs are lowercase with words separated by hyphens:
  - `GET /api/v1/analytics/revenue-by-category`
  - `POST /api/v1/benchmarks/explain-query`
- **Snake_Case Query Parameters**: URL query parameters adhere to snake_case:
  - `?start_date=2024-01-01&end_date=2024-12-31&page=1&page_size=50`
- **HTTP Methods**:
  - `GET`: Safe, idempotent retrieval. No server-side state mutation.
  - `POST`: Create a resource or submit an analytical execution payload (e.g. running a benchmark comparison).
  - `DELETE`: Idempotent resource removal.

---

## 3. Standard Response Envelopes

To ensure client predictability and uniform error handling across the entire frontend and backend, all endpoints emit responses inside structured envelopes.

### 3.1 Success Envelope
```json
{
  "data": { ... },
  "meta": {
    "timestamp": "2026-10-15T12:00:00Z",
    "execution_time_ms": 14.8,
    "pagination": {
      "page": 1,
      "page_size": 50,
      "total_items": 1250,
      "total_pages": 25
    }
  }
}
```
- `data`: The primary payload (object or array).
- `meta`: Metadata containing UTC ISO-8601 timestamp, server-measured execution latency, and optional pagination details.

### 3.2 Error Envelope
When an HTTP status is `>= 400`, the body must strictly follow this structure:
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested analytical cohort does not exist.",
    "details": {
      "cohort_id": "ch_98234"
    },
    "timestamp": "2026-10-15T12:00:00Z"
  }
}
```

---

## 4. Standard Error Codes & HTTP Statuses

| HTTP Status | Error Code (`error.code`) | Description |
| :--- | :--- | :--- |
| **400 Bad Request** | `INVALID_PARAMETERS` | Query parameter, filter, or payload validation failure. |
| **404 Not Found** | `RESOURCE_NOT_FOUND` | The specified entity, dataset, or report was not found. |
| **422 Unprocessable** | `SCHEMA_VALIDATION_ERROR` | Pydantic validation error detailing field-level constraints. |
| **500 Server Error** | `INTERNAL_SERVER_ERROR` | Unexpected server failure. Details are logged, but raw tracebacks are never exposed to the client. |
| **503 Unavailable** | `DATABASE_UNAVAILABLE` | PyMongo connection timeout or database unreachable. |

---

## 5. Query Performance Metadata

Because the platform is centered on database read performance research, analytical responses include database-level metrics in the `meta` section when profiling is requested:

```json
{
  "meta": {
    "execution_time_ms": 22.4,
    "profiling": {
      "stage": "IXSCAN",
      "index_name": "idx_category_order_date",
      "docs_examined": 1500,
      "keys_examined": 1500,
      "in_memory_sort": false
    }
  }
}
```
This metadata enables the frontend to display database engine diagnostics alongside the analytical results.
