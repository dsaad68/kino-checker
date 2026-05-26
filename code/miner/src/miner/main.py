from __future__ import annotations

import asyncio
import time
from datetime import date, timedelta
from pathlib import Path

from loguru import logger

from common.config import DatabaseConfig, TelegramConfig
from common.constants import MINER_FETCH_WINDOW_DAYS, MINER_POLL_INTERVAL
from common.logging_config import setup_logger
from miner.utils.film_db_manager import FilmDatabaseManager
from miner.utils.film_fetcher import CENTER_OID, HEADERS, FilmFetcher, FilmInfoExtractor
from miner.utils.film_notifier import FilmReleaseNotification
from miner.utils.scrapper import Scraper


def main() -> None:
    """Main entry point for the miner service."""
    setup_logger(
        service_name="miner",
        log_level="INFO",
        log_file=Path("logs/miner.log"),
    )

    db_config = DatabaseConfig()
    telegram_config = TelegramConfig()
    sql_connection_uri = db_config.connection_uri
    bot_token = telegram_config.bot_token

    logger.info("Main starts!")

    film_db_manager = FilmDatabaseManager(sql_connection_uri)

    while True:
        logger.info("----- Mining session starts! -----")

        start_time = time.time()

        logger.info("Call the API to getting the films' list!")
        film_fetcher = FilmFetcher(center_oid=CENTER_OID, headers=HEADERS)
        today = date.today()
        date_from = today.isoformat()
        date_to = (today + timedelta(days=MINER_FETCH_WINDOW_DAYS)).isoformat()
        response = film_fetcher.get_film_list(date_from, date_to)

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

                async def notify_and_shutdown(users: list) -> None:
                    notifier = FilmReleaseNotification(bot_token)
                    await notifier.send_notification(users)
                    await notifier.shutdown()

                asyncio.run(notify_and_shutdown(users_list))
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


if __name__ == "__main__":
    main()
