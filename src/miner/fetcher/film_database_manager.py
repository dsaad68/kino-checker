# %%
import logging
import datetime

from typing import List, Union, Dict

from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker, Session

from .db_model import Films, Performances

# %%


class FilmDatabaseManager:
    def __init__(self, connection_uri: str):
        self.connection_uri = connection_uri
        self.session_maker = self._session_maker()

    def update_films_list(self, films_list: List[dict]) -> None:
        # sourcery skip: extract-method

        try:
            # Create a new session
            with self.session_maker() as session:

                # Insert statement
                insert_stmt = insert(Films).values(films_list)

                # LEARN: What is excluded?
                # Build a dictionary for updating all columns except the primary key
                update_dict = {col.name: insert_stmt.excluded[col.name] for col in Films.__table__.columns if not col.primary_key}

                # set the last_update column to the current time
                update_dict['last_updated'] = datetime.datetime.now()

                # Upsert statement
                upsert_stmt = insert_stmt.on_conflict_do_update(index_elements=[Films.film_id], set_=update_dict)

                # Execute the upsert statement
                session.execute(upsert_stmt)

                # Commit the changes and close the session
                session.commit()

        except Exception as error:
            logging.error(f"ERROR : {error}", exc_info=True)
            session.rollback()

    def update_performances_list(self, performances_list: List[dict]) -> None:
        # sourcery skip: extract-method

        try:
            # Create a new session
            with self.session_maker() as session:

                # Insert statement
                insert_stmt = insert(Performances).values(performances_list)

                # LEARN: What is excluded?
                # Build a dictionary for updating all columns except the primary key
                update_dict = {col.name: insert_stmt.excluded[col.name] for col in Performances.__table__.columns if not col.primary_key}

                # set the last_update column to the current time
                update_dict['last_updated'] = datetime.datetime.now()

                # Upsert statement
                upsert_stmt = insert_stmt.on_conflict_do_update(index_elements=[Performances.performance_id], set_=update_dict)

                # Execute the upsert statement
                session.execute(upsert_stmt)

                # Commit the changes and close the session
                session.commit()

        except Exception as error:
            logging.error(f"ERROR : {error}", exc_info=True)
            session.rollback()

    @staticmethod
    def get_existing_row(title: str, session: Session) -> Union[Films, None]:
        return session.query(Films).filter(Films.title == title).first()

    @staticmethod
    def _extract_film_data(film_dict, keys: List[str]) -> Dict[str, Union[str, int]]:
        return {key: film_dict.get(key) for key in keys}

    def _session_maker(self) -> sessionmaker:
        # Define the database connection
        engine = create_engine(self.connection_uri, pool_size=2, max_overflow=2)
        # Define a session factory
        return sessionmaker(bind=engine)
