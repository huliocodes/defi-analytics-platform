import logging
import subprocess
import sys
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "pipeline.log"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


def run(command, step_name):
    command_str = " ".join(command)

    logger.info("START | %s | %s", step_name, command_str)

    started_at = time.perf_counter()

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
    )

    duration = time.perf_counter() - started_at

    if result.returncode != 0:
        logger.error(
            "FAILED | %s | exit_code=%s | duration=%.2fs",
            step_name,
            result.returncode,
            duration,
        )

        if result.stdout:
            logger.error("STDOUT:\n%s", result.stdout)

        if result.stderr:
            logger.error("STDERR:\n%s", result.stderr)

        sys.exit(result.returncode)

    logger.info(
        "SUCCESS | %s | duration=%.2fs",
        step_name,
        duration,
    )


def main():
    pipeline_started_at = time.perf_counter()

    logger.info("=" * 60)
    logger.info("PIPELINE START")
    logger.info("=" * 60)

    run(
        [
            sys.executable,
            "ingestion/defillama_pipeline.py",
        ],
        "defillama_ingestion",
    )

    run(
        [
            "dbt",
            "run",
            "--project-dir",
            "dbt",
        ],
        "dbt_run",
    )

    run(
        [
            "dbt",
            "test",
            "--project-dir",
            "dbt",
        ],
        "dbt_test",
    )

    total_duration = time.perf_counter() - pipeline_started_at

    logger.info("=" * 60)
    logger.info(
        "PIPELINE SUCCESS | total_duration=%.2fs",
        total_duration,
    )
    logger.info("=" * 60)


if __name__ == "__main__":
    main()