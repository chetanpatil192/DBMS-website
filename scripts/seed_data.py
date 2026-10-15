#!/usr/bin/env python3
"""Synthetic data generation pipeline for Commerce Insights.

Generates 50,000 e-commerce records (customers, products, and orders)
using Faker and inserts them into MongoDB in high-performance batches.
Also builds necessary compound and search indexes.
"""

import argparse
import os
import random
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

from faker import Faker
from pymongo import ASCENDING, DESCENDING, MongoClient, TEXT
from pymongo.collection import Collection

# Load environment configuration
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

try:
    from app.core.config import get_settings
    settings = get_settings()
    DEFAULT_MONGO_URI = settings.MONGODB_URI
    DEFAULT_DB_NAME = settings.MONGODB_DB_NAME
except Exception:
    DEFAULT_MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DEFAULT_DB_NAME = os.getenv("MONGODB_DB_NAME", "commerce_insights")


CATEGORIES = [
    {"primary": "Electronics", "sub": ["Audio", "Computers", "Smartphones", "Wearables", "Cameras"]},
    {"primary": "Home & Kitchen", "sub": ["Cookware", "Appliances", "Furniture", "Bedding", "Home Decor"]},
    {"primary": "Apparel", "sub": ["Men's Wear", "Women's Wear", "Footwear", "Activewear", "Accessories"]},
    {"primary": "Books", "sub": ["Technology", "Business", "Fiction", "Science", "Biography"]},
    {"primary": "Health & Wellness", "sub": ["Fitness", "Vitamins", "Personal Care", "Nutrition", "Yoga"]},
]

ORDER_STATUSES = ["completed", "completed", "completed", "shipped", "pending", "cancelled"]
PAYMENT_METHODS = ["credit_card", "paypal", "apple_pay", "bank_transfer"]
REGIONS = ["North America", "Europe", "Asia-Pacific", "Latin America", "Middle East"]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Seed 50,000 realistic e-commerce records into MongoDB",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--customers", type=int, default=5000, help="Customer records count")
    parser.add_argument("--products", type=int, default=1000, help="Product catalog records count")
    parser.add_argument("--orders", type=int, default=44000, help="Order transaction records count")
    parser.add_argument("--batch-size", type=int, default=5000, help="Batch size for insert_many")
    parser.add_argument("--mongo-uri", type=str, default=DEFAULT_MONGO_URI, help="MongoDB connection URI")
    parser.add_argument("--db-name", type=str, default=DEFAULT_DB_NAME, help="MongoDB target database")
    parser.add_argument("--drop", action="store_true", default=True, help="Drop collections before seeding")
    parser.add_argument("--seed", type=int, default=42, help="Deterministic random seed")
    return parser.parse_args()


def create_indexes(db: Any) -> None:
    """Creates the specific indexes needed for dashboard queries and customer search."""
    print("Creating MongoDB indexes...")
    # Customers indexes
    db.customers.create_index([("customer_id", ASCENDING)], unique=True, name="idx_cust_id")
    db.customers.create_index([("name", TEXT), ("email", TEXT)], name="idx_cust_text_search")
    db.customers.create_index([("created_at", DESCENDING)], name="idx_cust_created")
    db.customers.create_index([("total_spent", DESCENDING)], name="idx_cust_spent")

    # Orders indexes
    db.orders.create_index([("order_id", ASCENDING)], unique=True, name="idx_order_id")
    db.orders.create_index([("customer_id", ASCENDING)], name="idx_order_cust_id")
    db.orders.create_index([("order_date", DESCENDING)], name="idx_order_date_desc")
    db.orders.create_index([("status", ASCENDING), ("order_date", DESCENDING)], name="idx_order_status_date")
    print("✔ MongoDB indexes created successfully.")


