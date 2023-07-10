import os
import time
import logging

from datetime import datetime, timedelta

from tables.tables_model import Films

from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker

from logger.custom_logger import Logger

#%%

def session_maker(connection_uri: str):

    # Define the database connection
    engine = create_engine(connection_uri, pool_size=1, max_overflow=1)

    # Define a session factory
    return sessionmaker(bind=engine)

#%%

def update_trackable_rows(Session_Maker, days:int = 120) -> None:
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
        with Session_Maker() as session:

            # Create an update statement
            update_stmt = update(Films).where(Films.availability_date < threshold_date, Films.trackable == True).values(trackable=False)

            # Execute the update statement
            results = session.execute(update_stmt)

            # Commit the changes to the database
            session.commit()
            session.close()

            logging.info(f'Updated {results.rowcount} rows!')

    except Exception as error:
        logging.error(f'ERROR : {error}', exc_info=True)
        session.rollback()

    # Finally close the session
    finally:
        session.close()

#%%

if __name__ == '__main__':

    # Initialize the logger
    logger = Logger(file_handler=True)
    logger.get_logger()

    # Define the SQL connection URI
    SQL_CONNECTION_URI = os.environ.get('POSTGRES_CONNECTION_URI')

    TIME_INTERVAL = 180

    Session_Maker = session_maker(SQL_CONNECTION_URI)

    while True:

        # Update the trackable rows
        update_trackable_rows(Session_Maker, 10)

        # Sleep for TIME_INTERVAL seconds
        logging.info(f"==+== Sleeping for {TIME_INTERVAL/60} Min! ==+==")
        time.sleep(TIME_INTERVAL)