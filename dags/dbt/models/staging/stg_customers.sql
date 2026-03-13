-- ============================================================
-- stg_customers.sql
-- Layer: Staging
-- Source: RAW.CUSTOMERS
-- ============================================================

WITH source AS (
    SELECT * FROM {{ source('raw', 'customers') }}
),

staged AS (
    SELECT
        customer_id,

        -- Name cleanup
        INITCAP(TRIM(first_name))               AS first_name,
        INITCAP(TRIM(last_name))                AS last_name,
        LOWER(TRIM(email))                      AS email,
        TRIM(phone)                             AS phone,

        -- Dates
        TRY_TO_DATE(date_of_birth, 'YYYY-MM-DD') AS date_of_birth,
        TRY_TO_DATE(signup_date, 'YYYY-MM-DD')   AS signup_date,

        -- Demographics
        UPPER(TRIM(gender))                     AS gender,
        INITCAP(TRIM(country))                  AS country,
        INITCAP(TRIM(city))                     AS city,

        -- Segment
        UPPER(TRIM(customer_segment))           AS customer_segment,

        -- Boolean
        CASE
            WHEN UPPER(TRIM(is_active)) IN ('TRUE', '1', 'YES', 'Y') THEN TRUE
            ELSE FALSE
        END                                     AS is_active,

        -- Derived
        CONCAT(INITCAP(TRIM(first_name)), ' ', INITCAP(TRIM(last_name)))
                                                AS full_name,

        -- Metadata
        _source_file,
        _source_loaded_at,
        _batch_id

    FROM source
    WHERE customer_id IS NOT NULL
      AND customer_id != 'null'
)

SELECT * FROM staged
