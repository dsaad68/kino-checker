# %%
import logging
import datetime

from typing import List, Union, Dict

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .db_model import Films, Users

# %%


class FilmDatabaseManager:
    def __init__(self, connection_uri: str):
        self.connection_uri = connection_uri
        self.session_maker = self._session_maker()

    def update_films_list(self, rows: List[dict]) -> None:
        new_rows: list = []
        update_rows: list = []

        try:
            # Create a new session
            with self.session_maker() as session:
                # sourcery skip: extract-method, use-named-expression
                for row in rows:
                    keys = ["title", "link", "img_link"]
                    film_data = self._extract_film_data(row, keys)

                    # Check if the row already exists
                    row_exists = self.get_existing_row(film_data.get("title"), session)

                    if row_exists:
                        # Update the existing row
                        update_rows.append({"id": row_exists.id, "link": film_data.get("link"), "img_link": film_data.get("img_link")})

                    else:
                        # Insert a new row
                        new_rows.append(film_data)

                logging.info(f"New rows: {len(new_rows)}")
                logging.info(f"Update rows: {len(update_rows)}")

                # Perform bulk insert and update
                if new_rows:
                    session.bulk_insert_mappings(Films, new_rows)
                if update_rows:
                    session.bulk_update_mappings(Films, update_rows)

                # Commit the changes and close the session
                session.commit()

        except Exception as error:
            logging.error(f"ERROR : {error}", exc_info=True)
            session.rollback()

    def update_films_status(self, films: List[dict]) -> None:
        update_rows: list = []

        try:
            with self.session_maker() as session:
                for film in films:
                    title = film.get("title")
                    last_checked = film.get("last_checked")
                    availability = film.get("availability")
                    imax_3d_ov = film.get("imax_3d_ov")
                    imax_ov = film.get("imax_ov")
                    hd_ov = film.get("hd_ov")

                    # Check if the row already exists
                    row_exists = self.get_existing_row(title, session)

                    if availability and not row_exists.last_update:
                        # Update the existing row with the availability
                        update_rows.append(
                            {
                                "id": row_exists.id,
                                "last_checked": last_checked,
                                "availability": availability,
                                "imax_3d_ov": imax_3d_ov,
                                "imax_ov": imax_ov,
                                "hd_ov": hd_ov,
                                "last_update": row_exists.availability,
                                "availability_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            }
                        )

                    else:
                        # Update the existing row without the availability
                        update_rows.append(
                            {
                                "id": row_exists.id,
                                "last_checked": last_checked,
                                "availability": availability,
                                "imax_3d_ov": imax_3d_ov,
                                "imax_ov": imax_ov,
                                "hd_ov": hd_ov,
                                "last_update": row_exists.availability,
                            }
                        )

                logging.info(f"Update rows: {len(update_rows)}")

                # Perform bulk update
                session.bulk_update_mappings(Films, update_rows)

                # Commit the changes
                session.commit()

        except Exception as error:
            logging.error(f"ERROR : {error}", exc_info=True)
            session.rollback()

    def get_films_db_status(self) -> List[dict]:
        try:
            with self.session_maker() as session:
                subquery = session.query(Films.title).filter(Films.availability != Films.last_update, Films.availability == True)  # noqa: E712

                results = (
                    session.query(
                        Users.chat_id,
                        Users.message_id,
                        Users.title,
                        Films.availability,
                        Films.imax_3d_ov,
                        Films.imax_ov,
                        Films.hd_ov,
                        Films.last_checked,
                        Films.link,
                    )
                    .join(Films, Films.title == Users.title)
                    .filter(Users.title.in_(subquery))
                ).all()

                return [
                    {
                        "chat_id": row.chat_id,
                        "title": row.title,
                        "message_id": row.message_id,
                        "availability": row.availability,
                        "imax_3d_ov": row.imax_3d_ov,
                        "imax_ov": row.imax_ov,
                        "hd_ov": row.hd_ov,
                        "last_checked": row.last_checked,
                        "link": row.link,
                    }
                    for row in results
                ]

        except Exception as error:
            logging.error(f"ERROR : {error}", exc_info=True)

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
