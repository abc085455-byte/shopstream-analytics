-- ============================================================
-- stg_orders.sql
-- Layer: Staging
-- Source: RAW.ORDERS
-- Purpose: Clean types, rename columns, basic validation
-- ============================================================

WITH source AS (
    SELECT * FROM SHOPSTREAM_DB.RAW.orders
),

staged AS (
    SELECT
        -- Keys
        order_id,
        customer_id,

        -- Dates (cast from raw strings)
        TRY_TO_DATE(order_date, 'YYYY-MM-DD')           AS order_date,
        TRY_TO_TIMESTAMP(created_at)                     AS created_at,
        TRY_TO_TIMESTAMP(updated_at)                     AS updated_at,

        -- Status fields (uppercase for consistency)
        UPPER(TRIM(order_status))                        AS order_status,
        UPPER(TRIM(payment_method))                      AS payment_method,
        UPPER(TRIM(payment_status))                      AS payment_status,

        -- Amounts (cast to numeric)
        TRY_TO_DECIMAL(total_amount, 12, 2)              AS total_amount,
        TRY_TO_DECIMAL(discount_amount, 12, 2)           AS discount_amount,
        TRY_TO_DECIMAL(tax_amount, 12, 2)                AS tax_amount,
        COALESCE(TRY_TO_DECIMAL(total_amount, 12, 2), 0)
            - COALESCE(TRY_TO_DECIMAL(discount_amount, 12, 2), 0)
            + COALESCE(TRY_TO_DECIMAL(tax_amount, 12, 2), 0)
                                                         AS net_amount,

        -- Currency
        UPPER(TRIM(currency))                            AS currency,

        -- Address (keep as VARIANT for now, parsed in intermediate)
        shipping_address,

        -- Metadata
        _source_file,
        _source_loaded_at,
        _batch_id

    FROM source

    -- Basic data quality filter: skip rows with no order_id
    WHERE order_id IS NOT NULL
      AND order_id != 'null'
      AND order_id != ''
)

SELECT * FROM staged