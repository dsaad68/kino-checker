#%%

import datetime
import requests
import asyncio
import logging

from bs4 import BeautifulSoup
from typing import List

from miner_helpers.film_checker import Film_Checker

#%%

URL_PREFIX = 'https://www.filmpalast.net/'

#%%

def get_films_list(url:str) -> List[dict]:

    try:
        # download the webpage
        response = requests.get(url)

        # parse the HTML using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # find all the elements you want to extract
        items = soup.find_all('a', class_='item-link outline')

        return [ {'title': item.find('h6').text.strip(),
                'link': URL_PREFIX + item['href'],
                'img_link': URL_PREFIX + item.find('img')['data-src']
                    }
                for item in items]

    except requests.exceptions.RequestException as e:
        logging.error(f"Error while downloading webpage from {url}: \n {str(e)}")
        return []

    except Exception as e:
        logging.error(f"Error while extracting film list from {url}: \n {str(e)}")
        return []

#%%

def get_films_status(films: List[dict]) -> List[dict]:

    # create a list to store the results
    results = []

    # create a coroutine to run the async methods
    async def run_checker(film:dict) -> None:

        try:

            film_checker = Film_Checker(film.get('link'))
            await film_checker.get_website()

            film.update({
                'availability' : film_checker.check_availability(),
                'last_checked': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'imax_3d_ov' : film_checker.check_imax_3d_ov(),
                'imax_ov': film_checker.check_imax_ov(),
                'hd_ov': film_checker.check_hd_ov()
                })

            results.append(film)

        except Exception as e:
            # log the error or exception
            logging.error(f"Error occurred while processing film: {film.get('name')}\n{str(e)}")

    try:
        # create an event loop to run the async methods
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # run the async methods for each link(URL) in the list
        tasks = [loop.create_task(run_checker(film)) for film in films]
        loop.run_until_complete(asyncio.wait(tasks))

    except Exception as error:
        # log the error or exception
        logging.error(error)

    return results