def seed_database(args: argparse.Namespace) -> None:
    total_records = args.customers + args.products + args.orders
    print("=" * 70)
    print(f"  Commerce Insights Seeder: Target {total_records:,} Records")
    print("=" * 70)
    print(f"MongoDB URI     : {args.mongo_uri}")
    print(f"Database        : {args.db_name}")
    print(f"Customers       : {args.customers:,}")
    print(f"Products        : {args.products:,}")
    print(f"Orders          : {args.orders:,}")
    print(f"Batch Size      : {args.batch_size:,}")
    print(f"Random Seed     : {args.seed}")
    print("=" * 70)

    # Initialize Faker with seed
    fake = Faker()
    Faker.seed(args.seed)
    random.seed(args.seed)

    # Connect to MongoDB
    client: MongoClient = MongoClient(args.mongo_uri, serverSelectionTimeoutMS=5000)
    db = client[args.db_name]

    # Verify connection
    db.command("ping")
    print("✔ MongoDB server connected.")

    if args.drop:
        print("Dropping existing collections...")
        db.customers.drop()
        db.products.drop()
        db.orders.drop()
        print("✔ Existing collections dropped.")

    start_total_time = time.perf_counter()

    # 1. Generate and insert Products
    print(f"\n[1/3] Generating {args.products:,} products...")
    t0 = time.perf_counter()
    products: List[Dict[str, Any]] = []
    product_refs: List[Dict[str, Any]] = []

    for i in range(1, args.products + 1):
        cat_info = random.choice(CATEGORIES)
        primary_cat = cat_info["primary"]
        sub_cat = random.choice(cat_info["sub"])
        price = round(random.uniform(12.0, 499.0), 2)
        prod_id = f"prod_{i:05d}"

        product_doc = {
            "product_id": prod_id,
            "sku": f"SKU-{primary_cat[:3].upper()}-{i:04d}",
            "name": f"{fake.word().capitalize()} {sub_cat} {fake.color_name().capitalize()}",
            "category": primary_cat,
            "subcategory": sub_cat,
            "price": price,
            "stock_quantity": random.randint(10, 500),
            "created_at": datetime.now(timezone.utc) - timedelta(days=random.randint(100, 400)),
        }
        products.append(product_doc)
        product_refs.append({
            "product_id": prod_id,
            "name": product_doc["name"],
            "category": primary_cat,
            "price": price,
        })

        if len(products) >= args.batch_size:
            db.products.insert_many(products, ordered=False)
            products = []

    if products:
        db.products.insert_many(products, ordered=False)
    print(f"✔ Products inserted in {time.perf_counter() - t0:.2f}s")

    # 2. Generate and insert Customers
    print(f"\n[2/3] Generating {args.customers:,} customers...")
    t0 = time.perf_counter()
    customers: List[Dict[str, Any]] = []
    customer_refs: List[Dict[str, Any]] = []

    now = datetime.now(timezone.utc)
    for i in range(1, args.customers + 1):
        cust_id = f"cust_{i:06d}"
        name = fake.name()
        email = f"user_{i}_{fake.user_name()}@{fake.free_email_domain()}"
        city = fake.city()
        country = fake.country()
        created_at = now - timedelta(days=random.randint(30, 365))

        cust_doc = {
            "customer_id": cust_id,
            "name": name,
            "email": email,
            "phone": fake.phone_number(),
            "city": city,
            "country": country,
            "region": random.choice(REGIONS),
            "total_spent": 0.0,
            "order_count": 0,
            "created_at": created_at,
        }
        customers.append(cust_doc)
        customer_refs.append({
            "customer_id": cust_id,
            "name": name,
            "email": email,
            "region": cust_doc["region"],
            "created_at": created_at,
        })

        if len(customers) >= args.batch_size:
            db.customers.insert_many(customers, ordered=False)
            customers = []

    if customers:
        db.customers.insert_many(customers, ordered=False)
    print(f"✔ Customers inserted in {time.perf_counter() - t0:.2f}s")

    # 3. Generate and insert Orders
    print(f"\n[3/3] Generating {args.orders:,} orders with embedded items...")
    t0 = time.perf_counter()
    orders: List[Dict[str, Any]] = []
    
    # We will accumulate spent totals and order counts per customer for fast indexing
    customer_stats: Dict[str, Dict[str, Any]] = {
        c["customer_id"]: {"total_spent": 0.0, "order_count": 0} for c in customer_refs
    }

    base_time = now - timedelta(days=180)

    for i in range(1, args.orders + 1):
        order_id = f"ord_{i:08d}"
        cust = random.choice(customer_refs)
        # Order date distributed between 180 days ago and now
        order_date = base_time + timedelta(
            seconds=random.randint(0, int((now - base_time).total_seconds()))
        )
        status = random.choice(ORDER_STATUSES)

        # Generate 1 to 4 line items
        num_items = random.randint(1, 4)
        items = []
        order_total = 0.0

        for _ in range(num_items):
            prod = random.choice(product_refs)
            qty = random.randint(1, 3)
            unit_price = prod["price"]
            subtotal = round(qty * unit_price, 2)
            order_total += subtotal
            items.append({
                "product_id": prod["product_id"],
                "name": prod["name"],
                "category": prod["category"],
                "quantity": qty,
                "unit_price": unit_price,
                "subtotal": subtotal,
            })

        order_total = round(order_total, 2)

        order_doc = {
            "order_id": order_id,
            "customer_id": cust["customer_id"],
            "customer_name": cust["name"],
            "customer_email": cust["email"],
            "region": cust["region"],
            "order_date": order_date,
            "status": status,
            "payment_method": random.choice(PAYMENT_METHODS),
            "total_amount": order_total,
            "items_count": num_items,
            "items": items,
        }
        orders.append(order_doc)

        # Track customer stats if not cancelled
        if status != "cancelled":
            c_stat = customer_stats[cust["customer_id"]]
            c_stat["total_spent"] = round(c_stat["total_spent"] + order_total, 2)
            c_stat["order_count"] += 1

        if len(orders) >= args.batch_size:
            db.orders.insert_many(orders, ordered=False)
            orders = []
            if i % 10000 == 0:
                print(f"  Inserted {i:,}/{args.orders:,} orders...")

    if orders:
        db.orders.insert_many(orders, ordered=False)
    print(f"✔ Orders inserted in {time.perf_counter() - t0:.2f}s")

    # 4. Bulk update customers with aggregated stats
    print("\nUpdating customer aggregate stats...")
    t0 = time.perf_counter()
    from pymongo import UpdateOne
    bulk_updates = []
    for cust_id, stat in customer_stats.items():
        if stat["order_count"] > 0:
            bulk_updates.append(
                UpdateOne(
                    {"customer_id": cust_id},
                    {"$set": {"total_spent": stat["total_spent"], "order_count": stat["order_count"]}}
                )
            )
            if len(bulk_updates) >= args.batch_size:
                db.customers.bulk_write(bulk_updates, ordered=False)
                bulk_updates = []

    if bulk_updates:
        db.customers.bulk_write(bulk_updates, ordered=False)
    print(f"✔ Customer stats updated in {time.perf_counter() - t0:.2f}s")

    # 5. Build indexes
    create_indexes(db)

    # 6. Verify collection counts
    cust_count = db.customers.count_documents({})
    prod_count = db.products.count_documents({})
    ord_count = db.orders.count_documents({})
    total_docs = cust_count + prod_count + ord_count

    print("\n" + "=" * 70)
    print("  SEEDING COMPLETE & VERIFIED")
    print("=" * 70)
    print(f"Customers in DB : {cust_count:,}")
    print(f"Products in DB  : {prod_count:,}")
    print(f"Orders in DB    : {ord_count:,}")
    print(f"Total Documents : {total_docs:,}")
    print(f"Total Duration  : {time.perf_counter() - start_total_time:.2f} seconds")
    print("=" * 70)


def main() -> int:
    args = parse_arguments()
    try:
        seed_database(args)
        return 0
    except Exception as exc:
        print(f"\n✖ Seeding failed: {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
