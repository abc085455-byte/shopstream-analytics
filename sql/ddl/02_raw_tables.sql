-- ============================================================
-- ShopStream Analytics — RAW Layer Tables
-- These mirror exactly what lands from S3
-- Schema: SHOPSTREAM_DB.RAW
-- ============================================================

USE DATABASE SHOPSTREAM_DB;
USE SCHEMA RAW;
USE WAREHOUSE SHOPSTREAM_WH;
USE ROLE SHOPSTREAM_LOADER;

-- ─── ORDERS (raw) ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS RAW.ORDERS (
    -- Raw fields exactly as received from source
    order_id            VARCHAR(50),
    customer_id         VARCHAR(50),
    order_date          VARCHAR(30),        -- Raw string, typed in staging
    order_status        VARCHAR(30),
    payment_method      VARCHAR(30),
    payment_status      VARCHAR(30),
    shipping_address    VARIANT,            -- JSON blob
    total_amount        VARCHAR(20),        -- Raw string
    discount_amount     VARCHAR(20),
    tax_amount          VARCHAR(20),
    currency            VARCHAR(10),
    created_at          VARCHAR(30),
    updated_at          VARCHAR(30),

    -- Metadata added during ingestion
    _source_file        VARCHAR(500),
    _source_loaded_at   TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    _batch_id           VARCHAR(100)
);

-- ─── ORDER ITEMS (raw) ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS RAW.ORDER_ITEMS (
    order_item_id       VARCHAR(50),
    order_id            VARCHAR(50),
    product_id          VARCHAR(50),
    quantity            VARCHAR(20),
    unit_price          VARCHAR(20),
    discount_pct        VARCHAR(20),
    line_total          VARCHAR(20),

    _source_file        VARCHAR(500),
    _source_loaded_at   TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    _batch_id           VARCHAR(100)
);

-- ─── CUSTOMERS (raw) ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS RAW.CUSTOMERS (
    customer_id         VARCHAR(50),
    first_name          VARCHAR(100),
    last_name           VARCHAR(100),
    email               VARCHAR(200),
    phone               VARCHAR(50),
    date_of_birth       VARCHAR(30),
    gender              VARCHAR(20),
    country             VARCHAR(100),
    city                VARCHAR(100),
    signup_date         VARCHAR(30),
    customer_segment    VARCHAR(50),
    is_active           VARCHAR(10),

    _source_file        VARCHAR(500),
    _source_loaded_at   TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    _batch_id           VARCHAR(100)
);

-- ─── PRODUCTS (raw) ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS RAW.PRODUCTS (
    product_id          VARCHAR(50),
    product_name        VARCHAR(300),
    category            VARCHAR(100),
    sub_category        VARCHAR(100),
    brand               VARCHAR(100),
    sku                 VARCHAR(100),
    cost_price          VARCHAR(20),
    selling_price       VARCHAR(20),
    stock_quantity      VARCHAR(20),
    is_active           VARCHAR(10),
    created_date        VARCHAR(30),

    _source_file        VARCHAR(500),
    _source_loaded_at   TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    _batch_id           VARCHAR(100)
);

-- ─── EVENTS / CLICKSTREAM (raw) ──────────────────────────────
CREATE TABLE IF NOT EXISTS RAW.EVENTS (
    event_id            VARCHAR(100),
    session_id          VARCHAR(100),
    customer_id         VARCHAR(50),
    event_type          VARCHAR(50),       -- page_view, add_to_cart, purchase etc.
    event_timestamp     VARCHAR(50),
    page_url            VARCHAR(1000),
    product_id          VARCHAR(50),
    device_type         VARCHAR(30),
    browser             VARCHAR(50),
    ip_address          VARCHAR(50),
    properties          VARIANT,           -- JSON blob for extra attributes

    _source_file        VARCHAR(500),
    _source_loaded_at   TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    _batch_id           VARCHAR(100)
);

-- ─── AUDIT LOG ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS AUDIT.PIPELINE_RUNS (
    run_id              VARCHAR(100),
    dag_id              VARCHAR(200),
    task_id             VARCHAR(200),
    run_date            DATE,
    status              VARCHAR(20),       -- success, failed, skipped
    records_processed   INTEGER,
    records_failed      INTEGER,
    source_path         VARCHAR(500),
    target_table        VARCHAR(200),
    started_at          TIMESTAMP_NTZ,
    finished_at         TIMESTAMP_NTZ,
    duration_seconds    NUMBER(10,2),
    error_message       VARCHAR(5000)
);
