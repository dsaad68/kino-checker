# %%

import logging

from typing import Type
from sqlalchemy.sql import select, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine, and_, distinct
# from sqlalchemy.dialects.postgresql import Insert

from .db_model import Films, UpcomingFilms, Performances #, Users

# %%

# [ ] Update this class to new schema

class FilmInfoFinder:

    def __init__(self, connection_uri: str):
        self.connection_uri = connection_uri
        self.session_maker = self._session_maker()

    def _session_maker(self) -> sessionmaker:
        """Create a session factory for connecting to the database."""

        # Define the database connection
        engine = create_engine(self.connection_uri, pool_size=2, max_overflow=2)
        # Define a session factory
        return sessionmaker(bind=engine)

    def get_upcommings_films_list(self) -> list[Type] | None:
        return self._execute_query(self._create_upcommings_films_stmt())

    def get_showing_films_list(self) -> list[Type] | None:
        return self._execute_query(self._create_showing_films_stmt())

    def _create_upcommings_films_stmt(self) -> select:
        return select(UpcomingFilms.title).where( and_(UpcomingFilms.is_trackable == True, UpcomingFilms.is_released == False) ) # noqa: E712

    def _create_showing_films_stmt(self) -> select:
        return (
            select(distinct(Films.title))
            .join(Performances, Films.film_id == Performances.film_id)
            .where(Performances.performance_date >= func.current_date())
            )

    def _execute_query(self, stmt) -> list[Type] | None:
        """Execute a query with a given model and filter condition."""

        # sourcery skip: class-extract-method, extract-duplicate-method
        try:
            with self.session_maker() as session:
                return session.execute(stmt).scalars().all()
        except SQLAlchemyError as error:
            logging.error(f"Database Error: {error}", exc_info=True)
            session.rollback()  # type: ignore
            return None
        except Exception as error:
            logging.error(f"ERROR : {error}", exc_info=True)
            session.rollback()  # type: ignore
            return None

    # [ ] Get the performances info for a given film
    # [ ] Insert a user info to the database for notification

    # def get_film_info_db(self, title: str) -> dict:
    #     try:
    #         with self.session_maker() as session:
    #             film = session.query(Films).filter(Films.title == title).first()
    #         if film:
    #             return {
    #                 "title": film.title,
    #                 "availability": film.availability,
    #                 "imax_3d_ov": film.imax_3d_ov,
    #                 "imax_ov": film.imax_ov,
    #                 "hd_ov": film.hd_ov,
    #                 "last_checked": film.last_checked,
    #                 "link": film.link,
    #             }
    #         logging.info(f"No film with title {title} found in the database")
    #         return {}
    #     except Exception as error:
    #         logging.error(f"ERROR: {error}", exc_info=True)
    #         return {}

    # def update_users_db(self, chat_id, message_id, title) -> None:
    #     # sourcery skip: hoist-statement-from-if, use-named-expression

    #     try:
    #         with self.session_maker() as session:
    #             # checks if a row with the same chat_id and title already exists
    #             existing_row = session.query(Users).filter(Users.chat_id == str(chat_id), Users.title == title).first()
    #             if existing_row:
    #                 # update the existing row
    #                 existing_row.message_id = message_id
    #             else:
    #                 # create a new row
    #                 new_row = Users(chat_id=chat_id, message_id=message_id, title=title)
    #                 session.add(new_row)
    #             session.commit()
    #     except Exception as error:
    #         logging.error(f"ERROR: {error}", exc_info=True)
