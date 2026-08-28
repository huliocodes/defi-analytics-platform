SELECT
    protocol_id,
    protocol_name,
    gecko_id,
    protocol_tvl,
    market_cap,

    CASE
        WHEN market_cap > 0
        THEN protocol_tvl / market_cap
    END AS tvl_to_market_cap_ratio,

    snapshot_at

FROM {{ ref('int_protocol_market_cap') }}