with protocol_tvl as (

    select
        protocol_id,
        protocol_name,
        category,
        snapshot_at,
        sum(tvl) as total_tvl
    from {{ ref('int_protocol_chain_tvl') }}
    group by
        protocol_id,
        protocol_name,
        category,
        snapshot_at

)

select
    protocol_id,
    protocol_name,
    category,
    total_tvl,
    snapshot_at
from protocol_tvl