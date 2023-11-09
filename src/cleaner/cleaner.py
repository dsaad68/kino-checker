import os
import time
import logging

from datetime import datetime, timedelta

from cleaner_helpers.db_model import Films

from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker

from my_logger import Logger

#%%

def session_maker(connection_uri: str):

    # Define the database connection
    engine = create_engine(connection_uri, pool_size=1, max_overflow=1)

    # Define a session factory
    return sessionmaker(bind=engine)

#%%

class DBCleaner:
    def __init__(self, connection_uri: str):
        self.connection_uri = connection_uri
        self.session_maker = self._session_maker()

    def update_trackable_rows(self, days:int = 120) -> None:
        """this function updates the trackable atritbute to false for the films that are older than the threshold days (default 120 days)

        Parameters
        ----------
        days : int
            number of days to keep the rows trackable after their entry date
        Session_Maker : sqlalchemy.orm.session.sessionmaker
            sqlalchemy session maker
        """

        try:
            # Calculate the date threshold (Default 120 days ago from today)
            threshold_date = datetime.now() - timedelta(days)

            # Open a session using the session factory
            with self.session_maker() as session:

                # Create an update statement
                update_stmt = update(Films).where(Films.availability_date < threshold_date, Films.trackable == True).values(trackable=False) # noqa: E712

                # Execute the update statement
                results = session.execute(update_stmt)

                # Commit the changes to the database
                session.commit()
                session.close()

                logging.info(f'Updated {results.rowcount} rows!')

        except Exception as error:
            logging.error(f'ERROR : {error}', exc_info=True)
            session.rollback()

    def _session_maker(self) -> sessionmaker:
        # Define the database connection
        engine = create_engine(self.connection_uri, pool_size=2, max_overflow=2)
        # Define a session factory
        return sessionmaker(bind=engine)


#%%

if __name__ == '__main__':

    # Initialize the logger
    logger = Logger(file_handler=True)
    logger.get_logger()

    # Define the SQL connection URI
    SQL_CONNECTION_URI = os.environ.get('POSTGRES_CONNECTION_URI')

    TIME_INTERVAL = 180

    db_cleaner = DBCleaner(SQL_CONNECTION_URI)

    while True:

        # Update the trackable rows
        db_cleaner.update_trackable_rows(120)

        # Sleep for TIME_INTERVAL seconds
        logging.info(f"==+== Sleeping for {TIME_INTERVAL/60} Min! ==+==")
        time.sleep(TIME_INTERVAL)
