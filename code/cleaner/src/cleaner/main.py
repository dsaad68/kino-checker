import time
from pathlib import Path

from cleaner.utils.db_cleaner import DBCleaner
from common.constants import CLEANER_POLL_INTERVAL
from common.helpers import get_or_raise
from common.logging_config import setup_logger
from loguru import logger

if __name__ == "__main__":
    # Initialize the logger
    setup_logger(
        service_name="cleaner",
        log_level="INFO",
        log_file=Path("logs/cleaner.log"),
    )

    # Define the SQL connection URI
    SQL_CONNECTION_URI = get_or_raise("POSTGRES_DB_CONNECTION_URI")

    db_cleaner = DBCleaner(SQL_CONNECTION_URI)

    while True:
        # Update the trackable rows
        db_cleaner.update_trackable_rows(120)

        # Sleep for CLEANER_POLL_INTERVAL seconds
        logger.info(f"==+== Sleeping for {CLEANER_POLL_INTERVAL / 60} Min! ==+==")
        time.sleep(CLEANER_POLL_INTERVAL)
