from __future__ import annotations

import os
from datetime import date, datetime, time

import requests
from loguru import logger

# Max characters of response body to log on error (avoid huge logs)
_RESPONSE_BODY_LOG_LIMIT = 500

# API is served from the iframe subdomain (not cineorder.filmpalast.net)
CINEORDER_BASE_URL = "https://iframe.cineorder.filmpalast.net"
CENTER_OID = "6F000000014BHGWDVI"

HEADERS = {
    "authority": "iframe.cineorder.filmpalast.net",
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.9,de;q=0.8,fa;q=0.7",
    "dnt": "1",
    "referer": f"{CINEORDER_BASE_URL}/landingpage?center={CENTER_OID}&language=DE",
    "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
}


def _auth_headers() -> dict[str, str]:
    """Optional auth from env: CINEORDER_USER (bearer JWT), CINEORDER_COOKIE (e.g. __cfwaitingroom)."""
    out: dict[str, str] = {}
    jwt = os.environ.get("CINEORDER_USER", "").strip()
    if jwt:
        out["cineorder-user"] = f"bearer {jwt}" if not jwt.lower().startswith("bearer ") else jwt
    cookie = os.environ.get("CINEORDER_COOKIE", "").strip()
    if cookie:
        out["Cookie"] = cookie
    return out


def _safe_json_response(response: requests.Response, context: str = "") -> dict | list | None:
    """Parse response as JSON. On non-200 or empty/invalid body log status, Content-Type, and body snippet; return None."""
    status = response.status_code
    content_type = response.headers.get("Content-Type", "")
    text = response.text or ""

    if status != 200:
        snippet = (
            (text[:_RESPONSE_BODY_LOG_LIMIT] + "...") if len(text) > _RESPONSE_BODY_LOG_LIMIT else text or "(empty)"
        )
        logger.error(
            "API response not OK: status={} content_type={} context={} body={}",
            status,
            content_type,
            context or "api",
            snippet,
        )
        return None

    if not text.strip():
        logger.error(
            "API response empty body: status={} content_type={} context={}",
            status,
            content_type,
            context or "api",
        )
        return None

    try:
        return response.json()
    except requests.exceptions.JSONDecodeError as e:
        snippet = (text[:_RESPONSE_BODY_LOG_LIMIT] + "...") if len(text) > _RESPONSE_BODY_LOG_LIMIT else text
        logger.error(
            "API response invalid JSON: status={} content_type={} context={} error={} body={}",
            status,
            content_type,
            context or "api",
            e,
            snippet,
        )
        return None


class FilmFetcher:
    def __init__(self, center_oid: str = CENTER_OID, headers: dict = HEADERS):
        self.center_oid = center_oid
        self.headers = headers
        self.session_id = self._get_session_id()

    def _get_session_id(self) -> str | None:
        url = f"{CINEORDER_BASE_URL}/api/session"
        headers = self.headers | {"center-oid": self.center_oid} | _auth_headers()

        try:
            response = requests.request("GET", url, headers=headers, timeout=30)
        except requests.RequestException as e:
            logger.error("Session API request failed: %s", e)
            return None

        data = _safe_json_response(response, context="session")
        if data is None or not isinstance(data, dict):
            return None
        return data.get("sessionId")

    def get_film_list(self, date_from: str, date_to: str) -> list | None:
        url = f"{CINEORDER_BASE_URL}/api/films"
        params = {"cinemadate.from": date_from, "cinemadate.to": date_to}
        headers = self.headers | {"center-oid": self.center_oid, "session-id": self.session_id or ""} | _auth_headers()

        try:
            response = requests.request("GET", url, headers=headers, params=params, timeout=30)
        except requests.RequestException as e:
            logger.error("Films API request failed: %s", e)
            return None

        data = _safe_json_response(response, context="films")
        if data is None:
            return None
        return data if isinstance(data, list) else None


class FilmInfoExtractor:
    """This class extracts the films and performances from the film_fetcher_response."""

    def __init__(self, film_fetcher_response: list | None):
        if film_fetcher_response is not None:
            self.film_fetcher_response = film_fetcher_response
        else:
            logger.warning("API Response is empty!")
            self.film_fetcher_response = None

    def get_films_info_list(self) -> list[dict] | None:
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
                    "last_updated": datetime.now(),
                }
                for film in film_list  # type: ignore
            ]
        logger.warning("Film Fetcher Response is empty!")
        return None

    def get_performances_list(self) -> list[dict] | None:
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
                    # INFO: there other versions like 4K
                    "auditorium_name": performance.get("auditoriumName"),
                    "auditorium_id": performance.get("auditoriumId"),
                    "last_updated": datetime.now(),
                    # INFO: There is more information like `access` (performance.get("access")) in the API
                }
                for film in film_list  # type: ignore
                for performance in film.get("performances")
            ]
        logger.warning("Film Fetcher Response is empty!")
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
    def _extract_time(performance_date_time: str) -> time | None:
        """This function extracts the time from the performance_date_time."""
        if performance_date_time is None:
            return None
        dt = datetime.fromisoformat(performance_date_time)
        return dt.time()

    @staticmethod
    def _extract_date(performance_date_time: str) -> date | None:
        """This function extracts the date from the performance_date_time."""
        if performance_date_time is None:
            return None
        dt = datetime.fromisoformat(performance_date_time)
        return dt.date()

    @staticmethod
    def _empty_dict_checker(data: dict) -> dict | None:
        """This function checks if a dictionary is empty and returns None if it is"""
        if data is not None:
            return data
