with protocols as (

    select
        id as protocol_id,
        name as protocol_name,
        category,
        snapshot_at,
        "chain_tvls__ethereum",
        "chain_tvls__bitcoin",
        "chain_tvls__binance",
        "chain_tvls__solana",
        "chain_tvls__arbitrum",
        "chain_tvls__base",
        "chain_tvls__polygon",
        "chain_tvls__optimism",
        "chain_tvls__avalanche"
    from {{ source('defillama', 'protocols') }}

),

chain_tvl as (

    select
        protocol_id,
        protocol_name,
        category,
        'ethereum' as chain,
        "chain_tvls__ethereum" as tvl,
        snapshot_at
    from protocols
    where "chain_tvls__ethereum" is not null

    union all

    select
        protocol_id,
        protocol_name,
        category,
        'bitcoin' as chain,
        "chain_tvls__bitcoin" as tvl,
        snapshot_at
    from protocols
    where "chain_tvls__bitcoin" is not null

    union all

    select
        protocol_id,
        protocol_name,
        category,
        'binance' as chain,
        "chain_tvls__binance" as tvl,
        snapshot_at
    from protocols
    where "chain_tvls__binance" is not null

    union all

    select
        protocol_id,
        protocol_name,
        category,
        'solana' as chain,
        "chain_tvls__solana" as tvl,
        snapshot_at
    from protocols
    where "chain_tvls__solana" is not null

    union all

    select
        protocol_id,
        protocol_name,
        category,
        'arbitrum' as chain,
        "chain_tvls__arbitrum" as tvl,
        snapshot_at
    from protocols
    where "chain_tvls__arbitrum" is not null

    union all

    select
        protocol_id,
        protocol_name,
        category,
        'base' as chain,
        "chain_tvls__base" as tvl,
        snapshot_at
    from protocols
    where "chain_tvls__base" is not null

    union all

    select
        protocol_id,
        protocol_name,
        category,
        'polygon' as chain,
        "chain_tvls__polygon" as tvl,
        snapshot_at
    from protocols
    where "chain_tvls__polygon" is not null

    union all

    select
        protocol_id,
        protocol_name,
        category,
        'optimism' as chain,
        "chain_tvls__optimism" as tvl,
        snapshot_at
    from protocols
    where "chain_tvls__optimism" is not null

    union all

    select
        protocol_id,
        protocol_name,
        category,
        'avalanche' as chain,
        "chain_tvls__avalanche" as tvl,
        snapshot_at
    from protocols
    where "chain_tvls__avalanche" is not null

)

select *
from chain_tvl