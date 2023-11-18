# %%

import os
import time
import logging
# import asyncio

from alive_progress import alive_bar

# from miner_helpers.tlg_updater import send_status
# TODO: fix this later
from fetcher.scrapper import Scraper
from fetcher.film_db_manager import FilmDatabaseManager
from fetcher.film_fetcher import FilmFetcher, FilmInfoExtractor, HEADERS, CENTER_OID

from my_logger import Logger

# %%


def sleep_with_progress(seconds):
    with alive_bar(seconds) as bar:
        bar.title("Sleepmeter")
        for _ in range(seconds):
            time.sleep(1)
            bar()


def get_or_raise(env_name: str) -> str:
    value = os.environ.get(env_name)
    if value is not None:
        return value
    else:
        raise ValueError(f"Missing environment variable {env_name}")


# %%
if __name__ == "__main__":
    logger = Logger(file_handler=True)
    logger.get_logger()

    # create a function that gets the environment variables or raise an error

    SQL_CONNECTION_URI = get_or_raise(env_name="POSTGRES_CONNECTION_URI")
    # BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

    TIME_INTERVAL = 120

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

        # Updating Users if there is a chanage in availability

        logging.info("----- Updating session starts! -----")

        start_time = time.time()

        logging.info("Updating the released films in the upcoming films table in DB!")
        film_db_manager.update_released_films_in_upcoming_films_table()

        logging.info("Updating the released films in the users table in DB!")
        film_db_manager.update_users_table()

        logging.info("Getting the list of users to notify!")
        users_list = film_db_manager.get_users_to_notify()

        # [ ]: Sending message to users
        # asyncio.run(send_status(users_list, BOT_TOKEN))

        end_time = time.time()
        elapsed_time = end_time - start_time

        logging.info(f"----- Updating session ended in {elapsed_time:.4f} seconds! -----")

        # Sleep for 10 Min
        logging.info(f"==+== Sleeping for {TIME_INTERVAL/60} Min! ==+==")
        sleep_with_progress(TIME_INTERVAL)
