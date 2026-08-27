SELECT
    category,
    snapshot_at,
    SUM(tvl) AS total_tvl
FROM {{ ref('int_protocol_chain_tvl') }}
GROUP BY
    category,
    snapshot_at