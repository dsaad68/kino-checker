import time
import logging

from my_logger import Logger

from common.helpers import get_or_raise

from cleaner.utils.db_cleaner import DBCleaner

if __name__ == "__main__":

    # Initialize the logger
    logger = Logger(file_handler=True)
    logger.get_logger()

    # Define the SQL connection URI
    SQL_CONNECTION_URI = get_or_raise("POSTGRES_DB_CONNECTION_URI")

    TIME_INTERVAL = 10800

    db_cleaner = DBCleaner(SQL_CONNECTION_URI)

    while True:
        # Update the trackable rows
        db_cleaner.update_trackable_rows(120)

        # Sleep for TIME_INTERVAL seconds
        logging.info(f"==+== Sleeping for {TIME_INTERVAL/60} Min! ==+==")
        time.sleep(TIME_INTERVAL)
