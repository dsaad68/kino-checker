from __future__ import annotations

from sqlalchemy.sql import func

from cleaner.utils.db_cleaner import DBCleaner
from common.constants import CLEANER_TRACKABLE_DAYS
from common.db.db_model import UpcomingFilms
from common.db.manager import DBManager


def _get_film_by_title(manager: DBManager, title: str) -> UpcomingFilms | None:
    """Fetch upcoming film by title (test helper)."""
    return manager.execute_fetch_one(UpcomingFilms, lambda uf: func.lower(uf.title) == title.lower())


def test_update_trackable_rows(db_connection_uri_with_sample_data: str) -> None:
    db_cleaner = DBCleaner(db_connection_uri_with_sample_data)
    db_cleaner.update_trackable_rows(CLEANER_TRACKABLE_DAYS)

    # Case 1
    napoleon_film = _get_film_by_title(db_cleaner, "Napoleon")
    assert napoleon_film is not None
    assert napoleon_film.is_released is True
    assert napoleon_film.is_trackable is False

    # Case 2
    saw_x_film = _get_film_by_title(db_cleaner, "SAW X")
    assert saw_x_film is not None
    assert saw_x_film.is_released is True
    assert saw_x_film.is_trackable is False

    # Case 3
    wish_film = _get_film_by_title(db_cleaner, "Wish")
    assert wish_film is not None
    assert wish_film.is_released is True
    assert wish_film.is_trackable is True

    # Case 4
    raus_aus_dem_teich_film = _get_film_by_title(db_cleaner, "Raus aus dem Teich")
    assert raus_aus_dem_teich_film is not None
    assert raus_aus_dem_teich_film.is_released is False
    assert raus_aus_dem_teich_film.is_trackable is True
