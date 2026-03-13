-- ============================================================
-- mart_orders.sql
-- Layer: Marts
-- Purpose: Final orders analytics table for dashboards
-- Includes: order details + customer info + revenue metrics
-- ============================================================

WITH orders AS (
    SELECT * FROM {{ ref('int_orders_enriched') }}
),

customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

order_items_agg AS (
    SELECT
        order_id,
        COUNT(*)                    AS total_line_items,
        SUM(quantity::INTEGER)      AS total_units_sold,
        MAX(unit_price::DECIMAL)    AS max_unit_price,
        MIN(unit_price::DECIMAL)    AS min_unit_price
    FROM {{ source('raw', 'order_items') }}
    WHERE order_id IS NOT NULL
    GROUP BY order_id
),

final AS (
    SELECT
        -- Order identifiers
        o.order_id,
        o.customer_id,

        -- Customer info (denormalized for dashboard convenience)
        c.full_name          AS customer_name,
        c.email              AS customer_email,
        c.country            AS customer_country,
        c.city               AS customer_city,
        c.customer_segment,

        -- Order details
        o.order_date,
        o.order_status,
        o.payment_method,
        o.payment_status,
        o.currency,

        -- Financial metrics
        o.total_amount,
        o.discount_amount,
        o.tax_amount,
        o.net_amount,

        -- Line item metrics
        COALESCE(oi.total_line_items, 0)    AS total_line_items,
        COALESCE(oi.total_units_sold, 0)    AS total_units_sold,

        -- Time dimensions (for date-based filtering in dashboards)
        DATE_TRUNC('week', o.order_date)    AS order_week,
        DATE_TRUNC('month', o.order_date)   AS order_month,
        DATE_TRUNC('quarter', o.order_date) AS order_quarter,
        YEAR(o.order_date)                  AS order_year,
        DAYOFWEEK(o.order_date)             AS day_of_week,

        -- Boolean flags
        CASE WHEN o.order_status = 'COMPLETED' THEN TRUE ELSE FALSE END
                                            AS is_completed,
        CASE WHEN o.order_status = 'RETURNED' THEN TRUE ELSE FALSE END
                                            AS is_returned,
        CASE WHEN o.discount_amount > 0 THEN TRUE ELSE FALSE END
                                            AS has_discount,

        -- Pipeline metadata
        o._source_loaded_at,
        CURRENT_TIMESTAMP()                 AS _mart_updated_at

    FROM orders o
    LEFT JOIN customers c
        ON o.customer_id = c.customer_id
    LEFT JOIN order_items_agg oi
        ON o.order_id = oi.order_id
)

SELECT * FROM final
