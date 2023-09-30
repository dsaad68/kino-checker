#%%
import logging
import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from typing import List

from .db_model import Films
#%%

def session_maker(connection_uri: str):

    # Define the database connection
    engine = create_engine(connection_uri, pool_size=2, max_overflow=2)

    # Define a session factory
    return sessionmaker(bind=engine)

#%%

def update_films_list(rows: List[dict], Session_Maker) -> None:
    # TODO: this function should be refactored 
    
    new_rows: list = []
    update_rows: list = []

    try:

        # Create a new session
        with Session_Maker() as session:

            # sourcery skip: extract-method, use-named-expression
            for row in rows:
                title = row.get('title')
                link = row.get('link')
                img_link = row.get('img_link')

                # Check if the row already exists
                row_exists = session.query(Films).filter(Films.title == title).first()

                if row_exists:

                    # Update the existing row
                    update_rows.append({
                        'id': row_exists.id,
                        'link': link,
                        'img_link': img_link
                        })

                else:

                    # Insert a new row
                    new_rows.append({
                        'title':title,
                        'link':link,
                        'img_link':img_link
                    })

            logging.info(f'New rows: {len(new_rows)}')
            logging.info(f'Update rows: {len(update_rows)}')

            # Perform bulk insert and update
            if new_rows:
                session.bulk_insert_mappings(Films, new_rows)
            if update_rows:
                session.bulk_update_mappings(Films, update_rows)

            # Commit the changes and close the session
            session.commit()

    except Exception as error:
        logging.error(f'ERROR : {error}', exc_info=True)
        session.rollback()

    # Finally close the session
    finally:
        session.close()


#%%

def update_films_status(films: List[dict], Session) -> None:
    # TODO: this function should be refactored

    update_rows: list = []

    try:

        with Session() as session:

            for film in films:

                title = film.get('title')
                last_checked = film.get('last_checked')
                availability = film.get('availability')
                imax_3d_ov = film.get('imax_3d_ov')
                imax_ov = film.get('imax_ov')
                hd_ov = film.get('hd_ov')

                # Check if the row already exists
                row_exists = session.query(Films).filter(Films.title == title).first()

                if availability and not row_exists.last_update:
                    # Update the existing row with the availability
                    update_rows.append({
                        'id': row_exists.id,
                        'last_checked': last_checked,
                        'availability': availability,
                        'imax_3d_ov': imax_3d_ov,
                        'imax_ov': imax_ov,
                        'hd_ov': hd_ov,
                        'last_update': row_exists.availability,
                        'availability_date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })

                else:
                    # Update the existing row without the availability
                    update_rows.append({
                        'id': row_exists.id,
                        'last_checked': last_checked,
                        'availability': availability,
                        'imax_3d_ov': imax_3d_ov,
                        'imax_ov': imax_ov,
                        'hd_ov': hd_ov,
                        'last_update': row_exists.availability
                    })

            logging.info(f'Update rows: {len(update_rows)}')

            # Perform bulk update
            session.bulk_update_mappings(Films, update_rows)

            # Commit the changes
            session.commit()

    except Exception as error:
        logging.error(f'ERROR : {error}', exc_info=True)
        session.rollback()

    # Finally close the session
    finally:
        session.close()
