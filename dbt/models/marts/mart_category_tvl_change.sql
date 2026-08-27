WITH category_tvl AS (

    SELECT
        category,
        snapshot_at,
        total_tvl
    FROM {{ ref('mart_category_tvl') }}

),

with_previous AS (

    SELECT
        category,
        snapshot_at,
        total_tvl,

        LAG(total_tvl) OVER (
            PARTITION BY category
            ORDER BY snapshot_at
        ) AS previous_tvl

    FROM category_tvl

)

SELECT
    category,
    snapshot_at,
    previous_tvl,
    total_tvl,
    total_tvl - previous_tvl AS tvl_change,

    CASE
        WHEN previous_tvl IS NULL OR previous_tvl = 0
            THEN NULL
        ELSE
            100.0 * (total_tvl - previous_tvl) / previous_tvl
    END AS tvl_change_pct

FROM with_previous