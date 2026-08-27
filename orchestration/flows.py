import subprocess
import sys
from pathlib import Path

from prefect import flow, task


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def run_command(command: list[str]) -> None:
    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(command)}\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )


@task(retries=2, retry_delay_seconds=30)
def ingest_defillama():
    run_command([
        sys.executable,
        "ingestion/defillama_pipeline.py",
    ])


@task
def dbt_run():
    run_command([
        "dbt",
        "run",
        "--project-dir",
        "dbt",
    ])


@task
def dbt_test():
    run_command([
        "dbt",
        "test",
        "--project-dir",
        "dbt",
    ])


@flow(name="defi-analytics-pipeline")
def defi_analytics_flow():
    ingestion = ingest_defillama()

    transformations = dbt_run(
        wait_for=[ingestion]
    )

    dbt_test(
        wait_for=[transformations]
    )


if __name__ == "__main__":
    defi_analytics_flow()