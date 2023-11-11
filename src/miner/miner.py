# %%

import os
import time
import logging
import asyncio

from alive_progress import alive_bar

from miner_helpers.films_info_miner import get_films_list, get_films_status
from miner.miner_helpers.film_database_manager import FilmDatabaseManager
from miner_helpers.tlg_updater import send_status

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
    BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

    TIME_INTERVAL = 120

    url = "https://www.filmpalast.net/vorschau.html"

    logging.info("Main starts!")

    film_db_manager = FilmDatabaseManager(SQL_CONNECTION_URI)

    while True:
        logging.info("----- Mining session starts! -----")

        start_time = time.time()

        logging.info("Getting the films' list from the website!")
        Films = get_films_list(url)

        logging.info("Updating the films' list in DB!")
        film_db_manager.update_films_list(Films)

        logging.info("Getting the films' status from the website!")
        Films = get_films_status(Films)

        logging.info("Updating the films' status in DB!")
        film_db_manager.update_films_status(Films)

        end_time = time.time()
        elapsed_time = end_time - start_time

        logging.info(f"----- Mining session ended in {elapsed_time:.4f} seconds! -----")

        # Updating Users if there is a chanage in availability

        logging.info("----- Updating session starts! -----")

        start_time = time.time()

        users_list = film_db_manager.get_films_db_status()

        asyncio.run(send_status(users_list, BOT_TOKEN))

        end_time = time.time()
        elapsed_time = end_time - start_time

        logging.info(f"----- Updating session ended in {elapsed_time:.4f} seconds! -----")

        # Sleep for 10 Min
        logging.info(f"==+== Sleeping for {TIME_INTERVAL/60} Min! ==+==")
        sleep_with_progress(TIME_INTERVAL)
