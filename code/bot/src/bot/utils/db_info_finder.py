# %%

import logging

from typing import Type, Any
from datetime import date, time
from sqlalchemy.sql import select, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import update, and_, distinct

from common.db.manager import DBManager
from common.db.db_model import Films, UpcomingFilms, Performances, Users

# %%

class FilmInfoFinder(DBManager):

    def __init__(self, connection_uri: str):
        super().__init__(connection_uri)

    def get_film_id_by_title(self, title: str):
        """returns film_id by title from films table"""
        film = self.execute_fetch_one(Films, lambda film: func.lower(film.title) == title.lower())
        return film.film_id

    def check_performance_version_availability(self, film_id:str, versions:dict) -> bool:
        """ Checks if the perfomance of a film is available based on the versions"""

        version_filter= [ getattr(Performances, key) == value for key, value in versions.items() if value != 0 ] # noqa: E712
        stmt = select(Performances).where( and_(Performances.film_id == film_id, *version_filter))
        result = self.execute_query_all(stmt)
        return len(result) > 0

    def get_performance_ids_by_version(self, film_id:str, versions:dict) -> list[str] | None:
        """ Checks if the perfomance of a film is available based on the versions"""

        version_filter= [ getattr(Performances, key) == value for key, value in versions.items() if value != 0 ] # noqa: E712
        stmt = select(Performances.performance_id).where( and_(Performances.film_id == film_id, *version_filter))
        return self.execute_query_all(stmt)

    def get_performance_dates_by_film_id(self, film_id:str, versions:dict) -> list[date] | None:
        """ Retrieves the performance dates of a film based on the versions"""

        version_filter= [ getattr(Performances, key) == value for key, value in versions.items() if value != 0 ] # noqa: E712
        stmt = select(distinct(Performances.performance_date)).where(and_(Performances.film_id == film_id, *version_filter))
        return self.execute_query_all(stmt)

    def get_performance_hours_by_film_id(self, film_id:str, versions:dict, performance_date) -> list[time] | None:
        version_filter= [ getattr(Performances, key) == value for key, value in versions.items() if value != 0 ] # noqa: E712
        stmt = (
                select(distinct(Performances.performance_time))
                .where(and_(Performances.film_id == film_id, Performances.performance_date == performance_date, *version_filter))
                )
        return self.execute_query_all(stmt)

    def get_upcomings_films_list(self) -> list[dict[str, Any]] | None:
        return self.execute_query_mapping_all(self._create_upcomings_films_stmt())

    def get_showing_films_list(self) -> list[Type] | None:
        """ Get a list of films that are currently showing.
            INFO: performance_date >= current_date
        """
        return self.execute_query_all(self._create_showing_films_stmt())

    def _create_upcomings_films_stmt(self) -> select:
        return select(UpcomingFilms.title, UpcomingFilms.upcoming_film_id).where( and_(UpcomingFilms.is_trackable, ~ UpcomingFilms.is_released) ) # noqa: E712

    def _create_showing_films_stmt(self) -> select:
        return (
            select(distinct(Films.title))
            .join(Performances, Films.film_id == Performances.film_id)
            .where(Performances.performance_date >= func.current_date())
            )

    def upsert_users(self, chat_id:str, message_id:str, title:str, flags:str) -> bool:
        """ Insert a user info to the database for notification.
            If the row with the same chat_id and title already exists, it just updates the message_id.
            Returns True if the upsert is successful, False otherwise."""

        # sourcery skip: extract-duplicate-method, use-named-expression
        try:
            with self.session_maker() as session:

                # Check if a row with the same chat_id and title already exists
                stmt = select(Users).filter(Users.chat_id == chat_id, func.lower(Users.title) == title.lower())
                existing_row = session.execute(stmt).scalar_one_or_none()

                if existing_row:
                    # Update the existing row
                    update_stmt = (
                        update(Users)
                        .where(Users.chat_id == chat_id, func.lower(Users.title) == title.lower())
                        .values(message_id=message_id, flags=flags)
                    )
                    session.execute(update_stmt)
                else:
                    # Create a new row
                    new_row = Users(chat_id=chat_id, message_id=message_id, title=title, flags=flags)
                    session.add(new_row)

                session.commit()
            return True

        except SQLAlchemyError as error:
            logging.error(f"Database Error: {error}", exc_info=True)
            session.rollback()
            return False
        except Exception as error:  # Consider more specific exceptions

            logging.error(f"Error: {error}", exc_info=True)
            session.rollback()
            return False

    def _get_user_by_user_id(self, user_id: int) -> Type | None:
        """Get an existing user in the users table given its user_id."""
        return self.execute_fetch_one(Users, lambda user: user.user_id == user_id)
