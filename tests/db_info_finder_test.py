import os
import sys
import pytest
import logging

from integeration_db.docker_container import Docker
from integeration_db.integration_db import IntegrationDb, EnvVar

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src/"))
from bot.bot_helpers.db_info_finder import FilmInfoFinder # noqa: E402

CONTAINER_NAME = "postgres:alpine3.18"

dckr = Docker()

@pytest.mark.skipif(not dckr.is_image_running(CONTAINER_NAME), reason=f"There is no container based on the {CONTAINER_NAME} is running.")
@pytest.mark.skipif(IntegrationDb.db_int_not_available(), reason=f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
def test_get_upcommings_films_list():

    schemas = ["tracker"]
    init_scripts = [os.path.abspath("src/init-db/init-db.sql"), os.path.abspath("src/init-db/sample-data.sql")]

    with IntegrationDb(schemas, init_scripts) as CONNECTION_STRING:

        # Prepare
        expected_films = ['Wish', 'SAW X', '', 'Napoleon', 'Raus aus dem Teich']

        # Execute
        film_info_finder = FilmInfoFinder(CONNECTION_STRING)
        upcoming_films_list = film_info_finder.get_upcommings_films_list()

        # Verify
        assert len(upcoming_films_list) > 0
        assert set(upcoming_films_list).issubset(set(expected_films))

@pytest.mark.skipif(not dckr.is_image_running(CONTAINER_NAME), reason=f"There is no container based on the {CONTAINER_NAME} is running.")
@pytest.mark.skipif(IntegrationDb.db_int_not_available(), reason=f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
def test_get_showing_films_list():

    schemas = ["tracker"]
    init_scripts = [os.path.abspath("src/init-db/init-db.sql"), os.path.abspath("src/init-db/sample-data.sql")]

    with IntegrationDb(schemas, init_scripts) as CONNECTION_STRING:

        # Prepare
        # Prepare
        expected_films = ['Wonka']

        # Execute
        film_info_finder = FilmInfoFinder(CONNECTION_STRING)
        showing_films_list = film_info_finder.get_showing_films_list()

        logging.info(showing_films_list)

        # Verify
        assert len(showing_films_list) > 0
        assert set(showing_films_list).issubset(set(expected_films))

        # TODO: test the date of performance
