#%%

import os
import time
import logging
import asyncio

from alive_progress import alive_bar

from miner_helpers.films_info_miner import get_films_list, get_films_status
from miner_helpers.db_updater import session_maker, update_films_list, update_films_status
from miner_helpers.tlg_updater import get_films_db_status, send_status

from logger.custom_logger import Logger

#%%

def sleep_with_progress(seconds):
    with alive_bar(seconds) as bar:
        bar.title('Sleepmeter')
        for _ in range(seconds):
            time.sleep(1)
            bar()

#%%
if __name__ == "__main__":

    TIME_INTERVAL = 120

    SQL_CONNECTION_URI = os.environ.get('POSTGRES_CONNECTION_URI')
    BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

    logger = Logger(file_handler=True)
    logger.get_logger()

    logging.info("Main starts!")

    url = 'https://www.filmpalast.net/vorschau.html'

    while True:

        logging.info("----- Mining session starts! -----")

        start_time = time.time()

        Session_Maker = session_maker(SQL_CONNECTION_URI)

        logging.info("Getting the films' list from the website!")
        Films = get_films_list(url)

        logging.info("Updating the films' list in DB!")
        update_films_list(Films, Session_Maker)

        logging.info("Getting the films' status from the website!")
        Films = get_films_status(Films)

        logging.info("Updating the films' status in DB!")
        update_films_status(Films, Session_Maker)

        end_time = time.time()
        elapsed_time = end_time - start_time

        logging.info(f"----- Mining session ended in {elapsed_time:.4f} seconds! -----")

        # Updating Users if there is a chanage in availability

        logging.info("----- Updating session starts! -----")

        start_time = time.time()

        users_list = get_films_db_status(Session_Maker)

        asyncio.run(send_status(users_list, BOT_TOKEN))

        end_time = time.time()
        elapsed_time = end_time - start_time

        logging.info(f"----- Updating session ended in {elapsed_time:.4f} seconds! -----")

        # Sleep for 10 Min
        logging.info(f"==+== Sleeping for {TIME_INTERVAL/60} Min! ==+==")
        sleep_with_progress(TIME_INTERVAL)