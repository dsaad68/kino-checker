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

        # CHECK: test the date of performance

@pytest.mark.skipif(not dckr.is_image_running(CONTAINER_NAME), reason=f"There is no container based on the {CONTAINER_NAME} is running.")
@pytest.mark.skipif(IntegrationDb.db_int_not_available(), reason=f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
def test_upsert_users():

    schemas = ["tracker"]
    init_scripts = [os.path.abspath("src/init-db/init-db.sql"), os.path.abspath("src/init-db/sample-data.sql")]

    with IntegrationDb(schemas, init_scripts) as CONNECTION_STRING:

        # Prepare

        upsert = {
            'chat_id': '222211111',
            'message_id': '1111',
            'title': 'Wish'
            }

        insert = {
            'chat_id': '333311111',
            'message_id': '2222',
            'title': 'Wonka'
        }

        # Execute
        film_info_finder = FilmInfoFinder(CONNECTION_STRING)
        upsert_result = film_info_finder.upsert_users(**upsert)
        insert_result = film_info_finder.upsert_users(**insert)

        # Verify
        assert upsert_result
        assert insert_result

        uspert_user = film_info_finder._get_user_by_user_id(1)
        insert_user = film_info_finder._get_user_by_user_id(4)

        assert insert_user
        assert insert_user.chat_id == insert.get('chat_id')
        assert insert_user.title == insert.get('title')
        assert insert_user.message_id == insert.get('message_id')

        assert uspert_user
        assert uspert_user.chat_id == upsert.get('chat_id')
        assert uspert_user.title == upsert.get('title')
        assert uspert_user.message_id == upsert.get('message_id')
