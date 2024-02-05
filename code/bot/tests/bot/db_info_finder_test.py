#%%
import os
import pytest
import logging

from datetime import datetime, timedelta

from integeration_db.docker_container import Docker
from integeration_db.utils import str_2_date, str_2_time
from integeration_db.integration_db import IntegrationDb, EnvVar

from bot.utils.db_info_finder import FilmInfoFinder

#%%
CONTAINER_NAME = "postgres:alpine3.18"

dckr = Docker()

@pytest.fixture
def schemas():
    return ["tracker"]

@pytest.fixture
def init_scripts():
    return [os.path.abspath("./code/init-db/init-db.sql"),
            os.path.abspath("./code/init-db/sample-data.sql")]

@pytest.fixture
def date_ten_days_in_future_date():
    """ It returns a date 10 days in the future """
    return datetime.now().date() + timedelta(days=10)

#%%
@pytest.mark.skipif(not dckr.is_image_running(CONTAINER_NAME), reason=f"There is no container based on the {CONTAINER_NAME} is running.")
@pytest.mark.skipif(IntegrationDb.db_int_not_available(), reason=f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
def test_get_upcommings_films_list(schemas, init_scripts):

    with IntegrationDb(schemas, init_scripts) as CONNECTION_STRING:

        # Prepare
        expected_films=[{'title': 'Napoleon', 'upcoming_film_id': 1},
                        {'title': 'SAW X', 'upcoming_film_id': 2},
                        {'title': 'Wish', 'upcoming_film_id': 3},
                        {'title': 'Raus aus dem Teich', 'upcoming_film_id': 4}]

        # Execute
        film_info_finder = FilmInfoFinder(CONNECTION_STRING) # type: ignore
        upcoming_films_list = film_info_finder.get_upcomings_films_list()

        # Verify
        assert len(upcoming_films_list) > 0 # type: ignore
        assert upcoming_films_list == expected_films

@pytest.mark.skipif(not dckr.is_image_running(CONTAINER_NAME), reason=f"There is no container based on the {CONTAINER_NAME} is running.")
@pytest.mark.skipif(IntegrationDb.db_int_not_available(), reason=f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
def test_get_showing_films_list(schemas, init_scripts):

    with IntegrationDb(schemas, init_scripts) as CONNECTION_STRING:

        # Prepare
        expected_films = ['Wonka']

        # Execute
        film_info_finder = FilmInfoFinder(CONNECTION_STRING) # type: ignore
        showing_films_list = film_info_finder.get_showing_films_list()

        logging.info(showing_films_list)

        # Verify
        assert len(showing_films_list) > 0 # type: ignore
        assert set(showing_films_list).issubset(set(expected_films)) # type: ignore

@pytest.mark.skipif(not dckr.is_image_running(CONTAINER_NAME), reason=f"There is no container based on the {CONTAINER_NAME} is running.")
@pytest.mark.skipif(IntegrationDb.db_int_not_available(), reason=f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
def test_upsert_users(schemas, init_scripts):

    with IntegrationDb(schemas, init_scripts) as CONNECTION_STRING:

        # Prepare

        upsert = {
            'chat_id': '222211111',
            'message_id': '1111',
            'title': 'Wish',
            'flags': '1,ov|0,imax|2,3d'
            }

        insert = {
            'chat_id': '444411111',
            'message_id': '2222',
            'title': 'Wonka',
            'flags': '1,ov|1,imax|2,3d'
        }

        # Execute
        film_info_finder = FilmInfoFinder(CONNECTION_STRING) # type: ignore
        upsert_result = film_info_finder.upsert_users(**upsert)
        insert_result = film_info_finder.upsert_users(**insert)

        # Verify
        assert upsert_result
        assert insert_result

        uspert_user = film_info_finder._get_user_by_user_id(1)
        insert_user = film_info_finder._get_user_by_user_id(5)

        assert insert_user
        assert insert_user.chat_id == insert.get('chat_id') # type: ignore
        assert insert_user.title == insert.get('title') # type: ignore
        assert insert_user.message_id == insert.get('message_id') # type: ignore
        assert insert_user.flags == insert.get('flags') # type: ignore

        assert uspert_user
        assert uspert_user.chat_id == upsert.get('chat_id') # type: ignore
        assert uspert_user.title == upsert.get('title') # type: ignore
        assert uspert_user.message_id == upsert.get('message_id') # type: ignore
        assert uspert_user.flags == upsert.get('flags') # type: ignore

@pytest.mark.skipif(not dckr.is_image_running(CONTAINER_NAME), reason=f"There is no container based on the {CONTAINER_NAME} is running.")
@pytest.mark.skipif(IntegrationDb.db_int_not_available(), reason=f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
def test_get_film_id_by_title(schemas, init_scripts):

    with IntegrationDb(schemas, init_scripts) as CONNECTION_STRING:

        # Execute
        film_info_finder = FilmInfoFinder(CONNECTION_STRING) # type: ignore
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
        film_info_finder = FilmInfoFinder(CONNECTION_STRING) # type: ignore

        # Check if is_3d and is_imax set to 0 that means indifferent to imax
        is_marvel_3d = film_info_finder.check_performance_version_availability('DCC63000012BHGWDVI', {'is_3d': True, 'is_imax':0})
        # Check if is_ov and is_3d , and also is_imax set to 0 that means indifferent to imax
        is_marvel_3d_ov = film_info_finder.check_performance_version_availability('DCC63000012BHGWDVI', {'is_3d': True, 'is_ov': True, 'is_imax':0})
        is_marvel_3d_ov_imax = film_info_finder.check_performance_version_availability('DCC63000012BHGWDVI', {'is_3d':True, 'is_ov':True, 'is_imax':True})

        # Check if is_ov and is_imax set to 0 that means indifferent to imax
        is_wonka_ov = film_info_finder.check_performance_version_availability('A6D63000012BHGWDVI', {'is_ov': True, 'is_imax':0})
        # Check if is_3d and is_imax set to 0 that means indifferent to imax
        is_wonka_3d = film_info_finder.check_performance_version_availability('A6D63000012BHGWDVI', {'is_3d': True, 'is_imax':0})
        is_wonka_imax = film_info_finder.check_performance_version_availability('A6D63000012BHGWDVI', {'is_imax': True})
        is_wonka_imax_ov = film_info_finder.check_performance_version_availability('A6D63000012BHGWDVI', {'is_imax':True, 'is_ov':True})
        is_wonka_imax_3d = film_info_finder.check_performance_version_availability('A6D63000012BHGWDVI', {'is_imax':True, 'is_3d':True})

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
        film_info_finder = FilmInfoFinder(CONNECTION_STRING) # type: ignore

        # Checks if is_3d and is_imax set to 0 that means indifferent to imax
        marvels_3d = film_info_finder.get_performance_ids_by_version('DCC63000012BHGWDVI', {'is_3d': True, 'is_imax': 0})
        # Checks if is_ov and is_3d , and also is_imax set to 0 that means indifferent to imax
        marvels_3d_ov = film_info_finder.get_performance_ids_by_version('DCC63000012BHGWDVI',{'is_3d': True, 'is_ov': True, 'is_imax': 0})
        marvels_3d_ov_imax = film_info_finder.get_performance_ids_by_version('DCC63000012BHGWDVI',{'is_3d': True, 'is_ov': True, 'is_imax': True})

        # Checks if is_ov and is_imax set to 0 that means indifferent to imax
        wonka_3d = film_info_finder.get_performance_ids_by_version('A6D63000012BHGWDVI', {'is_3d': True, 'is_imax': 0})
        # Checks if is_3d ,and also is_imax set and is_3d to 0 that means indifferent to imax
        wonka_ov = film_info_finder.get_performance_ids_by_version('A6D63000012BHGWDVI', {'is_ov': True, 'is_imax': 0, 'is_3d': 0})
        wonka_imax = film_info_finder.get_performance_ids_by_version('A6D63000012BHGWDVI', {'is_imax': True})
        wonka_3d_imax = film_info_finder.get_performance_ids_by_version('A6D63000012BHGWDVI', {'is_3d': True, 'is_imax': True})
        wonka_imax_ov = film_info_finder.get_performance_ids_by_version('A6D63000012BHGWDVI', {'is_imax': True, 'is_ov': True})

        # Verify
        assert len(marvels_3d) == 2 # type: ignore
        assert len(marvels_3d_ov) == 2 # type: ignore
        assert len(marvels_3d_ov_imax) == 2 # type: ignore
        assert set(marvels_3d).issubset(set(marvels_expected)) # type: ignore
        assert set(marvels_3d_ov).issubset(set(marvels_expected)) # type: ignore
        assert set(marvels_3d_ov_imax).issubset(set(marvels_expected)) # type: ignore

        assert len(wonka_3d) == 0 # type: ignore
        assert len(wonka_ov) == 1 # type: ignore
        assert len(wonka_imax) == 1 # type: ignore
        assert len(wonka_3d_imax) == 0 # type: ignore
        assert len(wonka_imax_ov) == 0 # type: ignore
        assert set(wonka_ov).issubset(set(wonka_ov_expected)) # type: ignore
        assert set(wonka_imax).issubset(set(wonka_imax_expected)) # type: ignore

@pytest.mark.skipif(not dckr.is_image_running(CONTAINER_NAME), reason=f"There is no container based on the {CONTAINER_NAME} is running.")
@pytest.mark.skipif(IntegrationDb.db_int_not_available(), reason=f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
def test_get_performance_dates_by_film_id(schemas, init_scripts, date_ten_days_in_future_date):

    with IntegrationDb(schemas, init_scripts) as CONNECTION_STRING:

        # Prepare
        version_1 = {'is_imax': True}
        version_2 = {'is_ov': True}
        version_3 = {'is_imax': True, 'is_ov': True}

        marvels_expected_dates = [ str_2_date('2023-11-13'), str_2_date('2023-11-14')]

        # Execute
        film_info_finder = FilmInfoFinder(CONNECTION_STRING) # type: ignore

        performance_dates_1 = film_info_finder.get_performance_dates_by_film_id('A6D63000012BHGWDVI', version_1)
        performance_dates_2 = film_info_finder.get_performance_dates_by_film_id('A6D63000012BHGWDVI', version_2)
        performance_dates_3 = film_info_finder.get_performance_dates_by_film_id('A6D63000012BHGWDVI', version_3)

        performance_dates_4 = film_info_finder.get_performance_dates_by_film_id('DCC63000012BHGWDVI', version_1)
        performance_dates_5 = film_info_finder.get_performance_dates_by_film_id('DCC63000012BHGWDVI', version_2)
        performance_dates_6 = film_info_finder.get_performance_dates_by_film_id('DCC63000012BHGWDVI', version_3)

        # Verify
        assert len(performance_dates_1) == 1 # type: ignore
        assert len(performance_dates_2) == 1 # type: ignore
        assert len(performance_dates_3) == 0 # type: ignore
        assert len(performance_dates_4) == 2 # type: ignore
        assert len(performance_dates_5) == 2 # type: ignore
        assert len(performance_dates_6) == 2 # type: ignore

        assert performance_dates_1[0] == date_ten_days_in_future_date # type: ignore
        assert performance_dates_2[0] == date_ten_days_in_future_date # type: ignore
        assert performance_dates_3 == []

        assert set(performance_dates_4).issubset(set(marvels_expected_dates)) # type: ignore
        assert set(performance_dates_5).issubset(set(marvels_expected_dates)) # type: ignore
        assert set(performance_dates_6).issubset(set(marvels_expected_dates)) # type: ignore

@pytest.mark.skipif(not dckr.is_image_running(CONTAINER_NAME), reason=f"There is no container based on the {CONTAINER_NAME} is running.")
@pytest.mark.skipif(IntegrationDb.db_int_not_available(), reason=f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
def test_get_performance_hours_by_film_id(schemas, init_scripts, date_ten_days_in_future_date):

    with IntegrationDb(schemas, init_scripts) as CONNECTION_STRING:

        # Prepare
        version_1 = {'is_imax': True}
        version_2 = {'is_ov': True}
        version_3 = {'is_imax': True, 'is_ov': True}

        # Execute
        film_info_finder = FilmInfoFinder(CONNECTION_STRING) # type: ignore

        performance_hours_1 = film_info_finder.get_performance_hours_by_film_id('A6D63000012BHGWDVI', version_1, date_ten_days_in_future_date)
        performance_hours_2 = film_info_finder.get_performance_hours_by_film_id('A6D63000012BHGWDVI', version_2, date_ten_days_in_future_date)
        performance_hours_3 = film_info_finder.get_performance_hours_by_film_id('A6D63000012BHGWDVI', version_3, date_ten_days_in_future_date)

        # Verify
        assert len(performance_hours_1) == 1 # type: ignore
        assert len(performance_hours_2) == 1 # type: ignore
        assert len(performance_hours_3) == 0 # type: ignore

        assert performance_hours_1[0] == str_2_time('20:00:00') # type: ignore
        assert performance_hours_2[0] == str_2_time('17:15:00') # type: ignore
        assert performance_hours_3 == []
