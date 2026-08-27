# DeFi Analytics Platform

A data engineering pipeline that ingests DeFi protocol TVL data from DeFiLlama, stores historical snapshots in PostgreSQL, and transforms the data into analytics-ready datasets with dbt.

## Architecture

```text
DeFiLlama API
      ↓
Python + dlt
      ↓
PostgreSQL
      ↓
dbt
      ↓
┌─────────────────────────────┐
│ Staging                     │
│ Intermediate                │
│ Analytics Marts             │
└─────────────────────────────┘
```

## Tech Stack

- Python
- dlt
- PostgreSQL
- Docker
- dbt
- Git / GitHub

## Data Pipeline

The ingestion pipeline retrieves protocol data from the DeFiLlama API and stores timestamped snapshots in PostgreSQL.

dbt then transforms the raw data into:

- Protocol-level TVL
- Chain-level TVL
- Category-level TVL
- Protocol TVL changes
- Chain TVL changes
- Category TVL changes

## dbt Models

### Staging

`stg_protocols`

Cleans and standardizes the raw DeFiLlama protocol data.

### Intermediate

`int_protocol_chain_tvl`

Transforms chain-level TVL fields into a normalized protocol/chain structure.

### Marts

- `mart_protocol_tvl`
- `mart_chain_tvl`
- `mart_category_tvl`
- `mart_protocol_tvl_change`
- `mart_chain_tvl_change`
- `mart_category_tvl_change`

These models provide analytics-ready datasets for downstream analysis and visualization.

## Data Quality

The project includes dbt data tests for important fields such as:

- Protocol IDs
- Protocol names
- TVL values
- Snapshot timestamps

Run the tests with:

```bash
dbt test --project-dir dbt
```

## Running Locally

Start PostgreSQL:

```bash
docker compose up -d
```

Run the complete pipeline:

```bash
python scripts/run_pipeline.py
```

The pipeline runs:

1. DeFiLlama ingestion
2. dbt transformations
3. dbt data tests

## Project Structure

```text
.
├── ingestion/
│   ├── defillama_pipeline.py
│   └── inspect_defillama.py
├── dbt/
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   └── marts/
│   ├── macros/
│   └── dbt_project.yml
├── scripts/
│   └── run_pipeline.py
├── tests/
├── docker-compose.yaml
├── requirements.txt
└── README.md
```

## Current Status

The local pipeline is fully operational.

- API ingestion: complete
- PostgreSQL storage: complete
- dbt transformations: complete
- Analytics marts: complete
- Data quality tests: complete
- End-to-end pipeline runner: complete
- Hourly production scheduling: planned
- Cloud deployment: planned

