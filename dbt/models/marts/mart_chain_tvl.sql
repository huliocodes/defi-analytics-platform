SELECT
    chain,
    snapshot_at,
    SUM(tvl) AS total_tvl
FROM {{ ref('int_protocol_chain_tvl') }}
GROUP BY
    chain,
    snapshot_at