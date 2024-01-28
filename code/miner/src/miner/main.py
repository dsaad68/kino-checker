# %%

import os
import time
import logging
import asyncio

from miner.utils.scrapper import Scraper
from miner.utils.film_db_manager import FilmDatabaseManager
from miner.utils.film_notifier import FilmReleaseNotification
from miner.utils.film_fetcher import FilmFetcher, FilmInfoExtractor, HEADERS, CENTER_OID

from my_logger import Logger

# %%

def get_or_raise(env_name: str) -> str:
    value = os.environ.get(env_name)
    if value is not None:
        return value
    else:
        raise ValueError(f"Missing environment variable {env_name}")


# %%
# sourcery skip: use-named-expression
if __name__ == "__main__":
    logger = Logger(file_handler=True)
    logger.get_logger()

    # create a function that gets the environment variables or raise an error

    SQL_CONNECTION_URI = get_or_raise(env_name="POSTGRES_DB_CONNECTION_URI")
    BOT_TOKEN = get_or_raise(env_name="TELEGRAM_BOT_TOKEN")

    TIME_INTERVAL = 600

    url = "https://www.filmpalast.net/vorschau.html"

    logging.info("Main starts!")

    film_db_manager = FilmDatabaseManager(SQL_CONNECTION_URI)

    while True:
        logging.info("----- Mining session starts! -----")

        start_time = time.time()

        logging.info("Call the API to getting the films' list!")
        film_fetcher = FilmFetcher(center_oid=CENTER_OID, headers=HEADERS)
        response = film_fetcher.get_film_list("2022-01-01", "2022-01-31")

        logging.info("Extracting the films info and performance data from the API response!")
        film_info_extractor = FilmInfoExtractor(response)
        films_list = film_info_extractor.get_films_info_list()
        performance_list = film_info_extractor.get_performances_list()

        logging.info("Updating the films list in DB!")
        film_db_manager.update_films_table(films_list)

        logging.info("Updating the performances list in DB!")
        film_db_manager.update_performances_table(performance_list)

        logging.info("Updating the upcoming films list in DB!")
        upcoming_films_list = Scraper.set_base_url().run()

        logging.info("Updating the upcoming films list in DB!")
        film_db_manager.update_upcoming_films_table(upcoming_films_list)

        end_time = time.time()
        elapsed_time = end_time - start_time

        logging.info(f"----- Mining session ended in {elapsed_time:.4f} seconds! -----")

        logging.info("----- Updating session starts! -----")
        start_time = time.time()

        logging.info("Updating the released films in the upcoming films table in DB!")
        film_db_manager.update_released_films_in_upcoming_films_table()

        logging.info("Updating the released films in the users table in DB!")
        film_db_manager.update_users_table()

        # BUG: Sometimes is not working.
        # INFO: The Reason is that the films can be added to the film table, but there are no performances in the performances table.
        # INFO: The definition of availability needs to be changed.
        logging.info("Getting the list of users to notify!")
        users_list = film_db_manager.get_users_to_notify()

        if users_list:

            logging.info(f"Number of users to notify: {len(users_list)}")
            logging.info(f"Users to notify: {users_list}")

            logging.info("Sending notification to users!")
            film_notifier = FilmReleaseNotification(BOT_TOKEN)
            asyncio.run(film_notifier.send_notification(users_list))
            asyncio.run(film_notifier.shutdown())
            logging.info(f"Number of users has been notified: {len(users_list)}")

            # Check: might not work because of the bug above
            logging.info("Updating the notification status of notified users in the users table in DB!")
            film_db_manager.update_notified_users_table(users_list)
            logging.info("Updated the notification status of notified users in the users table in DB!")

        end_time = time.time()
        elapsed_time = end_time - start_time

        logging.info(f"----- Updating session ended in {elapsed_time:.4f} seconds! -----")

        # Sleep for 10 Min
        logging.info(f"==+== Sleeping for {TIME_INTERVAL/60} Min! ==+==")
        time.sleep(TIME_INTERVAL)
