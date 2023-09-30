import os
import sys
import pytest

from datetime import datetime, timedelta

from integeration_db.integration_db import IntegrationDb, EnvVar
from integeration_db.docker_container import Docker

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from miner.miner_helpers.db_updater import session_maker, update_films_list, update_films_status # noqa: E402
from miner.miner_helpers.db_model import Films # noqa: E402

CONTAINER_NAME = "postgres:16-bookworm"

dckr = Docker()

@pytest.mark.skipif(not dckr.is_image_running(CONTAINER_NAME), reason=f"There is no container based on the {CONTAINER_NAME} is running.")
@pytest.mark.skipif(IntegrationDb.db_int_not_available(), reason=f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
def test_update_films_list():

    schemas = ['kino']
    init_scripts = ["init-db/init-db.sql", "init-db/sample-data.sql"]

    with IntegrationDb(schemas, init_scripts) as CONNECTION_STRING:

        # Prepare

        exists = {
            'title': 'Oppenheimer',
            'link': 'https://www.filmpalast.net/film/oppenheimer.html',
            'img_link': 'https://www.filmpalast.net/img/film/oppenheimer.jpg'
        }

        dont_exist = {
            'title': 'The Creator',
            'link': 'https://www.filmpalast.net/film/the-creator.html',
            'img_link': 'https://www.filmpalast.net/fileadmin/_processed_/9/3/the_creator.jpg'
        }

        rows = [ exists, dont_exist ]

        # Execute

        Session_Maker = session_maker(CONNECTION_STRING)
        update_films_list(rows=rows, Session_Maker= Session_Maker)

        # Test

        with Session_Maker() as session:
            oppenheimer_film = session.query(Films).filter(Films.title == 'Oppenheimer').first()

            assert oppenheimer_film.title == 'Oppenheimer'
            assert oppenheimer_film.link == 'https://www.filmpalast.net/film/oppenheimer.html'
            assert oppenheimer_film.img_link == 'https://www.filmpalast.net/img/film/oppenheimer.jpg'

            creator_film = session.query(Films).filter(Films.title == 'The Creator').first()

            assert creator_film.title == 'The Creator'
            assert creator_film.link == 'https://www.filmpalast.net/film/the-creator.html'
            assert creator_film.img_link == 'https://www.filmpalast.net/fileadmin/_processed_/9/3/the_creator.jpg'


@pytest.mark.skipif(not dckr.is_image_running(CONTAINER_NAME), reason=f"There is no container based on the {CONTAINER_NAME} is running.")
@pytest.mark.skipif(IntegrationDb.db_int_not_available(), reason=f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
def test_update_films_status():

    schemas = ['kino']
    init_scripts = ["init-db/init-db.sql", "init-db/sample-data.sql"]

    with IntegrationDb(schemas, init_scripts) as CONNECTION_STRING:

        # Prepare

        with_availability = {
            'title': 'Oppenheimer',
            'link': 'https://www.filmpalast.net/film/oppenheimer.html',
            'img_link': 'https://www.filmpalast.net/img/film/oppenheimer.jpg',
            'availability': True,
            'imax_3d_ov': False,
            'imax_ov': True,
            'hd_ov': True,
            'last_checked': datetime.now(),
        }

        without_availability = {
            'title': 'The Flash',
            'link': 'https://www.filmpalast.net/film/the-flash.html',
            'img_link': 'https://www.filmpalast.net/fileadmin/_processed_/1/6/the_flash.jpg',
            'availability': True,
            'imax_3d_ov': False,
            'imax_ov': True,
            'hd_ov': True,
            'last_checked': datetime.now()
        }

        films = [ with_availability, without_availability ]

        # Execute
        start = datetime.now() - timedelta(seconds=1)               # adding buffer
        Session_Maker = session_maker(CONNECTION_STRING)
        update_films_status(films=films, Session= Session_Maker)
        end = datetime.now() + timedelta(seconds=1)                 # adding buffer

        # Test

        with Session_Maker() as session:
            oppenheimer_film = session.query(Films).filter(Films.title == 'Oppenheimer').first()

            assert oppenheimer_film.title == 'Oppenheimer'
            assert oppenheimer_film.link == 'https://www.filmpalast.net/film/oppenheimer.html'
            assert oppenheimer_film.img_link == 'https://www.filmpalast.net/img/film/oppenheimer.jpg'
            assert oppenheimer_film.availability
            assert oppenheimer_film.imax_3d_ov is False
            assert oppenheimer_film.imax_ov
            assert oppenheimer_film.hd_ov
            assert oppenheimer_film.last_update
            assert start <= oppenheimer_film.availability_date <= end
            assert start <= oppenheimer_film.last_checked <= end

            flash_film = session.query(Films).filter(Films.title == 'The Flash').first()

            assert flash_film.title == 'The Flash'
            assert flash_film.link == 'https://www.filmpalast.net/film/the-flash.html'
            assert flash_film.img_link == 'https://www.filmpalast.net/fileadmin/_processed_/1/6/the_flash.jpg'
            assert flash_film.availability
            assert flash_film.imax_3d_ov is False
            assert flash_film.imax_ov
            assert flash_film.hd_ov
            assert flash_film.last_update is False
            assert start <= flash_film.last_checked <= end
