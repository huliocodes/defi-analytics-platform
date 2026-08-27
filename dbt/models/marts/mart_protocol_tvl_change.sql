WITH protocol_tvl AS (

    SELECT
        protocol_id,
        protocol_name,
        category,
        snapshot_at,
        total_tvl
    FROM {{ ref('mart_protocol_tvl') }}

),

with_previous AS (

    SELECT
        protocol_id,
        protocol_name,
        category,
        snapshot_at,
        total_tvl,

        LAG(total_tvl) OVER (
            PARTITION BY protocol_id
            ORDER BY snapshot_at
        ) AS previous_tvl

    FROM protocol_tvl

)

SELECT
    protocol_id,
    protocol_name,
    category,
    snapshot_at,
    previous_tvl,
    total_tvl,

    CASE
        WHEN previous_tvl IS NULL
            THEN NULL
        ELSE total_tvl - previous_tvl
    END AS tvl_change,

    CASE
        WHEN previous_tvl IS NULL OR previous_tvl = 0
            THEN NULL
        ELSE
            100.0 * (total_tvl - previous_tvl) / previous_tvl
    END AS tvl_change_pct

FROM with_previous