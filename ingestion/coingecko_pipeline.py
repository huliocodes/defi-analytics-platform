import requests
from datetime import datetime, timezone

import dlt


URL = "https://api.coingecko.com/api/v3/coins/markets"


@dlt.resource(
    name="coin_markets",
    write_disposition="append",
)
def coin_markets():
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 250,
        "page": 1,
        "sparkline": "false",
    }

    response = requests.get(
        URL,
        params=params,
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()

    now = datetime.now(timezone.utc)
    snapshot_at = now.replace(
        minute=0,
        second=0,
        microsecond=0,
    )

    for coin in data:
        coin["snapshot_at"] = snapshot_at
        yield coin


pipeline = dlt.pipeline(
    pipeline_name="coingecko",
    destination="postgres",
    dataset_name="raw_coingecko",
)


if __name__ == "__main__":
    load_info = pipeline.run(coin_markets())

    print(load_info)