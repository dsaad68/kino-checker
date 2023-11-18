# %%
import logging

from typing import List, Union, Dict, Optional, Type, Callable

from sqlalchemy.sql import select, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import insert, Insert
from sqlalchemy import Update, create_engine, update, and_

from .db_model import Films, Performances, UpcomingFilms, Users

# %%

# IDEA: Think about breakdown of this class two classes one for updating and one for querying
class FilmDatabaseManager:
    """This class manages the films and performances tables in the database"""

    def __init__(self, connection_uri: str):
        self.connection_uri = connection_uri
        self.session_maker = self._session_maker()

    def update_films_table(self, films_list: Optional[List[dict]]) -> None:
        """Updates the films table."""
        if films_list is not None:
            logging.info("[ ] Updating Films table!")
            # Upsert statement
            upsert_stmt = self._create_upsert_stmt(Films, "film_id", films_list)
            # Execute the upsert statement
            self._excute_stmt(upsert_stmt)
            logging.info("[*] Updated Films table!")
        else:
            logging.warning("Films list is None")

    def update_performances_table(self, performances_list: Optional[List[dict]]) -> None:
        """Updates the performances table."""
        if performances_list is not None:
            logging.info("[ ] Updating Performances table!")
            # Upsert statement
            upsert_stmt = self._create_upsert_stmt(Performances, "performance_id", performances_list)
            # Execute the upsert statement
            self._excute_stmt(upsert_stmt)
            logging.info("[*] Updated Performances table!")
        else:
            logging.warning("Performances list is None")

    def update_upcoming_films_table(self, upcoming_films_list: Optional[List[dict]]) -> None:
        """Updates the upcoming films table."""

        if upcoming_films_list is not None:

            logging.info("[ ] Updating Upcoming Films table!")

            # Upsert statement
            exclude_cols = ['title', 'is_released', 'is_trackable', 'upcoming_film_id', 'film_id']
            upsert_stmt = self._create_upsert_stmt(UpcomingFilms, "title", upcoming_films_list, exclude_cols= exclude_cols)

            # Execute the upsert statement
            self._excute_stmt(upsert_stmt)
            logging.info("[*] Updated Upcoming Films table!")
        else:
            logging.warning("Upcoming Films list is None")

    def update_released_films_in_upcoming_films_table(self) -> None:
        """update the released films in the upcoming films table."""

        logging.info("[ ] Updating released films in Upcoming Films table!")
        # Update statement
        update_stmt = self._create_update_released_film_stmt()
        logging.info("[*] Updated released films in Upcoming Films table!")
        # Execute the upsert statement
        self._excute_stmt(update_stmt)

    def update_users_table(self) -> None:

        logging.info("[ ] Updating Users table!")
        # Update statement
        update_stmt = self._create_users_table_film_id_update_stmt()
        logging.info("[*] Updated Users table!")
        # Execute the update statement
        self._excute_stmt(update_stmt)

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

        # Build a dictionary for updating all columns except the primary key
        update_dict = {col.name: insert_stmt.excluded[col.name] for col in table.__table__.columns if not col.primary_key}

        # Remove keys from the dictionary
        if exclude_cols is not None:
            for key in exclude_cols:
                update_dict.pop(key, None)

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

        # Define the subquery with case-insensitive comparison
        film_id_subquery = select(Films.film_id).where(func.lower(UpcomingFilms.title) == func.lower(Films.title)).correlate(UpcomingFilms).scalar_subquery()

        # Update statement with case-insensitive comparison
        update_stmt = (
            update(UpcomingFilms)
            .values(film_id=film_id_subquery, is_released=True)
            .where(and_(UpcomingFilms.is_trackable == True, func.lower(UpcomingFilms.title) == func.lower(Films.title)))   # noqa: E712
        )
        return update_stmt

    @staticmethod
    def _create_users_table_film_id_update_stmt() -> Update:
        """Create an update statement for updating released films id in the users table.

        ```sql
        -- Update Users with Released Films
        UPDATE tracker.users u
        SET film_id = f.film_id
        FROM tracker.films f
        JOIN tracker.upcoming_films uf ON f.title = uf.title
        WHERE uf.is_trackable = TRUE
        AND uf.is_released = FALSE
        AND u.title = f.title;

        ```
        """
        # Scalar subquery
        # Subquery with case-insensitive comparison
        subquery = (
            select(Films.film_id)
            .join(UpcomingFilms, func.lower(Films.title) == func.lower(UpcomingFilms.title))
            .where(and_(UpcomingFilms.is_trackable == True, UpcomingFilms.is_released == False))  # noqa: E712
            .scalar_subquery()
        )

        # Update statement with case-insensitive comparison
        return (
            update(Users)
            .values(film_id=subquery)
            .where(func.lower(Users.title) == func.lower(UpcomingFilms.title))
        )

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

    def _execute_query(self, model: Type, filter_condition: Callable) -> Union[Type, None]:
        """Execute a query with a given model and filter condition."""

        # sourcery skip: class-extract-method, extract-duplicate-method
        try:
            with self.session_maker() as session:
                return session.execute(select(model).where(filter_condition(model))).scalars().first()
        except SQLAlchemyError as error:
            logging.error(f"Database Error: {error}", exc_info=True)
            session.rollback()  # type: ignore
            return None
        except Exception as error:
            logging.error(f"ERROR : {error}", exc_info=True)
            session.rollback()  # type: ignore
            return None

    def _get_film_by_title(self, title: str) -> Union[Films, None]:
        """Get an existing row in the films table given its title."""
        return self._execute_query(Films, lambda film: func.lower(film.title) == title.lower())

    def _get_film_by_film_id(self, film_id: str) -> Union[Films, None]:
        """Get an existing row in the films table given its film id."""
        return self._execute_query(Films, lambda film: film.film_id == film_id)

    def _get_performance_by_performance_id(self, performance_id: str) -> Union[Performances, None]:
        """Get an existing row in the performances table given its performance id."""
        return self._execute_query(Performances, lambda performance: performance.performance_id == performance_id)

    def _get_performance_by_film_id(self, film_id: str) -> Union[Performances, None]:
        """Get an existing row in the performances table given its film id."""
        return self._execute_query(Performances, lambda performance: performance.film_id == film_id)

    def _get_upcoming_film_by_title(self, title: str) -> Union[UpcomingFilms, None]:
        """Get an existing row in the upcoming films table given its title."""
        return self._execute_query(UpcomingFilms, lambda upcoming_film: func.lower(upcoming_film.title) == title.lower())

    def _get_upcoming_user_by_title(self, title: str) -> Union[Users, None]:
        """Get an existing rows in the users table given its title."""
        return self._execute_query(UpcomingFilms, lambda user: func.lower(user.title) == title.lower())

    def get_users_to_notify(self) -> Union[List[Users], None]:
        """Get list of users to notify."""

        # sourcery skip: extract-duplicate-method
        try:
            with self.session_maker() as session:
                return session.execute(select(Users).where(Users.film_id.isnot(None), Users.notified.is_(False))).scalars().all()
        except SQLAlchemyError as error:
            logging.error(f"Database Error: {error}", exc_info=True)
            session.rollback()  # type: ignore
            return None
        except Exception as error:
            logging.error(f"ERROR : {error}", exc_info=True)
            session.rollback()  # type: ignore
            return None
