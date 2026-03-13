"""
ShopStream Analytics — Sample Data Generator
=============================================
Yeh script realistic e-commerce sample data generate karta hai
aur seedha AWS S3 mein upload karta hai.

Run karo:
    pip install faker boto3 pandas
    python generate_sample_data.py

S3 Structure jo banega:
    shopstream-raw-data/
    └── ecommerce/
        ├── orders/2024/01/15/orders.csv
        ├── customers/2024/01/15/customers.csv
        ├── products/2024/01/15/products.csv
        └── events/2024/01/15/events.csv
"""

import boto3
import pandas as pd
import random
import uuid
import json
import os
from datetime import datetime, timedelta
from faker import Faker

# ─── CONFIG ──────────────────────────────────────────────────
fake = Faker()
random.seed(42)

BUCKET_NAME   = "shopstream-raw-data"
RUN_DATE      = datetime.today().strftime("%Y-%m-%d")
DATE_PATH     = datetime.today().strftime("%Y/%m/%d")
REGION        = "us-east-1"

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')

# Data volumes
NUM_CUSTOMERS = 500
NUM_PRODUCTS  = 100
NUM_ORDERS    = 1000
NUM_EVENTS    = 5000

print("=" * 60)
print("  ShopStream Analytics — Sample Data Generator")
print("=" * 60)

# ─── S3 CLIENT ───────────────────────────────────────────────
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION,
)

def upload_to_s3(df: pd.DataFrame, s3_key: str):
    """DataFrame ko CSV banao aur S3 mein upload karo"""
    csv_buffer = df.to_csv(index=False)
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=csv_buffer.encode("utf-8"),
        ContentType="text/csv",
    )
    print(f"  ✅ Uploaded {len(df):,} rows → s3://{BUCKET_NAME}/{s3_key}")

# ─── 1. CUSTOMERS ────────────────────────────────────────────
print("\n[1/4] Generating Customers...")

SEGMENTS   = ["Premium", "Regular", "New", "Churned", "VIP"]
COUNTRIES  = ["Pakistan", "India", "USA", "UK", "UAE", "Canada", "Australia"]
GENDERS    = ["Male", "Female", "Other"]

customer_ids = [str(uuid.uuid4())[:8].upper() for _ in range(NUM_CUSTOMERS)]

customers = []
for cid in customer_ids:
    signup = fake.date_between(start_date="-3y", end_date="today")
    customers.append({
        "customer_id":      cid,
        "first_name":       fake.first_name(),
        "last_name":        fake.last_name(),
        "email":            fake.email(),
        "phone":            fake.phone_number()[:15],
        "date_of_birth":    fake.date_of_birth(minimum_age=18, maximum_age=65).strftime("%Y-%m-%d"),
        "gender":           random.choice(GENDERS),
        "country":          random.choice(COUNTRIES),
        "city":             fake.city(),
        "signup_date":      signup.strftime("%Y-%m-%d"),
        "customer_segment": random.choice(SEGMENTS),
        "is_active":        random.choice(["True", "True", "True", "False"]),
    })

df_customers = pd.DataFrame(customers)
upload_to_s3(df_customers, f"ecommerce/customers/{DATE_PATH}/customers.csv")

# ─── 2. PRODUCTS ─────────────────────────────────────────────
print("\n[2/4] Generating Products...")

CATEGORIES = {
    "Electronics":  ["Mobile", "Laptop", "Tablet", "Headphones", "Smartwatch"],
    "Fashion":      ["T-Shirt", "Jeans", "Dress", "Shoes", "Jacket"],
    "Home":         ["Sofa", "Bed", "Table", "Chair", "Lamp"],
    "Beauty":       ["Moisturizer", "Lipstick", "Perfume", "Serum", "Shampoo"],
    "Sports":       ["Shoes", "Gloves", "Racket", "Dumbbells", "Yoga Mat"],
}

product_ids = [str(uuid.uuid4())[:8].upper() for _ in range(NUM_PRODUCTS)]
BRANDS = ["Samsung", "Apple", "Nike", "H&M", "IKEA", "L'Oreal", "Adidas", "Zara", "Sony", "LG"]

products = []
for pid in product_ids:
    category    = random.choice(list(CATEGORIES.keys()))
    sub_cat     = random.choice(CATEGORIES[category])
    cost        = round(random.uniform(10, 800), 2)
    sell_price  = round(cost * random.uniform(1.3, 2.5), 2)
    products.append({
        "product_id":       pid,
        "product_name":     f"{random.choice(BRANDS)} {sub_cat} {fake.color_name()}",
        "category":         category,
        "sub_category":     sub_cat,
        "brand":            random.choice(BRANDS),
        "sku":              f"SKU-{pid}",
        "cost_price":       cost,
        "selling_price":    sell_price,
        "stock_quantity":   random.randint(0, 500),
        "is_active":        random.choice(["True", "True", "True", "False"]),
        "created_date":     fake.date_between(start_date="-2y", end_date="-1m").strftime("%Y-%m-%d"),
    })

df_products = pd.DataFrame(products)
upload_to_s3(df_products, f"ecommerce/products/{DATE_PATH}/products.csv")

