WITH orders AS (
    SELECT * FROM SHOPSTREAM_DB.STAGING_staging.stg_orders
),

final AS (
    SELECT
        order_id,
        customer_id,
        order_date,
        order_status,
        payment_method,
        payment_status,
        currency,
        shipping_address,
        total_amount,
        discount_amount,
        tax_amount,
        net_amount,

        CASE
            WHEN order_status = 'COMPLETED'  THEN 'Revenue'
            WHEN order_status = 'RETURNED'   THEN 'Refund'
            WHEN order_status = 'CANCELLED'  THEN 'Lost'
            WHEN order_status = 'PENDING'    THEN 'In Progress'
            ELSE 'Other'
        END AS order_category,

        CASE
            WHEN net_amount >= 1000 THEN 'High Value'
            WHEN net_amount >= 300  THEN 'Mid Value'
            ELSE 'Low Value'
        END AS order_value_tier,

        _source_loaded_at,
        _batch_id

    FROM orders
)

SELECT * FROM final