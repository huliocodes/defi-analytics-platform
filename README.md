# DeFi Analytics Platform

A data engineering project that ingests DeFi and crypto market data from multiple APIs, transforms it with dbt, validates data quality, and orchestrates the full pipeline with Prefect.

The project demonstrates an end-to-end modern data engineering workflow using Python, PostgreSQL, dlt, dbt, Docker, Prefect, and Git.

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
                   Staging Models
                            │
                            v
                    Intermediate Models
                            │
                            v
                          Marts
                            │
                            v
                       dbt Tests

Prefect orchestrates and schedules the complete workflow.

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

The pipeline uses merge-based loading with the logical key:

```text
protocol_id + snapshot_at

```

This makes same-hour reruns idempotent.

### CoinGecko

CoinGecko provides token market-cap data used to enrich DeFiLlama protocols.

The ingestion pipeline:

- fetches up to 2,500 coins
- uses API pagination
- retrieves 250 coins per page
- handles HTTP 429 rate limits
- retries requests using exponential backoff
- stores hourly snapshots
- uses merge-based loading for idempotency

Only fields currently required by the project are ingested:

- coin ID
- symbol
- coin name
- market cap
- snapshot timestamp

This keeps ingestion aligned with the current data requirements.

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

The mart grain is:

```text
one row per protocol per hourly snapshot

```

A custom dbt test validates this uniqueness assumption.

## Multi-Source Integration

The project currently integrates two independent APIs:

```text
DeFiLlama
+
CoinGecko

```

DeFiLlama exposes a `gecko_id`, which provides a reliable entity-resolution key for joining protocols to CoinGecko assets.

Initial CoinGecko ingestion included only the top 250 assets and matched:

```text
31 protocols

```

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
- protocol market-cap mart grain is unique by protocol and snapshot

The project currently passes:

```text
17 dbt tests

```

## Idempotency

Both ingestion pipelines use hourly snapshots.

Repeated ingestion within the same hour does not create duplicate logical snapshots because dlt uses merge-based loading with source identifiers and snapshot timestamps as keys.

This makes local reruns and Prefect retries safe.

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

This allows pagination to continue instead of immediately failing the pipeline.

## Orchestration

Prefect orchestrates the complete workflow.

The current flow runs:

```text
ingest_defillama ──┐
                   ├──> dbt run ──> dbt test
ingest_coingecko ──┘

```

Both API ingestion tasks must complete successfully before dbt transformations begin.

The ingestion tasks also include Prefect retry behavior.

## Scheduling

The pipeline is scheduled locally using Prefect.

The deployment is:

```text
defi-analytics-pipeline/hourly-defi-analytics

```

The cron schedule is:

```text
0 * * * *

```

This schedules the pipeline once per hour at the top of the hour.

The scheduled deployment is served by:

```text
orchestration/serve.py

```

The local scheduling architecture is:

```text
Prefect Server
      │
      ↓
Hourly Deployment
      │
      ↓
Prefect Flow Runner
      │
      ↓
DeFiLlama + CoinGecko ingestion
      │
      ↓
dbt run
      │
      ↓
dbt test

```

The hourly schedule has been validated with a fully automatic run.

A scheduled run successfully executed:

```text
ingest_defillama → Completed
ingest_coingecko → Completed
dbt_run          → Completed
dbt_test         → Completed
flow run         → Completed

```

## Local Prefect Setup

The local scheduled pipeline requires two long-running processes.

### Prefect server

In one terminal:

```bash
source .venv/Scripts/activate
prefect server start

```

### Flow server

In another terminal:

```bash
source .venv/Scripts/activate
python orchestration/serve.py

```

The Prefect UI is available locally at:

```text
http://127.0.0.1:4200

```

A third terminal can be used normally for development commands such as Git, dbt, and PostgreSQL.

Because scheduling is currently local, the PC, PostgreSQL, Prefect server, and flow server must be running for scheduled executions to occur.

A future cloud deployment would remove this limitation.

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

### 3. Run the complete pipeline manually

```bash
python orchestration/flows.py

```

### 4. Run the scheduled deployment locally

Start the Prefect server:

```bash
prefect server start

```

Then, in another terminal:

```bash
python orchestration/serve.py

```

### 5. Run individual ingestion pipelines

DeFiLlama:

```bash
python ingestion/defillama_pipeline.py

```

CoinGecko:

```bash
python ingestion/coingecko_pipeline.py

```

### 6. Run dbt

Models:

```bash
dbt run --project-dir dbt

```

Tests:

```bash
dbt test --project-dir dbt

```

### 7. Connect to PostgreSQL

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
│   ├── flows.py
│   └── serve.py
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
│   ├── tests/
│   │   └── assert_mart_protocol_market_cap_unique.sql
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
- custom mart-grain uniqueness test
- pipeline logging
- error handling
- Prefect orchestration
- Prefect deployment
- hourly scheduled execution
- successful automatic scheduled run
- Git/GitHub version control

Potential future improvements:

- persistent production Prefect deployment
- cloud deployment
- CI/CD
- historical backfills
- improved cross-source time alignment
- pipeline monitoring and alerting
- additional DeFi data sources
- broader CoinGecko entity coverage

