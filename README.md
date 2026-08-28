# DeFi Analytics Platform

An end-to-end data engineering platform for ingesting, transforming, testing, and historically tracking DeFi protocol and crypto market data.

The project integrates **DeFiLlama** and **CoinGecko**, loads raw data into PostgreSQL with `dlt`, transforms it using `dbt`, validates data quality, and orchestrates the complete pipeline with Prefect.

## Project Status

**V1 Complete — Local End-to-End Data Pipeline**

The project successfully demonstrates:

- multi-source API ingestion
- incremental historical snapshots
- idempotent data loading
- API pagination
- rate-limit handling and retries
- PostgreSQL data warehousing
- dbt transformations
- staging, intermediate, and mart data models
- cross-source entity resolution
- automated data-quality testing
- pipeline logging and error handling
- Prefect orchestration
- automated hourly scheduling
- Git/GitHub version control

The V1 pipeline has been validated through successful automatic scheduled execution.

Further development is intentionally frozen at this stage.

The engineering patterns developed in this project provide the foundation for a separate treasury-intelligence data platform focused on evaluating liquid yield opportunities for corporate and institutional capital.

---

## Architecture

```text
DeFiLlama API ─────┐
                   │
                   ├──> Python + dlt
                   │        │
CoinGecko API ─────┘        │
                            ↓
                       PostgreSQL
                            │
                            ↓
                           dbt
                            │
               ┌────────────┼────────────┐
               ↓            ↓            ↓
            Staging    Intermediate     Marts
                                         │
                                         ↓
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
- Git
- GitHub

---

# Data Sources

## DeFiLlama

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

## CoinGecko

CoinGecko provides crypto market-cap data used to enrich DeFiLlama protocols.

The ingestion pipeline:

- fetches up to approximately 2,500 assets
- uses API pagination
- retrieves up to 250 assets per page
- handles HTTP 429 rate limits
- retries requests using exponential backoff
- stores hourly snapshots
- uses merge-based loading for idempotency

Only fields required by the project are ingested:

- coin ID
- symbol
- coin name
- market cap
- snapshot timestamp

This keeps ingestion scoped to actual downstream data requirements.

---

# Data Pipeline

The pipeline follows a layered data-engineering architecture:

```text
External APIs
     ↓
Python ingestion
     ↓
dlt
     ↓
Raw PostgreSQL schemas
     ↓
dbt staging
     ↓
dbt intermediate models
     ↓
dbt marts
     ↓
dbt tests

```

---

# Raw Data

## DeFiLlama

Schema:

```text
raw_defillama

```

Main table:

```text
raw_defillama.protocols

```

## CoinGecko

Schema:

```text
raw_coingecko

```

Main table:

```text
raw_coingecko.coin_markets

```

---

# dbt Transformation Layer

## Staging

Staging models clean and standardize raw source data.

```text
stg_protocols
stg_coin_markets

```

## Intermediate

Intermediate models handle reshaping and cross-source integration.

```text
int_protocol_chain_tvl
int_protocol_market_cap

```

`int_protocol_market_cap` joins DeFiLlama protocols with CoinGecko market-cap observations using:

```text
DeFiLlama gecko_id = CoinGecko coin_id

```

and matching hourly snapshots.

## Marts

Current analytics-ready marts include:

```text
mart_protocol_tvl
mart_protocol_tvl_change

mart_chain_tvl
mart_chain_tvl_change

mart_category_tvl
mart_category_tvl_change

mart_protocol_market_cap

```

---

# Multi-Source Integration

DeFiLlama exposes a `gecko_id`, allowing protocol records to be matched against CoinGecko assets.

Initial CoinGecko ingestion included only the top 250 assets.

This produced:

```text
31 matched protocols

```

Expanding ingestion through pagination to approximately 2,500 assets increased this to:

```text
290 matched protocols

```

from approximately:

```text
2,350 DeFiLlama protocols containing a CoinGecko ID

```

giving approximately:

```text
12.34% coverage

```

This represented roughly a **9.4x increase in cross-source matching**.

An important modeling lesson from this integration was that matching identifiers alone is insufficient.

The observations must also have compatible temporal grain.

Both pipelines therefore create normalized hourly snapshots.

---

# Protocol Market-Cap Mart

`mart_protocol_market_cap` combines protocol fundamentals with market valuation data.

The mart contains:

- protocol ID
- protocol name
- CoinGecko ID
- protocol TVL
- market capitalization
- TVL-to-market-cap ratio
- snapshot timestamp

The derived ratio is:

```text
protocol TVL / token market cap

```

The mart grain is:

```text
one row per protocol per hourly snapshot

```

A custom dbt test validates this uniqueness assumption.

---

# Historical Snapshots

Both sources are stored as historical observations rather than simply overwriting the latest state.

Snapshots are normalized to an hourly grain:

```text
YYYY-MM-DD HH:00:00 UTC

```

This allows the warehouse to accumulate historical observations for:

- trend analysis
- change detection
- cross-source comparison
- future signal generation

---

# Idempotency

Both ingestion pipelines use `dlt` merge loading.

Logical source keys include the entity identifier and hourly snapshot timestamp.

As a result, rerunning ingestion during the same hour does not create duplicate logical observations.

This also makes Prefect retries safe.

---

# CoinGecko Pagination

The CoinGecko ingestion pipeline retrieves multiple pages of market data.

Configuration:

```text
250 assets per page
up to 10 pages
≈ 2,500 assets

