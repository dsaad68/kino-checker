import logging
import requests

from typing import List, Optional
from datetime import date, time, datetime

CENTER_OID = "6F000000014BHGWDVI"
HEADERS = {
    "authority": "cineorder.filmpalast.net",
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.9,de;q=0.8,fa;q=0.7",
    "dnt": "1",
    "referer": "https://cineorder.filmpalast.net/zkm",
    "sec-ch-ua": '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
}


class FilmFetcher:
    def __init__(self, center_oid: str = CENTER_OID, headers: dict = HEADERS):
        self.center_oid = center_oid
        self.headers = headers
        self.session_id = self._get_session_id()

    def _get_session_id(self) -> Optional[str]:
        url = "https://cineorder.filmpalast.net/api/session"

        headers = self.headers | {"center-oid": self.center_oid}

        try:
            response = requests.request("GET", url, headers=headers)
            return response.json().get("sessionId", None)

        except requests.RequestException as e:
            logging.error(f"An error occurred: {e}")
            return None

    def get_film_list(self, date_from: str, date_to: str) -> Optional[List]:
        url = "https://cineorder.filmpalast.net/api/films"

        payload = {"cinemadate.from": date_from, "cinemadate.to": date_to}
        headers = self.headers | {"center-oid": self.center_oid, "session-id": self.session_id}

        try:
            response = requests.request("GET", url, headers=headers, data=payload)
            return response.json()

        except requests.RequestException as e:
            logging.error(f"An error occurred: {e}")
            return None


class FilmInfoExtractor:
    """This class extracts the films and performances from the film_fetcher_response."""
    def __init__(self, film_fetcher_response: Optional[list]):
        if film_fetcher_response is not None:
            self.film_fetcher_response = film_fetcher_response
        else:
            logging.warning("API Response is empty!")
            self.film_fetcher_response = None

    # IDEA: if it works with film object instead of dict
    def get_films_info_list(self) -> Optional[List[dict]]:
        """Extracts the films from the film_fetcher_response and returns a list of dictionaries."""
        film_list = self.film_fetcher_response
        if film_list is not None:
            return [
                {
                    "film_id": film.get("id"),
                    "title": film.get("title"),
                    "name": film.get("name"),
                    "production_year": film.get("productionYear"),
                    "length_in_minutes": film.get("lengthInMinutes"),
                    "nationwide_start": film.get("nationwideStart"),
                    "image_url": film.get("imageUrl"),
                    "last_updated": datetime.now()
                }
                for film in film_list  # type: ignore
            ]
        logging.warn("Film Fetcher Response is empty!")
        return None

    # CHECK: the time because of time zone
    # IDEA: if it works with performance object instead of dict
    def get_performances_list(self) -> Optional[List[dict]]:
        """Extracts the performances from the film_fetcher_response and returns a list of dictionaries."""
        film_list = self.film_fetcher_response
        if film_list is not None:
            return [
                {
                    "performance_id": performance.get("id"),
                    "film_id": film.get("id"),
                    "film_id_p": performance.get("filmId"),
                    "performance_datetime": performance.get("performanceDateTime"),
                    "performance_time": self._extract_time(performance.get("performanceDateTime")),
                    "performance_date": self._extract_date(performance.get("performanceDateTime")),
                    "release_type": performance.get("releaseTypeName"),
                    "is_imax": self._is_imax(performance.get("releaseTypeName")),
                    "is_ov": self._is_ov(performance.get("releaseTypeName")),
                    "is_3d": performance.get("is3D"),
                    "auditorium_name": performance.get("auditoriumName"),
                    "auditorium_id": performance.get("auditoriumId"),
                    "last_updated": datetime.now(),
                    # TODO: Add this later
                    # **self._empty_dict_checker(performance.get("access")),
                }
                for film in film_list  # type: ignore
                for performance in film.get("performances")
            ]
        logging.warn("Film Fetcher Response is empty!")
        return None

    @staticmethod
    def _is_imax(release_type: str) -> bool:
        """This function checks if a film is available in IMAX in a cinema"""
        return "IMAX" in release_type if release_type is not None else False

    @staticmethod
    def _is_ov(release_type: str) -> bool:
        """This function checks if a film is available in OV in a cinema"""
        return ("OV" in release_type or "englisch" in release_type) if release_type is not None else False

    @staticmethod
    def _extract_time(performanceDateTime: str) -> Optional[time]:
        """This function extracts the time from the performanceDateTime"""
        if performanceDateTime is None:
            return None
        dt = datetime.fromisoformat(performanceDateTime)
        return dt.time()

    @staticmethod
    def _extract_date(performanceDateTime: str) -> Optional[date]:
        """This function extracts the date from the performanceDateTime"""
        if performanceDateTime is None:
            return None
        dt = datetime.fromisoformat(performanceDateTime)
        return dt.date()

    @staticmethod
    def _empty_dict_checker(data: dict) -> Optional[dict]:
        """This function checks if a dictionary is empty and returns None if it is"""
        if data is not None:
            return data
