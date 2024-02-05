# %%
import logging

from typing import List, Dict, Tuple
from sqlalchemy.sql import select, func
from sqlalchemy import Update, update, and_, tuple_
from sqlalchemy.dialects.postgresql import insert, Insert

from common.db.manager import DBManager
from common.call_parser import CallParser
from common.db.db_model import Films, UpcomingFilms, Performances, Users, UsersFilmInfo


# %%

class FilmDatabaseManager(DBManager):
    """This class manages the films and performances tables in the database"""

    def __init__(self, connection_uri: str):
        super().__init__(connection_uri)

    def update_films_table(self, films_list: List[dict] | None) -> None:
        """Updates the films table."""
        if films_list is not None:
            logging.info("[ ] Updating Films table!")
            # Upsert statement
            upsert_stmt = self._create_upsert_stmt(Films, "film_id", films_list)
            # Execute the upsert statement
            self.execute_insert_stmt(upsert_stmt)
            logging.info("[*] Updated Films table!")
        else:
            logging.warning("Films list is None")

    def update_performances_table(self, performances_list: List[dict] | None) -> None:
        """Updates the performances table."""
        if performances_list is not None:
            logging.info("[ ] Updating Performances table!")
            # Upsert statement
            upsert_stmt = self._create_upsert_stmt(Performances, "performance_id", performances_list)
            # Execute the upsert statement
            self.execute_insert_stmt(upsert_stmt)
            logging.info("[*] Updated Performances table!")
        else:
            logging.warning("Performances list is None")

    def update_upcoming_films_table(self, upcoming_films_list: List[dict] | None) -> None:
        """Updates the upcoming films table."""

        if upcoming_films_list is not None:

            logging.info("[ ] Updating Upcoming Films table!")

            # Upsert statement
            exclude_cols = ['title', 'is_released', 'is_trackable', 'upcoming_film_id', 'film_id']
            upsert_stmt = self._create_upsert_stmt(UpcomingFilms, "title", upcoming_films_list, exclude_cols= exclude_cols)

            # Execute the upsert statement
            self.execute_insert_stmt(upsert_stmt)
            logging.info("[*] Updated Upcoming Films table!")
        else:
            logging.warning("Upcoming Films list is None")

    def update_released_films_in_upcoming_films_table(self) -> None:
        """Updates the released films in the upcoming films table.
        If a film is released then its film_id will be updated in the upcoming films table.
        It is used to trigger to notification that a film has been released.
        """

        logging.info("[ ] Updating released films in Upcoming Films table!")
        # Update statement
        update_stmt = self._create_update_released_film_stmt()
        logging.info("[*] Updated released films in Upcoming Films table!")
        # Execute the upsert statement
        self.execute_insert_stmt(update_stmt)

    def update_users_table(self) -> None:

        logging.info("[ ] Updating Users table!")
        # Update statement
        update_stmt = self._create_users_table_film_id_update_stmt()
        logging.info("[*] Updated Users table!")
        # Execute the update statement
        self.execute_insert_stmt(update_stmt)

    def update_notified_users_table(self, users_list: List[UsersFilmInfo]) -> None:

        logging.info("[ ] Updating notified users' status Users table!")
        # Update statement
        user_film_pair = [(ufi.user_id, ufi.film_id) for ufi in users_list]
        update_stmt = self._create_notfied_users_update_stmt(user_film_pair)
        logging.info("[*] Updated notified users' status Users table!")
        # Execute the update statement
        self.execute_insert_stmt(update_stmt)

    @staticmethod
    def _extract_film_data(film_dict, keys: List[str]) -> Dict[str, str | int]:
        """Extracts film data from a dictionary."""
        return {key: film_dict.get(key) for key in keys}

    def _create_upsert_stmt(self, table, id_col_name: str, update_list: List[dict], exclude_cols: List[str] | None = None) -> Insert:
        """Creates an upsert statement for a table"""

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
        """Creates an update statement for released films in the upcoming films table.

        SQL Query:
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
        """Creates an update statement for updating released films id in the users table.

        # INFO: Corrected query
        SQL Query:
        ```sql
        -- Update Users with Released Films
        UPDATE tracker.users u
        SET film_id = uf.film_id
        FROM tracker.upcoming_films uf
        WHERE uf.is_trackable = TRUE
        AND uf.is_released = TRUE
        AND u.title = uf.title;
        ```
        """
        # Scalar subquery
        # Subquery with case-insensitive comparison
        subquery = (
            select(UpcomingFilms.film_id, UpcomingFilms.title)
            .where(and_(UpcomingFilms.is_trackable == True, UpcomingFilms.is_released == True))  # noqa: E712
            .subquery()
        )

        # Update statement with case-insensitive comparison
        return (
            update(Users)
            .values(film_id=subquery.c.film_id)
            .where(func.lower(Users.title) == func.lower(subquery.c.title))
        )

    @staticmethod
    def _create_notfied_users_update_stmt(user_film_pairs: List[Tuple[int, str]]) -> Update:
        """ Creates an update statement for notifying users.
        Sets notified = True for pair of user_id and film_id.
        """

        return update(Users).where(
            tuple_(Users.user_id, Users.film_id).in_(user_film_pairs)).values(notified=True)

    def _get_film_by_title(self, title: str) -> Films |None:
        """Get an existing row in the films table given its title."""
        return self.execute_fetch_one(Films, lambda film: func.lower(film.title) == title.lower())

    def _get_film_by_film_id(self, film_id: str) -> Films | None:
        """Get an existing row in the films table given its film id."""
        return self.execute_fetch_one(Films, lambda film: film.film_id == film_id)

    def _get_performance_by_performance_id(self, performance_id: str) -> Performances | None:
        """Get an existing row in the performances table given its performance id."""
        return self.execute_fetch_one(Performances, lambda performance: performance.performance_id == performance_id)

    def _get_performance_by_film_id(self, film_id: str) -> Performances | None:
        """Get an existing row in the performances table given its film id."""
        return self.execute_fetch_one(Performances, lambda performance: performance.film_id == film_id)

    def _get_upcoming_film_by_title(self, title: str) -> UpcomingFilms | None:
        """Get an existing row in the upcoming films table given its title."""
        return self.execute_fetch_one(UpcomingFilms, lambda upcoming_film: func.lower(upcoming_film.title) == title.lower())

    def _get_upcoming_user_by_title(self, title: str) -> UpcomingFilms | None:
        """Get an existing rows in the users table given its title."""
        return self.execute_fetch_one(UpcomingFilms, lambda user: func.lower(user.title) == title.lower())

    def _get_user_by_user_id(self, user_id: int) -> Users | None:
        """Get an existing row in the users table given its user id."""
        return self.execute_fetch_one(Users, lambda user: user.user_id == user_id)

    def get_users_to_notify(self) -> List[UsersFilmInfo]:
        """Get list of users to notify with information about first available performance based on user preferences.

        SQL Query:
        ```sql
        SELECT
            u.film_id,
            u.title,
            u.user_id,
            u.chat_id,
            u.message_id,
            u.notified,
            u.flags,
            p.is_3d,
            p.is_ov,
            p.is_imax,
            p.last_updated
        FROM
            tracker.users as u
        INNER JOIN
            tracker.performances as p ON u.film_id = p.film_id
        WHERE
            u.notified = FALSE
            AND u.film_id IS NOT NULL;
        ```
        Returns
        -------
        List[UsersFilmInfo]
            List of users to notify.
        """

        users_list = []

        # Join Users with Performances to fetch in a single query
        query = ( select(Users.film_id, Users.title, Users.flags,
                        Users.user_id, Users.chat_id, Users.message_id, Users.notified,
                        Films.name,
                        Performances.performance_id,
                        Performances.is_3d, Performances.is_ov, Performances.is_imax, Performances.last_updated)
                .join(Performances, Users.film_id == Performances.film_id)
                .join(Films, Users.film_id == Films.film_id)
                .where(and_(Users.notified == False, Users.film_id.isnot(None)))  # noqa: E712
            )

        unnotified_users = self.execute_query_mapping_all(query)

        if unnotified_users is not None:

            # Use a set to avoid duplicate users
            seen = set()

            # Filter users based on user's preferences
            unnotified_users = [user
                                for user in unnotified_users
                                if all(getattr(user, key) == value for key, value in CallParser.parse(user.flags).items() if value != 2)]

            unnotified_users = [user
                                for user in unnotified_users
                                if (user.user_id, user.film_id) not in seen and not seen.add((user.user_id, user.film_id))]

            for user in unnotified_users:
                # create a UsersFilmInfo object with the user's data and performance data
                user = UsersFilmInfo(
                    user_id=user.user_id,
                    chat_id=user.chat_id,
                    message_id=user.message_id,
                    notified=user.notified,
                    film_id=user.film_id,
                    title=user.title,
                    last_updated=user.last_updated,
                    is_imax=user.is_imax,
                    is_ov=user.is_ov,
                    is_3d=user.is_3d,
                    flags=user.flags,
                    name=user.name,
                    performance_id=user.performance_id
                    )

                users_list.append(user)

        return users_list
