import time
from datetime import datetime, timezone

import dlt
import requests

URL = "https://api.coingecko.com/api/v3/coins/markets"

PER_PAGE = 250
MAX_PAGES = 10
MAX_RETRIES = 5


@dlt.resource(
    name="coin_markets",
    write_disposition="merge",
    primary_key=["id", "snapshot_at"],
)
def coin_markets():
    now = datetime.now(timezone.utc)
    snapshot_at = now.replace(
        minute=0,
        second=0,
        microsecond=0,
    )

    for page in range(1, MAX_PAGES + 1):
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": PER_PAGE,
            "page": page,
            "sparkline": "false",
        }

        for attempt in range(MAX_RETRIES):
            response = requests.get(
                URL,
                params=params,
                timeout=30,
            )

            if response.status_code == 429:
                wait_seconds = 2 ** attempt * 5
                print(
                    f"Rate limited on page {page}. "
                    f"Retrying in {wait_seconds}s..."
                )
                time.sleep(wait_seconds)
                continue

            response.raise_for_status()
            break

        else:
            raise RuntimeError(
                f"Failed to fetch page {page} after {MAX_RETRIES} retries"
            )

        data = response.json()

        if not data:
            break

        print(f"Fetched page {page}: {len(data)} coins")

        for coin in data:
            coin["snapshot_at"] = snapshot_at
            yield {
                "id": coin["id"],
                "symbol": coin["symbol"],
                "name": coin["name"],
                "market_cap": coin["market_cap"],
                "snapshot_at": snapshot_at,
            }

        if len(data) < PER_PAGE:
            break

        time.sleep(3)


pipeline = dlt.pipeline(
    pipeline_name="coingecko",
    destination="postgres",
    dataset_name="raw_coingecko",
)


if __name__ == "__main__":
    load_info = pipeline.run(coin_markets())
    print(load_info)