-- ============================================================
-- mart_customers.sql
-- Layer: Marts
-- Purpose: Customer 360 view — LTV, order history, segments
-- ============================================================

WITH customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

orders AS (
    SELECT *
    FROM {{ ref('stg_orders') }}
    WHERE order_status NOT IN ('CANCELLED', 'RETURNED')
),

customer_order_stats AS (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id)                            AS total_orders,
        SUM(net_amount)                                     AS total_revenue,
        AVG(net_amount)                                     AS avg_order_value,
        MIN(order_date)                                     AS first_order_date,
        MAX(order_date)                                     AS last_order_date,
        DATEDIFF('day', MIN(order_date), MAX(order_date))   AS customer_lifespan_days,
        COUNT(DISTINCT DATE_TRUNC('month', order_date))     AS active_months

    FROM orders
    GROUP BY customer_id
),

final AS (
    SELECT
        -- Customer identifiers
        c.customer_id,
        c.full_name,
        c.email,
        c.phone,
        c.country,
        c.city,
        c.gender,
        c.date_of_birth,
        c.signup_date,
        c.customer_segment,
        c.is_active,

        -- Age
        DATEDIFF('year', c.date_of_birth, CURRENT_DATE())  AS age_years,

        -- Tenure
        DATEDIFF('day', c.signup_date, CURRENT_DATE())     AS days_since_signup,

        -- Order metrics
        COALESCE(os.total_orders, 0)                        AS total_orders,
        COALESCE(os.total_revenue, 0)                       AS lifetime_value,
        COALESCE(os.avg_order_value, 0)                     AS avg_order_value,
        os.first_order_date,
        os.last_order_date,
        os.customer_lifespan_days,

        -- Recency (days since last order)
        DATEDIFF('day', os.last_order_date, CURRENT_DATE()) AS days_since_last_order,

        -- RFM Segments (Recency-Frequency-Monetary)
        CASE
            WHEN DATEDIFF('day', os.last_order_date, CURRENT_DATE()) <= 30
                 AND os.total_orders >= 3                   THEN 'Champion'
            WHEN DATEDIFF('day', os.last_order_date, CURRENT_DATE()) <= 60
                 AND os.total_orders >= 2                   THEN 'Loyal'
            WHEN DATEDIFF('day', os.last_order_date, CURRENT_DATE()) <= 90  THEN 'At Risk'
            WHEN os.total_orders IS NULL                    THEN 'No Purchase'
            ELSE 'Inactive'
        END                                                 AS rfm_segment,

        -- LTV tier
        CASE
            WHEN COALESCE(os.total_revenue, 0) >= 5000     THEN 'VIP'
            WHEN COALESCE(os.total_revenue, 0) >= 1000     THEN 'High Value'
            WHEN COALESCE(os.total_revenue, 0) >= 200      THEN 'Mid Value'
            WHEN COALESCE(os.total_revenue, 0) > 0         THEN 'Low Value'
            ELSE 'No Purchase'
        END                                                 AS ltv_tier,

        -- Metadata
        CURRENT_TIMESTAMP()                                 AS _mart_updated_at

    FROM customers c
    LEFT JOIN customer_order_stats os
        ON c.customer_id = os.customer_id
)

SELECT * FROM final
