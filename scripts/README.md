# Automation & Tooling Scripts: Commerce Insights

This directory contains standalone Python command-line tools for environment diagnostics, synthetic data generation, and database performance benchmarking.

---

## 1. Available Scripts

### `verify_environment.py`
Automated pre-flight diagnostic utility that inspects the local development environment:
- Verifies Python version (`>= 3.11`) and virtual environment state.
- Inspects Node.js (`>= 20`) and npm availability.
- Detects local MongoDB binaries (`mongod`, `mongosh`).
- Validates the project directory structure and `.env` / `.env.example` existence.

**Usage:**
```bash
python3 scripts/verify_environment.py
```

---

### `seed_data.py`
Synthetic e-commerce data generation tool designed for Phase 2 implementation. It uses `Faker` to deterministically generate high-volume collections:
- `customers`: Demographic profiles, registration dates, regions.
- `products`: Deep catalog taxonomy, SKU, price, category hierarchy.
- `orders`: Realistic transactional order volume with embedded order line items.

**Planned Options:**
- `--customers <count>`: Target customer population (default: `10000`).
- `--products <count>`: Target product catalog size (default: `2000`).
- `--orders <count>`: Target order transaction volume (default: `50000`).
- `--batch-size <size>`: Batch size for bulk MongoDB inserts (default: `5000`).
- `--drop`: Drop existing collections before seeding.
- `--dry-run`: Generate samples to stdout without writing to the database.

**Usage Example:**
```bash
python3 scripts/seed_data.py --dry-run --customers 10 --orders 20
```
