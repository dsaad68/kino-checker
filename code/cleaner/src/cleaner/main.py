from __future__ import annotations

import time
from pathlib import Path

from loguru import logger

from cleaner.utils.db_cleaner import DBCleaner
from common.config import DatabaseConfig
from common.constants import CLEANER_POLL_INTERVAL, CLEANER_TRACKABLE_DAYS
from common.logging_config import setup_logger


def main() -> None:
    """Main entry point for the cleaner service."""
    setup_logger(
        service_name="cleaner",
        log_level="INFO",
        log_file=Path("logs/cleaner.log"),
    )

    config = DatabaseConfig()
    db_cleaner = DBCleaner(config.connection_uri)

    while True:
        db_cleaner.update_trackable_rows(CLEANER_TRACKABLE_DAYS)
        logger.info(f"==+== Sleeping for {CLEANER_POLL_INTERVAL / 60} Min! ==+==")
        time.sleep(CLEANER_POLL_INTERVAL)


if __name__ == "__main__":
    main()