# ─── 3. ORDERS + ORDER ITEMS ─────────────────────────────────
print("\n[3/4] Generating Orders...")

STATUSES        = ["completed", "completed", "completed", "pending", "cancelled", "returned"]
PAYMENT_METHODS = ["credit_card", "debit_card", "jazzcash", "easypaisa", "bank_transfer", "cod"]
PAYMENT_STATUS  = ["paid", "paid", "paid", "pending", "failed"]

orders      = []
order_items = []

for _ in range(NUM_ORDERS):
    oid         = str(uuid.uuid4())[:10].upper()
    cid         = random.choice(customer_ids)
    order_date  = fake.date_between(start_date="-1y", end_date="today")
    status      = random.choice(STATUSES)
    n_items     = random.randint(1, 5)

    total       = 0
    discount    = round(random.uniform(0, 50), 2)

    # Order items
    for i in range(n_items):
        pid        = random.choice(product_ids)
        prod       = next(p for p in products if p["product_id"] == pid)
        qty        = random.randint(1, 4)
        unit_price = prod["selling_price"]
        disc_pct   = round(random.uniform(0, 0.2), 2)
        line_total = round(qty * unit_price * (1 - disc_pct), 2)
        total     += line_total

        order_items.append({
            "order_item_id": str(uuid.uuid4())[:10].upper(),
            "order_id":      oid,
            "product_id":    pid,
            "quantity":      qty,
            "unit_price":    unit_price,
            "discount_pct":  disc_pct,
            "line_total":    line_total,
        })

    tax = round(total * 0.17, 2)  # 17% GST Pakistan

    orders.append({
        "order_id":       oid,
        "customer_id":    cid,
        "order_date":     order_date.strftime("%Y-%m-%d"),
        "order_status":   status,
        "payment_method": random.choice(PAYMENT_METHODS),
        "payment_status": random.choice(PAYMENT_STATUS),
        "shipping_address": json.dumps({
            "city":    fake.city(),
            "country": random.choice(COUNTRIES),
            "zip":     fake.postcode(),
        }),
        "total_amount":   round(total, 2),
        "discount_amount":discount,
        "tax_amount":     tax,
        "currency":       "PKR",
        "created_at":     order_date.strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at":     (order_date + timedelta(days=random.randint(0, 5))).strftime("%Y-%m-%d %H:%M:%S"),
    })

df_orders      = pd.DataFrame(orders)
df_order_items = pd.DataFrame(order_items)

upload_to_s3(df_orders,      f"ecommerce/orders/{DATE_PATH}/orders.csv")
upload_to_s3(df_order_items, f"ecommerce/orders/{DATE_PATH}/order_items.csv")

# ─── 4. EVENTS / CLICKSTREAM ─────────────────────────────────
print("\n[4/4] Generating Events...")

EVENT_TYPES = [
    "page_view", "page_view", "page_view",
    "product_view", "product_view",
    "add_to_cart",
    "remove_from_cart",
    "checkout_start",
    "purchase",
    "search",
]
DEVICES  = ["mobile", "mobile", "desktop", "tablet"]
BROWSERS = ["Chrome", "Safari", "Firefox", "Edge"]

events = []
for _ in range(NUM_EVENTS):
    event_date = fake.date_time_between(start_date="-30d", end_date="now")
    event_type = random.choice(EVENT_TYPES)
    pid        = random.choice(product_ids) if event_type in ["product_view", "add_to_cart", "purchase"] else None

    events.append({
        "event_id":        str(uuid.uuid4()),
        "session_id":      str(uuid.uuid4())[:12],
        "customer_id":     random.choice(customer_ids + [None] * 50),  # some anonymous
        "event_type":      event_type,
        "event_timestamp": event_date.strftime("%Y-%m-%d %H:%M:%S"),
        "page_url":        f"https://shopstream.com/{fake.uri_path()}",
        "product_id":      pid,
        "device_type":     random.choice(DEVICES),
        "browser":         random.choice(BROWSERS),
        "ip_address":      fake.ipv4(),
        "properties":      json.dumps({"source": random.choice(["organic", "paid", "email", "social"])}),
    })

df_events = pd.DataFrame(events)
upload_to_s3(df_events, f"ecommerce/events/{DATE_PATH}/events.csv")

# ─── SUMMARY ─────────────────────────────────────────────────
print("\n" + "=" * 60)
print("  ✅ ALL DATA UPLOADED TO S3 SUCCESSFULLY!")
print("=" * 60)
print(f"\n  📦 Bucket   : s3://{BUCKET_NAME}")
print(f"  📅 Date Path: ecommerce/*/{ DATE_PATH}/")
print(f"\n  📊 Records Generated:")
print(f"     Customers  : {len(df_customers):,}")
print(f"     Products   : {len(df_products):,}")
print(f"     Orders     : {len(df_orders):,}")
print(f"     Order Items: {len(df_order_items):,}")
print(f"     Events     : {len(df_events):,}")
print("\n  🚀 Next Step: Airflow DAG run karo!")
print("=" * 60)