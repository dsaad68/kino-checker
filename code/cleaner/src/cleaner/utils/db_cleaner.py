from __future__ import annotations

from datetime import datetime, timedelta

from loguru import logger
from sqlalchemy import update

from common.constants import CLEANER_TRACKABLE_DAYS
from common.db.db_model import UpcomingFilms
from common.db.manager import DBManager


class DBCleaner(DBManager):
    def __init__(self, connection_uri: str) -> None:
        super().__init__(connection_uri)

    def update_trackable_rows(self, days: int = CLEANER_TRACKABLE_DAYS) -> None:
        """Update the trackable attribute to false for films older than the threshold.

        Parameters
        ----------
        days : int
            Number of days to keep rows trackable after their release date.
        """

        # First, mark films as released if their release date has passed
        now = datetime.now()
        mark_released_stmt = (
            update(UpcomingFilms)
            .where(
                UpcomingFilms.release_date < now,
                UpcomingFilms.is_released.is_(False),
            )
            .values(is_released=True)
        )

        logger.info("Marking films as released...")
        self.execute_insert_stmt(mark_released_stmt)
        logger.info("Marked films as released...")

        # Calculate the date threshold (Default 120 days ago from today)
        threshold_date = now - timedelta(days)

        # Create an update statement to mark old films as not trackable
        update_stmt = (
            update(UpcomingFilms)
            .where(
                UpcomingFilms.release_date < threshold_date,
                UpcomingFilms.is_trackable.is_(True),
                UpcomingFilms.is_released.is_(True),
            )
            .values(is_trackable=False)
        )

        # Execute the update statement
        logger.info("Cleaning outdated films ...")
        self.execute_insert_stmt(update_stmt)
        logger.info("Cleaned outdated films ...")
