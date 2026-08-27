import requests
from datetime import datetime, timezone

import dlt


URL = "https://api.llama.fi/protocols"


@dlt.resource(
    name="protocols",
    write_disposition="merge",
    primary_key=["id", "snapshot_at"],
)
def protocols():
    response = requests.get(URL, timeout=30)
    response.raise_for_status()

    data = response.json()

    now = datetime.now(timezone.utc)
    snapshot_at = now.replace(
        minute=0,
        second=0,
        microsecond=0,
    )

    for protocol in data:
        protocol["snapshot_at"] = snapshot_at
        yield protocol


pipeline = dlt.pipeline(
    pipeline_name="defillama",
    destination="postgres",
    dataset_name="raw_defillama",
)


if __name__ == "__main__":
    load_info = pipeline.run(protocols())

    print(load_info)