# %%
import logging
import datetime

from typing import List, Union, Dict, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import insert, Insert

from .db_model import Films, Performances, UpcomingFilms

# %%


class FilmDatabaseManager:
    def __init__(self, connection_uri: str):
        self.connection_uri = connection_uri
        self.session_maker = self._session_maker()

    def update_films_table(self, films_list: Optional[List[dict]]) -> None:

        if films_list is not None:

            # Upsert statement
            upsert_stmt = self._create_upsert_stmt(Films, 'film_id', films_list)
            # Execute the upsert statement
            self._excute_upsert_stmt(upsert_stmt)

        else:
            logging.warning("Films list is None")

    def update_performances_table(self, performances_list: Optional[List[dict]]) -> None:

        if performances_list is not None:

            # Upsert statement
            upsert_stmt = self._create_upsert_stmt(Performances, 'performance_id', performances_list)
            # Execute the upsert statement
            self._excute_upsert_stmt(upsert_stmt)

        else:
            logging.warning("Performances list is None")

    def update_upcoming_films_table(self, upcoming_films_list: Optional[List[dict]]) -> None:

        exclude_cols = ['is_release', 'is_trackable']

        if upcoming_films_list is not None:

            # Upsert statement
            upsert_stmt = self._create_upsert_stmt(UpcomingFilms, 'upcoming_film_id', upcoming_films_list, exclude_cols=exclude_cols)
            # Execute the upsert statement
            self._excute_upsert_stmt(upsert_stmt)

        else:
            logging.warning("Performances list is None")

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

    def _create_upsert_stmt(self, table, id_col_name: str, update_list: List[dict], exclude_cols: Optional[List[str]] = None) -> Insert:

        # Insert statement
        insert_stmt = insert(table).values(update_list)
        # LEARN: What is excluded?
        # Build a dictionary for updating all columns except the primary key
        update_dict = {col.name: insert_stmt.excluded[col.name] for col in table.__table__.columns if not col.primary_key}

        # Remove keys from the dictionary
        if exclude_cols is not None:
            for key in exclude_cols:
                update_dict.pop(key, None)

        # set the last_update column to the current time
        update_dict['last_updated'] = datetime.datetime.now()

        # Return the Upsert statement
        return insert_stmt.on_conflict_do_update(index_elements=[getattr(table, id_col_name)], set_=update_dict)

    def _excute_upsert_stmt(self, upsert_stmt: Insert) -> None:

        try:
            # Create a new session
            with self.session_maker() as session:
                # Execute the upsert statement
                session.execute(upsert_stmt)
                # Commit the changes and close the session
                session.commit()
        except Exception as error:
            logging.error(f"ERROR : {error}", exc_info=True)
            session.rollback() # type: ignore
