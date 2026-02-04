# %%

import asyncio
import time
from pathlib import Path

from common.constants import MINER_POLL_INTERVAL
from common.helpers import get_or_raise
from common.logging_config import setup_logger
from loguru import logger
from miner.utils.film_db_manager import FilmDatabaseManager
from miner.utils.film_fetcher import CENTER_OID, HEADERS, FilmFetcher, FilmInfoExtractor
from miner.utils.film_notifier import FilmReleaseNotification
from miner.utils.scrapper import Scraper

# %%
# sourcery skip: use-named-expression
if __name__ == "__main__":
    setup_logger(
        service_name="miner",
        log_level="INFO",
        log_file=Path("logs/miner.log"),
    )

    # create a function that gets the environment variables or raise an error

    SQL_CONNECTION_URI = get_or_raise(env_name="POSTGRES_DB_CONNECTION_URI")
    BOT_TOKEN = get_or_raise(env_name="TELEGRAM_BOT_TOKEN")

    url = "https://www.filmpalast.net/vorschau.html"

    logger.info("Main starts!")

    film_db_manager = FilmDatabaseManager(SQL_CONNECTION_URI)

    while True:
        logger.info("----- Mining session starts! -----")

        start_time = time.time()

        logger.info("Call the API to getting the films' list!")
        film_fetcher = FilmFetcher(center_oid=CENTER_OID, headers=HEADERS)
        response = film_fetcher.get_film_list("2022-01-01", "2022-01-31")

        logger.info("Extracting the films info and performance data from the API response!")
        film_info_extractor = FilmInfoExtractor(response)
        films_list = film_info_extractor.get_films_info_list()
        performance_list = film_info_extractor.get_performances_list()

        logger.info("Updating the films list in DB!")
        film_db_manager.update_films_table(films_list)

        logger.info("Updating the performances list in DB!")
        film_db_manager.update_performances_table(performance_list)

        logger.info("Updating the upcoming films list in DB!")
        upcoming_films_list = Scraper.set_base_url().run()

        logger.info("Updating the upcoming films list in DB!")
        film_db_manager.update_upcoming_films_table(upcoming_films_list)

        end_time = time.time()
        elapsed_time = end_time - start_time

        logger.info(f"----- Mining session ended in {elapsed_time:.4f} seconds! -----")

        logger.info("----- Updating session starts! -----")
        start_time = time.time()

        logger.info("Updating the released films in the upcoming films table in DB!")
        film_db_manager.update_released_films_in_upcoming_films_table()

        logger.info("Updating the released films in the users table in DB!")
        film_db_manager.update_users_table()

        logger.info("Getting the list of users to notify!")
        users_list = film_db_manager.get_users_to_notify()

        if users_list:
            logger.info(f"Number of users to notify: {len(users_list)}")
            logger.info(f"Users to notify: {users_list}")

            logger.info("Sending notification to users!")
            try:
                film_notifier = FilmReleaseNotification(BOT_TOKEN)
                asyncio.run(film_notifier.send_notification(users_list))
                asyncio.run(film_notifier.shutdown())
                logger.info(f"Number of users has been notified: {len(users_list)}")
            except Exception as error:
                logger.error(f"An error occurred while sending notifications: {error}", exc_info=True)
            else:
                logger.info("Updating the notification status of notified users in the users table in DB!")
                film_db_manager.update_notified_users_table(users_list)
                logger.info("Updated the notification status of notified users in the users table in DB!")

        end_time = time.time()
        elapsed_time = end_time - start_time

        logger.info(f"----- Updating session ended in {elapsed_time:.4f} seconds! -----")

        # Sleep for 10 Min
        logger.info(f"==+== Sleeping for {MINER_POLL_INTERVAL / 60} Min! ==+==")
        time.sleep(MINER_POLL_INTERVAL)
