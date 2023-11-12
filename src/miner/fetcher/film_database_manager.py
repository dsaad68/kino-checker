# %%
import logging
import datetime

from typing import List, Union, Dict, Optional

from sqlalchemy.sql import select
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import Update, create_engine, update, and_
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
            upsert_stmt = self._create_upsert_stmt(Films, "film_id", films_list)
            # Execute the upsert statement
            self._excute_stmt(upsert_stmt)

        else:
            logging.warning("Films list is None")

    def update_performances_table(self, performances_list: Optional[List[dict]]) -> None:
        if performances_list is not None:
            # Upsert statement
            upsert_stmt = self._create_upsert_stmt(Performances, "performance_id", performances_list)
            # Execute the upsert statement
            self._excute_stmt(upsert_stmt)

        else:
            logging.warning("Performances list is None")

    def update_upcoming_films_table(self, upcoming_films_list: Optional[List[dict]]) -> None:
        """Updates the upcoming films table."""

        if upcoming_films_list is not None:
            exclude_cols = ["is_release", "is_trackable", "title"]
            # Upsert statement
            upsert_stmt = self._create_upsert_stmt(UpcomingFilms, "title", upcoming_films_list, exclude_cols=exclude_cols)

            # Execute the upsert statement
            self._excute_stmt(upsert_stmt)

        else:
            logging.warning("Performances list is None")

    def update_released_films_in_upcoming_films_table(self) -> None:
        """update the released films in the upcoming films table."""

        # Update statement
        update_stmt = self._create_update_released_film_stmt()

        # Execute the upsert statement
        self._excute_stmt(update_stmt)

    @staticmethod
    def _get_existing_row(title: str, session: Session) -> Union[Films, None]:
        """Get an existing row in the films table given its title."""
        return session.query(Films).filter(Films.title == title).first()

    @staticmethod
    def _extract_film_data(film_dict, keys: List[str]) -> Dict[str, Union[str, int]]:
        """Extracts film data from a dictionary."""
        return {key: film_dict.get(key) for key in keys}

    def _session_maker(self) -> sessionmaker:
        """Create a session factory for connecting to the database."""

        # Define the database connection
        engine = create_engine(self.connection_uri, pool_size=2, max_overflow=2)
        # Define a session factory
        return sessionmaker(bind=engine)

    def _create_upsert_stmt(self, table, id_col_name: str, update_list: List[dict], exclude_cols: Optional[List[str]] = None) -> Insert:
        """Create an upsert statement for a table"""

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
        update_dict["last_updated"] = datetime.datetime.now()

        # Return the Upsert statement
        return insert_stmt.on_conflict_do_update(index_elements=[getattr(table, id_col_name)], set_=update_dict)

    @staticmethod
    def _create_update_released_film_stmt() -> Update:
        """Create an update statement for released films in the upcoming films table.

        ```sql
        -- Update Released Films
        UPDATE tracker.upcoming_films
        SET
            film_id = f.film_id,
            is_released = TRUE
        FROM tracker.films f
        WHERE
            tracker.upcoming_films.title = f.title
            AND tracker.upcoming_films.is_trackable = TRUE;
        ```
        """
        # sourcery skip: inline-immediately-returned-variable
        stmt = (
            update(UpcomingFilms)
            .values(film_id=select([Films.c.film_id]).where(UpcomingFilms.c.title == Films.c.title).as_scalar(), is_released=True)
            .where(and_(UpcomingFilms.c.is_trackable == True, UpcomingFilms.c.title == Films.c.title))  # noqa: E712
        )
        return stmt

    # TODO: Extend this function to be able to excute statements generally
    def _excute_stmt(self, stmt: Union[Insert, Update]) -> None:
        """Execute an upsert statement."""

        try:
            # Create a new session
            with self.session_maker() as session:
                # Execute the upsert statement
                session.execute(stmt)
                # Commit the changes and close the session
                session.commit()
        except Exception as error:
            logging.error(f"ERROR : {error}", exc_info=True)
            session.rollback()  # type: ignore
