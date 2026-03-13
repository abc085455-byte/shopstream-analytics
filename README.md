🛒 ShopStream Analytics — End-to-End E-Commerce Data Pipeline


📐 Architecture
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

🗂️ Project Structure
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

📊 Data Pipeline
LayerToolWhat it doesRaw StorageAWS S3CSV files land here dailyOrchestrationApache AirflowSchedules & monitors the pipelineRaw WarehouseSnowflake RAWExact copy of S3 dataStagingdbt viewsCleaned, renamed, typedIntermediatedbt tablesJoined, enriched business logicMartsdbt tablesFinal KPIs — RFM, LTV, revenue

📦 Data Domains
DomainRecordsDescriptionOrders1,000/dayTransactions, status, revenueCustomers500Profiles, segments, RFM scoresProducts100Catalog, pricing, inventoryEvents5,000/dayClickstream, funnel analytics

🚀 How to Run This Project
Prerequisites

Python 3.10+
Docker Desktop
AWS Account (S3 bucket)
Snowflake Account (free trial works)
dbt-snowflake installed

1. Clone the repo
bashgit clone https://github.com/abc085455-byte/shopstream-analytics.git
cd shopstream-analytics
2. Setup environment variables
bashcp .env.example .env
# Fill in your AWS and Snowflake credentials in .env
3. Setup Snowflake
sql-- Run in Snowflake worksheet
-- sql/ddl/01_snowflake_setup.sql  (database, schemas, warehouse)
-- sql/ddl/02_raw_tables.sql       (RAW tables)
4. Generate sample data & upload to S3
bashpython generate_sample_data.py
5. Start Airflow
bashcd /path/to/airflow
docker compose up -d
# Open http://localhost:8080
# Trigger: shopstream_master_pipeline
6. Run dbt transformations
bashcd dbt
dbt run
dbt test

🏗️ dbt Models
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

📈 Key Metrics Generated
mart_orders

Net revenue per order
Order status breakdown
Payment method analysis

mart_customers

RFM Score (Recency, Frequency, Monetary)
LTV Tier (High / Medium / Low)
Customer segments



🛠️ Tech Stack
ToolVersionPurposeApache Airflow3.1.7Pipeline orchestrationdbt Core1.11.7SQL transformationsSnowflake—Cloud data warehouseAWS S3—Raw data storagePython3.10Ingestion scriptsDocker—Airflow containerization

👤 Author
Muhammad Shawail
Data Engineering Project
