# %%

import os
import time
import logging
# import asyncio

from alive_progress import alive_bar

# from miner_helpers.tlg_updater import send_status
# TODO: fix this later
from fetcher.film_database_manager import FilmDatabaseManager
from fetcher.film_fetcher import FilmFetcher, FilmInfoExtractor, HEADERS, CENTER_OID

from my_logger import Logger

# %%


def sleep_with_progress(seconds):
    with alive_bar(seconds) as bar:
        bar.title("Sleepmeter")
        for _ in range(seconds):
            time.sleep(1)
            bar()


# %%
if __name__ == "__main__":
    logger = Logger(file_handler=True)
    logger.get_logger()

    SQL_CONNECTION_URI = os.environ.get("POSTGRES_CONNECTION_URI")
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
        films_list= FilmInfoExtractor(response).get_films_info_list()
        performance_list = FilmInfoExtractor(response).get_performances_list()

        logging.info("Updating the films list in DB!")
        film_db_manager.update_films_list(films_list)

        logging.info("Updating the performances list in DB!")
        film_db_manager.update_performances_list(performance_list)

        # logging.info("Getting the films' status from the website!")
        # Films = get_films_status(Films)

        # logging.info("Updating the films' status in DB!")
        # film_db_manager.update_films_status(Films)

        end_time = time.time()
        elapsed_time = end_time - start_time

        logging.info(f"----- Mining session ended in {elapsed_time:.4f} seconds! -----")

        # Updating Users if there is a chanage in availability

        # logging.info("----- Updating session starts! -----")

        # start_time = time.time()

        # users_list = film_db_manager.get_films_db_status()

        # asyncio.run(send_status(users_list, BOT_TOKEN))

        # end_time = time.time()
        # elapsed_time = end_time - start_time

        # logging.info(f"----- Updating session ended in {elapsed_time:.4f} seconds! -----")

        # Sleep for 10 Min
        logging.info(f"==+== Sleeping for {TIME_INTERVAL/60} Min! ==+==")
        sleep_with_progress(TIME_INTERVAL)
