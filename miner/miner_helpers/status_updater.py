#%%
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from typing import List

from tables.tables_model import Films
#%%

def session_maker(connection_uri: str):

    # Define the database connection
    engine = create_engine(connection_uri)

    # Define a session factory
    return sessionmaker(bind=engine)

#%%

def update_films_list(rows: List[dict], Session_Maker) -> None:

    # Create a new session
    session = Session_Maker()

    # TODO: Change this logic with bulk_insert_mappings and bulk_update_mappings later.

    for row in rows:
        title = row.get('title')
        link = row.get('link')
        img_link = row.get('img_link')

        try:
            # Check if the row already exists
            row_exists = session.query(Films).filter(Films.title == title).first() is not None

            if row_exists:
                # Update the existing row
                session.query(Films).filter(Films.title == title).update({
                    Films.link: link,
                    Films.img_link: img_link
                })
            else:
                # Insert a new row
                new_row = Films(
                    title=title,
                    link=link,
                    img_link=img_link
                )
                session.add(new_row)

        except Exception as error:
            logging.error(f'ERROR : {error}', exc_info=True)
            session.rollback()

    # Commit the changes and close the session
    session.commit()
    session.close()

#%%

def update_films_status(films: List[dict], Session) -> None:

    # Create a new session
    session = Session()

    # TODO: Change this logic with bulk_insert_mappings and bulk_update_mappings later.

    for film in films:
        title = film.get('title')
        link = film.get('link')
        img_link = film.get('img_link')
        last_checked = film.get('last_checked')
        availability = film.get('availability')
        imax_3d_ov = film.get('imax_3d_ov')
        imax_ov = film.get('imax_ov')
        hd_ov = film.get('hd_ov')

        try:
            # Check if the row already exists
            row_exists = session.query(Films).filter(Films.title == title).first() is not None

            if row_exists:

                # Capture Data Change in availability column
                last_update = session.query(Films.availability).filter(Films.title == title).first()

                # Update the existing row
                session.query(Films).filter(Films.title == title).update({
                    Films.last_checked: last_checked,
                    Films.availability: availability,
                    Films.imax_3d_ov: imax_3d_ov,
                    Films.imax_ov: imax_ov,
                    Films.hd_ov: hd_ov,
                    Films.last_update: last_update[0]
                })
            else:
                # Insert a new row
                new_row = Films(
                    title=title,
                    link = link,
                    img_link = img_link,
                    last_checked = last_checked,
                    availability = availability,
                    imax_3d_ov = imax_3d_ov,
                    imax_ov = imax_ov,
                    hd_ov = hd_ov
                )
                session.add(new_row)

        except Exception as error:
            logging.error(f'ERROR : {error}', exc_info=True)
            session.rollback()

    # Commit the changes and close the session
    session.commit()
    session.close()