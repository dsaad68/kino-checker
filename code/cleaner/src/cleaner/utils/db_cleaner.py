import logging
from sqlalchemy import update
from datetime import datetime, timedelta

from common.db.manager import DBManager
from common.db.db_model import UpcomingFilms


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

        # Calculate the date threshold (Default 120 days ago from today)
        threshold_date = datetime.now() - timedelta(days)

        # Create an update statement
        update_stmt = update(UpcomingFilms).where(UpcomingFilms.release_date < threshold_date, UpcomingFilms.is_trackable == True).values(trackable=False)  # noqa: E712

        # Execute the update statement
        logging.info("Cleaning outdated films ...")
        self.execute_insert_stmt(update_stmt)
        logging.info("Cleaned outdated films ...")
