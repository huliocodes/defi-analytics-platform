# DeFi Analytics Platform

A data engineering project that ingests DeFi and crypto market data from multiple APIs, transforms it with dbt, validates data quality, and orchestrates the full pipeline with Prefect.

The project is designed to demonstrate an end-to-end modern data engineering workflow using Python, PostgreSQL, dlt, dbt, Docker, and Prefect.

## Architecture

```text
DeFiLlama API ─────┐
                   │
                   ├──> Python + dlt
                   │        │
CoinGecko API ─────┘        │
                            v
                       PostgreSQL
                            │
                            v
                           dbt
                   Bronze / Staging
                            │
                            v
                       Intermediate
                            │
                            v
                          Marts
                            │
                            v
                       dbt Tests

Prefect orchestrates the complete workflow.

```

## Tech Stack

- Python
- requests
- dlt
- PostgreSQL
- Docker
- dbt
- Prefect
- Git / GitHub

## Data Sources

### DeFiLlama

The DeFiLlama pipeline ingests protocol-level DeFi data including:

- protocol ID
- protocol name
- category
- chain
- TVL
- short-term TVL changes
- CoinGecko identifier
- protocol metadata

Each ingestion run creates an hourly snapshot.

The pipeline uses a merge strategy with:

```text
protocol_id + snapshot_at

```

as the logical snapshot grain, making same-hour reruns idempotent.

### CoinGecko

CoinGecko provides token market-cap data used to enrich DeFiLlama protocols.

The ingestion pipeline:

- fetches up to 2,500 coins
- uses API pagination
- retrieves 250 coins per page
- handles HTTP 429 rate limits with retry and exponential backoff
- stores hourly snapshots
- uses merge-based loading for idempotency

Only fields currently required by the project are ingested:

- coin ID
- symbol
- coin name
- market cap
- snapshot timestamp

This keeps the raw ingestion aligned with the current data requirements.

## Data Pipeline

The pipeline follows these stages:

```text
API ingestion
    ↓
Raw PostgreSQL schemas
    ↓
dbt staging models
    ↓
dbt intermediate models
    ↓
dbt marts
    ↓
dbt tests

```

## Raw Schemas

### DeFiLlama

```text
raw_defillama

```

Main table:

```text
raw_defillama.protocols

```

### CoinGecko

```text
raw_coingecko

```

Main table:

```text
raw_coingecko.coin_markets

```

## dbt Models

### Staging

Staging models clean and standardize raw API data.

```text
stg_protocols
stg_coin_markets

```

### Intermediate

Intermediate models handle reshaping and multi-source integration.

```text
int_protocol_chain_tvl
int_protocol_market_cap

```

`int_protocol_market_cap` joins DeFiLlama protocols with CoinGecko market-cap data using:

```text
DeFiLlama gecko_id = CoinGecko coin_id

```

and matching hourly snapshots.

### Marts

Current analytics-ready marts:

```text
mart_protocol_tvl
mart_protocol_tvl_change
mart_chain_tvl
mart_chain_tvl_change
mart_category_tvl
mart_category_tvl_change
mart_protocol_market_cap

```

### Protocol Market Cap Mart

`mart_protocol_market_cap` combines protocol TVL with token market capitalization.

It contains:

- protocol ID
- protocol name
- CoinGecko ID
- protocol TVL
- market cap
- TVL-to-market-cap ratio
- snapshot timestamp

The derived ratio is calculated as:

```text
protocol TVL / token market cap

```

## Multi-Source Integration

The project currently integrates two independent APIs:

```text
DeFiLlama
+
CoinGecko

```

DeFiLlama already exposes a `gecko_id`, which provides a reliable entity-resolution key for joining protocols to CoinGecko assets.

Initial CoinGecko ingestion included only the top 250 assets and matched 31 DeFiLlama protocols.

After implementing pagination to ingest approximately 2,500 assets, the integration matched:

```text
290 protocols

```

out of:

```text
2,350 DeFiLlama protocols with a CoinGecko ID

```

for approximately:

```text
12.34% coverage

```

This increased cross-source matching by roughly 9.4x.

## Data Quality

dbt tests validate important assumptions in staging and mart models.

Current checks include:

- required identifiers are not null
- protocol names are not null
- coin names are not null
- market caps are not null
- snapshot timestamps are not null

The project currently passes all configured dbt tests.

## Idempotency

Both ingestion pipelines use hourly snapshots.

Repeated ingestion within the same hour does not create duplicate logical snapshots because dlt uses merge-based loading with source identifiers and snapshot timestamps as keys.

This makes local reruns and orchestration retries safe.

## Rate Limit Handling

The CoinGecko keyless API may return:

```text
HTTP 429 Too Many Requests

```

The ingestion pipeline handles this using exponential retry delays.

Example retry sequence:

```text
5 seconds
10 seconds
20 seconds
40 seconds
80 seconds

```

This allows pagination to continue without immediately failing the pipeline.

## Orchestration

Prefect orchestrates the complete data workflow.

The current flow runs:

```text
ingest_defillama
        │
        ├─────────────┐
        │             │
        │       ingest_coingecko
        │             │
        └──────┬──────┘
               ↓
            dbt run
               ↓
            dbt test

```

Both API ingestion tasks must complete successfully before dbt transformations begin.

The ingestion tasks also include Prefect retry behavior.

## Running the Project Locally

### 1. Activate the Python environment

Git Bash:

```bash
source .venv/Scripts/activate

```

### 2. Start PostgreSQL

```bash
docker compose up -d

```

Check the container:

```bash
docker compose ps

```

### 3. Run the complete orchestrated pipeline

```bash
python orchestration/flows.py

```

This runs:

```text
DeFiLlama ingestion
CoinGecko ingestion
dbt run
dbt test

```

### 4. Run individual components

DeFiLlama:

```bash
python ingestion/defillama_pipeline.py

```

CoinGecko:

```bash
python ingestion/coingecko_pipeline.py

```

dbt models:

```bash
dbt run --project-dir dbt

```

dbt tests:

```bash
dbt test --project-dir dbt

```

### 5. Connect to PostgreSQL

```bash
docker exec -it defi-postgres psql -U defi_user -d defi_analytics

```

Exit PostgreSQL with:

```text
\q

```

## Project Structure

```text
defi-analytics-platform/
│
├── ingestion/
│   ├── defillama_pipeline.py
│   └── coingecko_pipeline.py
│
├── orchestration/
│   └── flows.py
│
├── scripts/
│   └── run_pipeline.py
│
├── dbt/
│   ├── models/
│   │   ├── staging/
│   │   │   ├── defillama/
│   │   │   └── coingecko/
│   │   ├── intermediate/
│   │   └── marts/
│   │
│   └── macros/
│
├── logs/
│
├── docker-compose.yml
├── .gitignore
└── README.md

```

## Current Status

Completed:

- local PostgreSQL environment with Docker
- DeFiLlama API ingestion
- CoinGecko API ingestion
- dlt loading
- hourly snapshots
- idempotent ingestion
- CoinGecko pagination
- API rate-limit handling
- dbt staging models
- dbt intermediate models
- dbt marts
- cross-source integration
- protocol TVL + market-cap mart
- data quality tests
- pipeline logging
- error handling
- Prefect orchestration
- Git/GitHub version control

Potential future improvements:

- scheduled Prefect deployments
- persistent Prefect server
- cloud deployment
- CI/CD
- additional DeFi data sources
- broader CoinGecko entity coverage
- historical backfills
- pipeline monitoring and alerting