```

Pagination materially increased the number of DeFiLlama protocols that could be enriched with market-cap data.

---

# Rate-Limit Handling

The CoinGecko public API can return:

```text
HTTP 429 Too Many Requests

```

The pipeline handles rate limits with exponential backoff.

Example:

```text
5 seconds
10 seconds
20 seconds
40 seconds
80 seconds

```

The pipeline also pauses between successful page requests.

This prevents temporary API throttling from immediately failing ingestion.

---

# Scoped Ingestion

During development, ingesting the complete CoinGecko API response exposed integer values outside the supported serialization range for lower-ranked assets.

Rather than storing unused fields, the pipeline was narrowed to the fields actually required downstream:

```text
id
symbol
name
market_cap
snapshot_at

```

This keeps the raw model aligned with current data requirements and avoids unnecessary schema complexity.

---

# Data Quality

dbt tests validate important assumptions across staging and mart models.

Current checks include:

- required identifiers are not null
- protocol names are not null
- coin names are not null
- market caps are not null
- snapshot timestamps are not null
- protocol-market-cap mart grain is unique by protocol and snapshot

The project currently passes:

```text
17 dbt tests

```

A custom singular test validates that:

```text
protocol_id + snapshot_at

```

is unique in `mart_protocol_market_cap`.

---

# Orchestration

Prefect orchestrates the complete pipeline.

The flow executes:

```text
ingest_defillama ──┐
                   ├──> dbt run ──> dbt test
ingest_coingecko ──┘

```

Both ingestion tasks must complete before transformations begin.

Ingestion tasks also use automatic retries for transient failures.

---

# Scheduling

The pipeline is scheduled locally using a Prefect deployment.

Deployment:

```text
defi-analytics-pipeline/hourly-defi-analytics

```

Schedule:

```text
0 * * * *

```

This executes the pipeline automatically at the top of every hour.

The scheduled deployment is served through:

```text
orchestration/serve.py

```

The complete scheduled execution path is:

```text
Prefect Server
      ↓
Hourly Deployment
      ↓
Prefect Flow Runner
      ↓
DeFiLlama + CoinGecko ingestion
      ↓
dbt run
      ↓
dbt test

```

Automatic scheduling was validated with a successful unattended run in which:

```text
ingest_defillama → Completed
ingest_coingecko → Completed
dbt_run          → Completed
dbt_test         → Completed
flow run         → Completed

```

---

# Observability

The project includes basic operational visibility through:

- structured Python logging
- pipeline execution durations
- terminal logs
- persistent pipeline logs
- captured subprocess output
- Prefect task states
- Prefect flow-run history
- explicit failure handling

This provides enough observability for the current local V1 architecture.

---

# Running Locally

## 1. Activate the virtual environment

Git Bash:

```bash
source .venv/Scripts/activate

```

## 2. Start PostgreSQL

```bash
docker compose up -d

```

Verify:

```bash
docker compose ps

```

## 3. Run the complete pipeline manually

```bash
python orchestration/flows.py

```

## 4. Run dbt models

```bash
dbt run --project-dir dbt

```

## 5. Run dbt tests

```bash
dbt test --project-dir dbt

```

## 6. Connect to PostgreSQL

```bash
docker exec -it defi-postgres psql -U defi_user -d defi_analytics

```

Exit:

```text
\q

```

---

# Running the Hourly Scheduler

Local scheduling requires the PostgreSQL container and two long-running Prefect processes.

## Terminal 1 — Prefect server

```bash
source .venv/Scripts/activate
prefect server start

```

## Terminal 2 — Flow server

```bash
source .venv/Scripts/activate
python orchestration/serve.py

```

The Prefect UI is available locally at:

```text
http://127.0.0.1:4200

```

The machine, PostgreSQL container, Prefect server, and flow server must remain running for scheduled executions to occur.

---

# Project Structure

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
├── docker-compose.yml
├── .gitignore
└── README.md

```

---

# What This Project Demonstrates

This project was intentionally developed incrementally.

New technologies were introduced when an engineering problem justified them:

```text
Need persistent local storage
→ PostgreSQL + Docker

Need repeatable API ingestion
→ Python + dlt

Need transformation layers
→ dbt

Need data-quality validation
→ dbt tests

Need historical observations
→ hourly snapshots

Need safe reruns
→ merge-based idempotency

Need operational visibility
→ logging and error handling

Need pipeline dependencies and retries
→ Prefect

Need richer protocol context
→ second data source

Need broader entity coverage
→ API pagination

Need reliable external API ingestion
→ rate-limit handling

Need automatic historical collection
→ Prefect scheduling

```

The objective was not to accumulate technologies for their own sake, but to introduce infrastructure as the pipeline developed requirements for it.

---

# V1 Conclusion

The local V1 data-engineering platform is complete.

It successfully:

1. collects data from multiple external APIs
2. persists historical snapshots
3. handles pagination and external API rate limits
4. prevents duplicate logical observations
5. transforms raw data through layered dbt models
6. integrates independent data sources
7. produces analytics-ready marts
8. validates data-quality assumptions
9. orchestrates dependencies and retries
10. executes automatically on an hourly schedule

The next project builds on these engineering foundations but starts from a business problem rather than an infrastructure objective:

> Build data infrastructure for evaluating liquid yield opportunities for corporate and institutional treasury capital.

That project is intentionally maintained separately so this repository remains a focused example of an end-to-end DeFi data-engineering pipeline.