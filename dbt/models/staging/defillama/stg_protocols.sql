SELECT
    id AS protocol_id,
    name AS protocol_name,
    slug,
    gecko_id,
    category,
    chain,
    symbol,
    url,
    tvl,
    change_1h,
    change_1d,
    change_7d,
    snapshot_at
FROM {{ source('defillama', 'protocols') }}