#%%

import logging

from typing import List

from tables.tables_model import Films, Users

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#%%

def session_maker(connection_uri: str) -> sessionmaker:

    # Define the database connection
    engine = create_engine(connection_uri)

    # Define a session factory
    return sessionmaker(bind=engine)

def get_films_list_db(Session_Maker: sessionmaker) -> List:

    try:

        with Session_Maker() as session:

            films = session.query(Films.title).all()
            return [film[0] for film in films]

    except Exception as error:
        logging.error(f'ERROR: {error}', exc_info=True)
        return []

def get_film_info_db(title: str , Session_Maker: sessionmaker) -> dict:

    try:

        with Session_Maker() as session:

            film = session.query(Films).filter(Films.title == title).one()

        return {'title': film.title,
                'availability': film.availability,
                'imax_3d_ov': film.imax_3d_ov,
                'imax_ov': film.imax_ov,
                'hd_ov': film.hd_ov,
                'last_checked': film.last_checked,
                'link': film.link}

    except Exception as error:
        logging.error(f'ERROR: {error}', exc_info=True)
        return {}

def update_users_db(chat_id, message_id, title, Session_Maker: sessionmaker) -> None:
    # sourcery skip: hoist-statement-from-if, use-named-expression

    try:

        with Session_Maker() as session:

            # check if a row with the same chat_id and title already exists
            existing_row = session.query(Users).filter(Users.chat_id== str(chat_id) , Users.title==title).first()

            if existing_row:
                # update the existing row
                existing_row.message_id = message_id

            else:
                # create a new row
                new_row = Users(chat_id=chat_id, message_id=message_id, title=title)
                session.add(new_row)

            session.commit()

    except Exception as error:
        logging.error(f'ERROR: {error}', exc_info=True)

    finally:
        session.close()