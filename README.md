# 🛒 ShopStream Analytics — E-Commerce Data Platform

## Architecture Overview

```
AWS S3 (Raw Data)
      │
      ▼
┌─────────────┐
│   Airflow   │  ← Orchestration (Docker @ D:\airflow)
│    DAGs     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Databricks  │  ← PySpark Transformation Jobs
│  Spark Jobs │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│     dbt     │  ← SQL Transformations (Staging → Marts)
│   Models    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Snowflake  │  ← Data Warehouse (Final Storage)
│  Warehouse  │
└──────┬──────┘
       │
       ▼
  📊 Dashboards (Tableau / Metabase / Power BI)
```

## Project Structure

```
shopstream-analytics/
│
├── dags/                          # Airflow DAGs (copy to D:\airflow\dags)
│   ├── shopstream_ingestion_dag.py       # S3 raw data ingestion
│   ├── shopstream_transform_dag.py       # dbt transformation trigger
│   └── shopstream_master_dag.py          # End-to-end pipeline
│
├── ingestion/                     # S3 ingestion scripts
│   ├── s3_extractor.py
│   └── schema_validator.py
│
├── spark_jobs/                    # Databricks PySpark jobs
│   ├── orders_cleaner.py
│   ├── customers_enrichment.py
│   └── products_aggregator.py
│
├── dbt/                           # dbt transformation project
│   ├── models/
│   │   ├── staging/               # Raw → Cleaned (1:1 source tables)
│   │   ├── intermediate/          # Business logic layer
│   │   └── marts/                 # Final analytics tables
│   ├── tests/
│   ├── macros/
│   └── seeds/
│
├── sql/                           # Snowflake DDL
│   ├── ddl/                       # Table definitions
│   └── procedures/                # Stored procedures
│
├── config/                        # Connection configs (never commit secrets!)
│   ├── airflow_connections.json
│   └── profiles.yml               # dbt profiles
│
├── tests/                         # Data quality tests
└── docs/                          # Architecture docs
```

## Data Flow

| Layer | Tool | Description |
|-------|------|-------------|
| **Ingestion** | Python + S3 | Raw CSV/JSON files land in S3 |
| **Orchestration** | Airflow | Schedules and monitors all pipelines |
| **Processing** | Databricks Spark | Large-scale data cleaning |
| **Transformation** | dbt | Business logic, metrics |
| **Storage** | Snowflake | Final warehouse tables |
| **Serving** | Dashboard tool | Analytics & reporting |

## Data Domains

- **Orders** — transactions, order status, revenue
- **Customers** — profiles, segments, LTV
- **Products** — catalog, inventory, category performance
- **Events** — clickstream, funnel analytics

## Setup Instructions

### 1. Copy DAGs to Airflow
```bash
# Windows
xcopy /E /I dags D:\airflow\dags\shopstream
```

### 2. Set Airflow Connections
In Airflow UI → Admin → Connections:
- `aws_s3_shopstream` — AWS credentials
- `snowflake_shopstream` — Snowflake connection
- `databricks_shopstream` — Databricks token

### 3. Configure dbt
```bash
cp config/profiles.yml ~/.dbt/profiles.yml
cd dbt && dbt debug
```

### 4. Trigger Pipeline
```bash
# Via Airflow UI or CLI
airflow dags trigger shopstream_master_dag
```

## Environment Variables Required
```
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_S3_BUCKET=
SNOWFLAKE_ACCOUNT=
SNOWFLAKE_USER=
SNOWFLAKE_PASSWORD=
SNOWFLAKE_DATABASE=SHOPSTREAM_DB
SNOWFLAKE_WAREHOUSE=SHOPSTREAM_WH
SNOWFLAKE_ROLE=TRANSFORMER
DATABRICKS_HOST=
DATABRICKS_TOKEN=
```
