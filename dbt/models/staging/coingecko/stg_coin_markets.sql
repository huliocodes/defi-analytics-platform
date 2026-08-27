SELECT
    id AS coin_id,
    symbol,
    name AS coin_name,
    market_cap::double precision AS market_cap,
    snapshot_at
FROM {{ source('coingecko', 'coin_markets') }}