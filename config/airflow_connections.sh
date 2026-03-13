# ============================================================
# ShopStream Analytics — Airflow Connections Setup
# ============================================================
# After copying DAGs, set these connections in Airflow UI:
# Go to: http://localhost:8080 → Admin → Connections
# ============================================================

# ─── 1. AWS S3 Connection ────────────────────────────────────
# Connection Id : aws_s3_shopstream
# Connection Type: Amazon Web Services
# AWS Access Key ID: <your key>
# AWS Secret Access Key: <your secret>
# Extra: {"region_name": "us-east-1"}

# CLI equivalent:
airflow connections add 'aws_s3_shopstream' \
    --conn-type 'aws' \
    --conn-extra '{"aws_access_key_id": "YOUR_KEY", "aws_secret_access_key": "YOUR_SECRET", "region_name": "us-east-1"}'

# ─── 2. Snowflake Connection ─────────────────────────────────
# Connection Id : snowflake_shopstream
# Connection Type: Snowflake
# Host: <account>.snowflakecomputing.com
# Schema: RAW
# Login: shopstream_user
# Password: <your password>
# Extra: {"account": "your_account", "warehouse": "SHOPSTREAM_WH", "database": "SHOPSTREAM_DB", "role": "SHOPSTREAM_LOADER"}

airflow connections add 'snowflake_shopstream' \
    --conn-type 'snowflake' \
    --conn-host '<account>.snowflakecomputing.com' \
    --conn-schema 'RAW' \
    --conn-login 'shopstream_user' \
    --conn-password 'YOUR_PASSWORD' \
    --conn-extra '{"account": "YOUR_ACCOUNT", "warehouse": "SHOPSTREAM_WH", "database": "SHOPSTREAM_DB", "role": "SHOPSTREAM_LOADER"}'

# ─── 3. Databricks Connection ────────────────────────────────
# Connection Id : databricks_shopstream
# Connection Type: Databricks
# Host: https://your-workspace.azuredatabricks.net
# Password (Token): <your token>

airflow connections add 'databricks_shopstream' \
    --conn-type 'databricks' \
    --conn-host 'https://your-workspace.azuredatabricks.net' \
    --conn-password 'YOUR_DATABRICKS_TOKEN'

# ─── 4. Airflow Variables ────────────────────────────────────
# Set via UI: Admin → Variables

airflow variables set aws_s3_bucket "shopstream-raw-data"
airflow variables set databricks_host "https://your-workspace.azuredatabricks.net"
airflow variables set databricks_token "YOUR_TOKEN"
airflow variables set alert_email "your-email@company.com"

# Databricks job IDs (get from Databricks UI → Jobs)
airflow variables set databricks_job_ids '{"orders_cleaner": 123, "customers_enrichment": 456}'
