# %%

import logging

from typing import List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .db_model import Films, Users

# %%


class DBInfoFinder:
    def __init__(self, connection_uri: str):
        self.connection_uri = connection_uri
        self.session_maker = self._session_maker()

    def get_films_list_db(self) -> List[str]:
        try:
            with self.session_maker() as session:
                films = session.query(Films.title).filter(Films.trackable == True).all()  # noqa: E712
                return [film[0] for film in films]
        except Exception as error:
            logging.error(f"ERROR: {error}", exc_info=True)
            return []

    def get_film_info_db(self, title: str) -> dict:
        try:
            with self.session_maker() as session:
                film = session.query(Films).filter(Films.title == title).first()
            if film:
                return {
                    "title": film.title,
                    "availability": film.availability,
                    "imax_3d_ov": film.imax_3d_ov,
                    "imax_ov": film.imax_ov,
                    "hd_ov": film.hd_ov,
                    "last_checked": film.last_checked,
                    "link": film.link,
                }
            logging.info(f"No film with title {title} found in the database")
            return {}
        except Exception as error:
            logging.error(f"ERROR: {error}", exc_info=True)
            return {}

    def update_users_db(self, chat_id, message_id, title) -> None:
        # sourcery skip: hoist-statement-from-if, use-named-expression

        try:
            with self.session_maker() as session:
                # check if a row with the same chat_id and title already exists
                existing_row = session.query(Users).filter(Users.chat_id == str(chat_id), Users.title == title).first()
                if existing_row:
                    # update the existing row
                    existing_row.message_id = message_id
                else:
                    # create a new row
                    new_row = Users(chat_id=chat_id, message_id=message_id, title=title)
                    session.add(new_row)
                session.commit()
        except Exception as error:
            logging.error(f"ERROR: {error}", exc_info=True)

    def _session_maker(self) -> sessionmaker:
        # Define the database connection
        engine = create_engine(self.connection_uri, pool_size=2, max_overflow=2)
        # Define a session factory
        return sessionmaker(bind=engine)
