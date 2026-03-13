# 🛒 ShopStream Analytics — End-to-End E-Commerce Data Pipeline

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Airflow](https://img.shields.io/badge/Airflow-3.1.7-red)
![dbt](https://img.shields.io/badge/dbt-1.11.7-orange)
![Snowflake](https://img.shields.io/badge/Snowflake-Data%20Warehouse-lightblue)
![AWS S3](https://img.shields.io/badge/AWS-S3-yellow)

A production-grade data engineering portfolio project that simulates a real-world e-commerce analytics platform — from raw data ingestion to business-ready data marts.

---

## 📐 Architecture

```
AWS S3 (Raw CSV Data)
        │
        ▼
   Apache Airflow          ← Orchestration & Scheduling (Docker)
        │
        ▼
  Snowflake RAW            ← Raw data landing zone
        │
        ▼
     dbt Core              ← SQL Transformations
   ┌────┴────┐
 Staging  Intermediate
        │
        ▼
  Snowflake Marts          ← Business-ready analytics tables
        │
        ▼
    Dashboard              ← Power BI / Metabase
```

---

## 🗂️ Project Structure

```
shopstream-analytics/
├── dags/
│   └── shopstream_master_dag.py     # Airflow DAG — S3 to Snowflake
├── dbt/
│   ├── dbt_project.yml
│   └── models/
│       ├── staging/                 # stg_orders, stg_customers
│       ├── intermediate/            # int_orders_enriched
│       └── marts/                   # mart_orders, mart_customers
├── ingestion/
│   └── s3_extractor.py              # S3 extraction utility
├── sql/
│   └── ddl/
│       ├── 01_snowflake_setup.sql   # Database, schemas, warehouse
│       └── 02_raw_tables.sql        # RAW layer table definitions
├── generate_sample_data.py          # Generates & uploads fake e-commerce data to S3
├── requirements.txt
├── .env.example                     # Environment variables template
└── README.md
```

---

## 📊 Data Pipeline

| Layer | Tool | What it does |
|-------|------|-------------|
| **Raw Storage** | AWS S3 | CSV files land here daily |
| **Orchestration** | Apache Airflow | Schedules & monitors the pipeline |
| **Raw Warehouse** | Snowflake RAW | Exact copy of S3 data |
| **Staging** | dbt views | Cleaned, renamed, typed |
| **Intermediate** | dbt tables | Joined, enriched business logic |
| **Marts** | dbt tables | Final KPIs — RFM, LTV, revenue |

---

## 📦 Data Domains

| Domain | Records | Description |
|--------|---------|-------------|
| Orders | 1,000/day | Transactions, status, revenue |
| Customers | 500 | Profiles, segments, RFM scores |
| Products | 100 | Catalog, pricing, inventory |
| Events | 5,000/day | Clickstream, funnel analytics |

---

## 🚀 How to Run This Project

### Prerequisites
- Python 3.10+
- Docker Desktop
- AWS Account (S3 bucket)
- Snowflake Account (free trial works)
- dbt-snowflake installed

### 1. Clone the repo
```bash
git clone https://github.com/abc085455-byte/shopstream-analytics.git
cd shopstream-analytics
```

### 2. Setup environment variables
```bash
cp .env.example .env
# Fill in your AWS and Snowflake credentials in .env
```

### 3. Setup Snowflake
```sql
-- Run in Snowflake worksheet
-- sql/ddl/01_snowflake_setup.sql  (database, schemas, warehouse)
-- sql/ddl/02_raw_tables.sql       (RAW tables)
```

### 4. Generate sample data & upload to S3
```bash
python generate_sample_data.py
```

### 5. Start Airflow
```bash
cd /path/to/airflow
docker compose up -d
# Open http://localhost:8080
# Trigger: shopstream_master_pipeline
```

### 6. Run dbt transformations
```bash
cd dbt
dbt run
dbt test
```

---

## 🏗️ dbt Models

```
RAW.ORDERS + RAW.CUSTOMERS
        │
        ▼
stg_orders          stg_customers
        │                  │
        └──────┬───────────┘
               ▼
      int_orders_enriched
               │
       ┌───────┴────────┐
       ▼                ▼
  mart_orders     mart_customers
  (revenue KPIs)  (RFM + LTV segments)
```

---

## 📈 Key Metrics Generated

**mart_orders**
- Net revenue per order
- Order status breakdown
- Payment method analysis

**mart_customers**
- RFM Score (Recency, Frequency, Monetary)
- LTV Tier (High / Medium / Low)
- Customer segments

---

## 🔐 Security Notes

- Never commit `profiles.yml` or `.env` files
- Use environment variables for all credentials
- Rotate AWS keys regularly
- See `.env.example` for required variables

---

## 🛠️ Tech Stack

| Tool | Version | Purpose |
|------|---------|---------|
| Apache Airflow | 3.1.7 | Pipeline orchestration |
| dbt Core | 1.11.7 | SQL transformations |
| Snowflake | — | Cloud data warehouse |
| AWS S3 | — | Raw data storage |
| Python | 3.10 | Ingestion scripts |
| Docker | — | Airflow containerization |

---

## 👤 Author
Muhammad Shawail Data Engineering Project

**Muhammad Shawail**
Data Engineering Portfolio Project
