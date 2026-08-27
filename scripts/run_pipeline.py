import logging
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "pipeline.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


def run(command):
    command_str = " ".join(command)

    print(f"\n>>> {command_str}")
    logger.info("Starting: %s", command_str)

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
    )

    if result.returncode != 0:
        logger.error(
            "Command failed with exit code %s: %s",
            result.returncode,
            command_str,
        )
        print(f"\nPipeline failed: {command_str}")
        sys.exit(result.returncode)

    logger.info("Completed successfully: %s", command_str)


logger.info("========== PIPELINE START ==========")

run([
    sys.executable,
    "ingestion/defillama_pipeline.py",
])

run([
    "dbt",
    "run",
    "--project-dir",
    "dbt",
])

run([
    "dbt",
    "test",
    "--project-dir",
    "dbt",
])

logger.info("========== PIPELINE SUCCESS ==========")

print("\nPipeline completed successfully.")