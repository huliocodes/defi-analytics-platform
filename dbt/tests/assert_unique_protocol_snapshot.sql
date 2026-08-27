SELECT
    protocol_id,
    snapshot_at,
    COUNT(*) AS row_count
FROM {{ ref('mart_protocol_tvl') }}
GROUP BY
    protocol_id,
    snapshot_at
HAVING COUNT(*) > 1