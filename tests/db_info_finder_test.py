#%%
import os
import sys
import pytest
import logging

from integeration_db.docker_container import Docker
from integeration_db.integration_db import IntegrationDb, EnvVar

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src/"))
from bot.bot_helpers.db_info_finder import FilmInfoFinder # noqa: E402

#%%
CONTAINER_NAME = "postgres:alpine3.18"

dckr = Docker()

@pytest.fixture
def schemas():
    return ["tracker"]

@pytest.fixture
def init_scripts():
    return [os.path.abspath("src/init-db/init-db.sql"), os.path.abspath("src/init-db/sample-data.sql")]

#%%
@pytest.mark.skipif(not dckr.is_image_running(CONTAINER_NAME), reason=f"There is no container based on the {CONTAINER_NAME} is running.")
@pytest.mark.skipif(IntegrationDb.db_int_not_available(), reason=f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
def test_get_upcommings_films_list(schemas, init_scripts):

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
def test_get_showing_films_list(schemas, init_scripts):

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
def test_upsert_users(schemas, init_scripts):

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

@pytest.mark.skipif(not dckr.is_image_running(CONTAINER_NAME), reason=f"There is no container based on the {CONTAINER_NAME} is running.")
@pytest.mark.skipif(IntegrationDb.db_int_not_available(), reason=f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
def test_get_film_id_by_title(schemas, init_scripts):

    with IntegrationDb(schemas, init_scripts) as CONNECTION_STRING:

        # Execute
        film_info_finder = FilmInfoFinder(CONNECTION_STRING)
        wish_film_id = film_info_finder.get_film_id_by_title('Wish')
        marvels_film_id = film_info_finder.get_film_id_by_title('The Marvels')

        # Verify
        assert wish_film_id
        assert wish_film_id == '2EE63000012BHGWDVI'

        assert marvels_film_id
        assert marvels_film_id == 'DCC63000012BHGWDVI'

@pytest.mark.skipif(not dckr.is_image_running(CONTAINER_NAME), reason=f"There is no container based on the {CONTAINER_NAME} is running.")
@pytest.mark.skipif(IntegrationDb.db_int_not_available(), reason=f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
def test_check_performance_version_availability(schemas, init_scripts):

    with IntegrationDb(schemas, init_scripts) as CONNECTION_STRING:

        # Execute
        film_info_finder = FilmInfoFinder(CONNECTION_STRING)

        is_marvel_3d = film_info_finder.check_performance_version_availability('DCC63000012BHGWDVI', ['is_3d'])
        is_marvel_3d_ov = film_info_finder.check_performance_version_availability('DCC63000012BHGWDVI', ['is_3d', 'is_ov'])
        is_marvel_3d_ov_imax = film_info_finder.check_performance_version_availability('DCC63000012BHGWDVI', ['is_3d', 'is_ov', 'is_imax'])

        is_wonka_3d = film_info_finder.check_performance_version_availability('A6D63000012BHGWDVI', ['is_3d'])
        is_wonka_ov = film_info_finder.check_performance_version_availability('A6D63000012BHGWDVI', ['is_ov'])
        is_wonka_imax = film_info_finder.check_performance_version_availability('A6D63000012BHGWDVI', ['is_imax'])
        is_wonka_imax_ov = film_info_finder.check_performance_version_availability('A6D63000012BHGWDVI', ['is_imax', 'is_ov'])
        is_wonka_imax_3d = film_info_finder.check_performance_version_availability('A6D63000012BHGWDVI', ['is_imax', 'is_3d'])

        # Verify
        assert is_marvel_3d
        assert is_marvel_3d_ov
        assert is_marvel_3d_ov_imax

        assert is_wonka_ov
        assert is_wonka_imax
        assert is_wonka_3d is False
        assert is_wonka_imax_ov is False
        assert is_wonka_imax_3d is False

@pytest.mark.skipif(not dckr.is_image_running(CONTAINER_NAME), reason=f"There is no container based on the {CONTAINER_NAME} is running.")
@pytest.mark.skipif(IntegrationDb.db_int_not_available(), reason=f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
def test_get_performance_ids_by_version(schemas, init_scripts):

    with IntegrationDb(schemas, init_scripts) as CONNECTION_STRING:

        # Prepare
        marvels_expected = ['C9C45000023UHQLKCP', 'B5C45000023UHQLKCP']
        wonka_ov_expected = ['71D45000023UHQLKCP']
        wonka_imax_expected = ['61D45000023UHQLKCP']

        # Execute
        film_info_finder = FilmInfoFinder(CONNECTION_STRING)

        marvels_3d = film_info_finder.get_performance_ids_by_version('DCC63000012BHGWDVI', ['is_3d', 'is_ov'])
        marvels_3d_ov = film_info_finder.get_performance_ids_by_version('DCC63000012BHGWDVI',['is_3d', 'is_ov'])
        marvels_3d_ov_imax = film_info_finder.get_performance_ids_by_version('DCC63000012BHGWDVI',['is_3d', 'is_ov', 'is_imax'])

        wonka_3d = film_info_finder.get_performance_ids_by_version('A6D63000012BHGWDVI', ['is_3d'])
        wonka_ov = film_info_finder.get_performance_ids_by_version('A6D63000012BHGWDVI', ['is_ov'])
        wonka_imax = film_info_finder.get_performance_ids_by_version('A6D63000012BHGWDVI', ['is_imax'])
        wonka_3d_imax = film_info_finder.get_performance_ids_by_version('A6D63000012BHGWDVI', ['is_3d', 'is_imax'])
        wonka_imax_ov = film_info_finder.get_performance_ids_by_version('A6D63000012BHGWDVI', ['is_imax', 'is_ov'])

        # Verify
        assert len(marvels_3d) == 2
        assert len(marvels_3d_ov) == 2
        assert len(marvels_3d_ov_imax) == 2
        assert set(marvels_3d).issubset(set(marvels_expected))
        assert set(marvels_3d_ov).issubset(set(marvels_expected))
        assert set(marvels_3d_ov_imax).issubset(set(marvels_expected))

        assert len(wonka_3d) == 0
        assert len(wonka_ov) == 1
        assert len(wonka_imax) == 1
        assert len(wonka_3d_imax) == 0
        assert len(wonka_imax_ov) == 0
        assert set(wonka_ov).issubset(set(wonka_ov_expected))
        assert set(wonka_imax).issubset(set(wonka_imax_expected))
