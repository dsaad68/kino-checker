from datetime import datetime, timedelta

from common.db.db_model import UpcomingFilms
from common.db.manager import DBManager
from loguru import logger
from sqlalchemy import update
from sqlalchemy.sql import func


class DBCleaner(DBManager):
    def __init__(self, connection_uri: str):
        super().__init__(connection_uri)

    def update_trackable_rows(self, days: int = 120) -> None:
        """this function updates the trackable atritbute to false for the films that are older than the threshold days (default 120 days)

        Parameters
        ----------
        days : int
            number of days to keep the rows trackable after their entry date
        Session_Maker : sqlalchemy.orm.session.sessionmaker
            sqlalchemy session maker
        """

        # First, mark films as released if their release date has passed
        now = datetime.now()
        mark_released_stmt = (
            update(UpcomingFilms)
            .where(
                UpcomingFilms.release_date < now,
                UpcomingFilms.is_released == False,
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
                UpcomingFilms.is_trackable == True,
                UpcomingFilms.is_released == True,
            )
            .values(is_trackable=False)
        )

        # Execute the update statement
        logger.info("Cleaning outdated films ...")
        self.execute_insert_stmt(update_stmt)
        logger.info("Cleaned outdated films ...")

    def _get_upcoming_film_by_title(self, title: str) -> UpcomingFilms | None:
        """Get an existing row in the upcoming films table given its title."""
        return self.execute_fetch_one(
            UpcomingFilms, lambda upcoming_film: func.lower(upcoming_film.title) == title.lower()
        )
