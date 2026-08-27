WITH protocols AS (

    SELECT
        protocol_id,
        protocol_name,
        gecko_id,
        snapshot_at,
        tvl
    FROM {{ ref('stg_protocols') }}
    WHERE gecko_id IS NOT NULL
      AND tvl IS NOT NULL

),

coin_markets AS (

    SELECT
        coin_id,
        market_cap,
        snapshot_at
    FROM {{ ref('stg_coin_markets') }}
    WHERE market_cap IS NOT NULL

)

SELECT
    p.protocol_id,
    p.protocol_name,
    p.gecko_id,
    p.tvl AS protocol_tvl,
    c.market_cap,
    p.snapshot_at

FROM protocols p

INNER JOIN coin_markets c
    ON p.gecko_id = c.coin_id
   AND p.snapshot_at = c.snapshot_at