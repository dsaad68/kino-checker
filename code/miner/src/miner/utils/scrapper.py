import re
import logging
import requests

from bs4 import BeautifulSoup
from typing import List, Tuple
from datetime import datetime, date
from requests import RequestException


class Scraper:
    def __init__(self):
        self.base_url = None
        self.date_pattern = re.compile(r"\b\d{2}\.\d{2}\.\d{4}\b")

    @classmethod
    def set_base_url(cls, base_url="https://filmpalast.net/vorschau/page/"):
        """Sets the base URL for the scraper."""
        instance = cls()
        instance.base_url = base_url
        return instance

    def run(self) -> list[dict]:
        """Runs the scraper and returns a list of results."""

        MAX_ITERATIONS = 100  # Set a reasonable limit to prevent infinite loops

        i = 1
        results: List[dict] = []

        while i <= MAX_ITERATIONS:
            url = f"{self.base_url}{i}/"
            soup, status_code = self._get_website(url)

            # Break the loop if 404 status code is encountered
            if status_code == 404:
                break

            logging.info(f"Scrapper run for page {i}, Status code: {status_code}")
            # extract data if status code is not 999
            if status_code != 999:
                data = self._extractor(soup)
                # sourcery skip: merge-nested-ifs
                if data is not None:
                    if len(data) > 0:
                        results.extend(data)

            i += 1

        return results

    def _get_website(self, url) -> Tuple[BeautifulSoup | None, int]:
        """Retrieves a website and returns its BeautifulSoup object and status code."""

        try:
            response = requests.get(url)
            return BeautifulSoup(response.text, "html.parser"), response.status_code
        except RequestException as e:
            logging.error(f"An error occurred with request: {e}")
            return None, 999
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return None, 999

    # IDEA: if it works with upcoming film object instead of dict
    def _extractor(self, soup) -> List[dict] | None:
        """Extracts data from a BeautifulSoup object."""

        results: List[dict] = []

        title_selector = "div.elementor-container div.elementor-column-gap-default h2"
        release_date_selector = "div.elementor-container div.elementor-column-gap-default ul > li:nth-of-type(2) span"

        elements = soup.select(".elementor-container .elementor-column-gap-default")

        try:
            for element in elements:
                title = element.select_one(title_selector)
                release_date = element.select_one(release_date_selector)
                if title is not None:
                    results.append({
                                    "title": title.get_text(),
                                    "release_date": self._get_date(release_date.get_text()),
                                    "last_updated": datetime.now()
                                    })
            return results
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return None

    def _get_date(self, input) -> date | None:
        """Returns the current date in the format 'YYYY-MM-DD' if input is not None."""

        if input is None:
            return None

        match = self.date_pattern.search(input)
        if match is None:
            return None
        date_str = match.group(0)
        return datetime.strptime(date_str, "%d.%m.%Y").date()
