#%%
import pytest

from datetime import datetime, timedelta, date, time

from integeration_db.docker_container import Docker
from integeration_db.integration_db import IntegrationDb, EnvVar
from integeration_db.utils import str_2_datetime, str_2_date, str_2_time

from common.db.db_model import PerformanceInfo
from miner.utils.film_db_manager import FilmDatabaseManager

#%%

CONTAINER_NAME = "postgres:alpine3.18"

dckr = Docker()

#%%

@pytest.mark.skipif(not dckr.is_image_running(CONTAINER_NAME), reason=f"There is no container based on the {CONTAINER_NAME} is running.")
@pytest.mark.skipif(IntegrationDb.db_int_not_available(), reason=f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
def test_update_films_table(schemas, init_scripts):

    with IntegrationDb(schemas, init_scripts) as CONNECTION_STRING:

        # Prepare
        exists = {
            "film_id": "2EE63000012BHGWDVI",
            "title": "Wish",
            "name": "Wish",
            "production_year": 2022,
            "length_in_minutes": 95,
            "nationwide_start": "2023-11-30",
            "image_url": "https://contentservice.cineorder.shop/contents/img?q=fDJ8M3w3fDEwMjI3OTZfL3JDQ3JHNHN3a3hnRlpmbHVwNTZzeDZ5bWs1aS5qcGdffA",
            "last_updated": datetime.now()
        }

        upsert_case = {
            "film_id": "A6D63000012BHGWDVI",
            "title": "Wonka",
            "name": "Wonka",
            "production_year": 2023,
            "length_in_minutes": 160,
            "nationwide_start": "2023-12-10",
            "image_url": "https://contentservice.cineorder.shop/contents/img?q=fDJ8M3w3fDc4NzY5OV8vZXQxT2ZSdmZ3V21Ua1lpandxYUR3S0ZnWTFsLmpwZ19kZXw",
            "last_updated": datetime.now()
        }

        dont_exist ={
                "film_id": "38E63000012BHGWDVI",
                "title": "Oppenheimer",
                "name": "Oppenheimer",
                "production_year": 2022,
                "length_in_minutes": 180,
                "nationwide_start": "2023-07-20",
                "image_url": "https://contentservice.cineorder.shop/contents/img?q=683jXD30IV9SmgAABHGWNjb",
                "last_updated": datetime.now()
            }

        # Execute
        start = datetime.now() - timedelta(seconds=1)  # adding buffer

        film_db_manager = FilmDatabaseManager(CONNECTION_STRING) # type: ignore
        film_db_manager.update_films_table(films_list=[exists, dont_exist, upsert_case])

        end = datetime.now() + timedelta(seconds=1)  # adding buffer

        # Verify

        # don't exist
        oppenheimer_film = film_db_manager._get_film_by_title("Oppenheimer")

        assert oppenheimer_film is not None
        assert oppenheimer_film.film_id == "38E63000012BHGWDVI" # type: ignore
        assert oppenheimer_film.title == "Oppenheimer" # type: ignore
        assert oppenheimer_film.name == "Oppenheimer"  # type: ignore
        assert oppenheimer_film.production_year == 2022 # type: ignore
        assert oppenheimer_film.length_in_minutes == 180 # type: ignore
        assert oppenheimer_film.nationwide_start == "2023-07-20" # type: ignore
        assert oppenheimer_film.image_url == "https://contentservice.cineorder.shop/contents/img?q=683jXD30IV9SmgAABHGWNjb" # type: ignore
        assert start <= oppenheimer_film.last_updated <= end # type: ignore

        # exist and don't change
        wish_film = film_db_manager._get_film_by_film_id("2EE63000012BHGWDVI")

        assert wish_film is not None
        assert wish_film.film_id == "2EE63000012BHGWDVI" # type: ignore
        assert wish_film.title == "Wish" # type: ignore
        assert wish_film.name == "Wish"  # type: ignore
        assert wish_film.production_year == 2022 # type: ignore
        assert wish_film.length_in_minutes == 95 # type: ignore
        assert wish_film.nationwide_start == "2023-11-30" # type: ignore
        assert wish_film.image_url == "https://contentservice.cineorder.shop/contents/img?q=fDJ8M3w3fDEwMjI3OTZfL3JDQ3JHNHN3a3hnRlpmbHVwNTZzeDZ5bWs1aS5qcGdffA" # type: ignore # noqa: E501
        assert start <= wish_film.last_updated <= end # type: ignore

        # exist and updates
        wonka_film = film_db_manager._get_film_by_film_id("A6D63000012BHGWDVI")

        assert wonka_film is not None
        assert wonka_film.film_id == "A6D63000012BHGWDVI" # type: ignore
        assert wonka_film.title == "Wonka" # type: ignore
        assert wonka_film.name == "Wonka"  # type: ignore
        assert wonka_film.production_year == 2023 # type: ignore
        assert wonka_film.length_in_minutes == 160 # type: ignore
        assert wonka_film.nationwide_start == "2023-12-10" # type: ignore
        assert wonka_film.image_url == "https://contentservice.cineorder.shop/contents/img?q=fDJ8M3w3fDc4NzY5OV8vZXQxT2ZSdmZ3V21Ua1lpandxYUR3S0ZnWTFsLmpwZ19kZXw" # type: ignore # noqa: E501
        assert start <= wonka_film.last_updated <= end # type: ignore

@pytest.mark.skipif(not dckr.is_image_running(CONTAINER_NAME), reason=f"There is no container based on the {CONTAINER_NAME} is running.")
@pytest.mark.skipif(IntegrationDb.db_int_not_available(), reason=f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
def test_update_performances_table(schemas, init_scripts):

    with IntegrationDb(schemas, init_scripts) as CONNECTION_STRING:

        # Prepare
        exists = {
            "performance_id": "71D45000023UHQLKCP",
            "film_id": "A6D63000012BHGWDVI",
            "film_id_p": "A6D63000012BHGWDVI",
            "performance_datetime": "2023-12-06 17:15:00",
            "performance_date": "2023-12-06",
            "performance_time": "17:15:00",
            "release_type": "englisch/OV",
            "is_imax": False,
            "is_ov": True,
            "is_3d": False,
            "auditorium_id": "10000000015UHQLKCP",
            "auditorium_name": "Kino 1",
            "last_updated": datetime.now()
            }

        upsert_case = {
                "performance_id": "B5C45000023UHQLKCP",
                "film_id": "DCC63000012BHGWDVI",
                "film_id_p": "DCC63000012BHGWDVI",
                "performance_datetime": "2023-11-14 17:00:00",
                "performance_date": "2023-11-14",
                "performance_time": "17:00:00",
                "release_type": "Digital",
                "is_imax": False,
                "is_ov": False,
                "is_3d": False,
                "auditorium_id": "30000000015UHQLKCP",
                "auditorium_name": "Kino 4",
                "last_updated": datetime.now()
                }


        dont_exist = {
            "performance_id": "9EC45000023UHQLKCP",
            "film_id": "DCC63000012BHGWDVI",
            "film_id_p": "DCC63000012BHGWDVI",
            "performance_datetime": "2023-11-22 16:45:00",
            "performance_date": "2023-11-22",
            "performance_time": "16:45:00",
            "release_type": "IMAX/Digital",
            "is_imax": True,
            "is_ov": False,
            "is_3d": False,
            "auditorium_id": "30000000015UHQLKCP",
            "auditorium_name": "Kino 3",
            "last_updated": datetime.now()
            }

        # Execute
        start = datetime.now() - timedelta(seconds=1)  # adding buffer

        film_db_manager = FilmDatabaseManager(CONNECTION_STRING) # type: ignore
        film_db_manager.update_performances_table(performances_list=[exists, dont_exist, upsert_case])

        end = datetime.now() + timedelta(seconds=1)  # adding buffer

        # Verify
        existing_performance = film_db_manager._get_performance_by_performance_id("71D45000023UHQLKCP")

        assert existing_performance is not None
        assert existing_performance.performance_id == "71D45000023UHQLKCP" # type: ignore
        assert existing_performance.film_id == "A6D63000012BHGWDVI" # type: ignore
        assert existing_performance.film_id_p == "A6D63000012BHGWDVI" # type: ignore
        assert existing_performance.performance_datetime == str_2_datetime("2023-12-06 17:15:00") # type: ignore
        assert existing_performance.performance_date == str_2_date("2023-12-06") # type: ignore
        assert existing_performance.performance_time == str_2_time("17:15:00") # type: ignore
        assert existing_performance.release_type == "englisch/OV" # type: ignore
        assert existing_performance.is_imax is False # type: ignore
        assert existing_performance.is_ov  # type: ignore
        assert existing_performance.is_3d is False # type: ignore
        assert existing_performance.auditorium_id == "10000000015UHQLKCP" # type: ignore
        assert existing_performance.auditorium_name == "Kino 1" # type: ignore
        assert start <= existing_performance.last_updated <= end # type: ignore

        new_performance = film_db_manager._get_performance_by_performance_id("9EC45000023UHQLKCP")

        assert new_performance is not None
        assert new_performance.performance_id == "9EC45000023UHQLKCP" # type: ignore
        assert new_performance.film_id == "DCC63000012BHGWDVI" # type: ignore
        assert new_performance.film_id_p == "DCC63000012BHGWDVI" # type: ignore
        assert new_performance.performance_datetime == str_2_datetime("2023-11-22 16:45:00") # type: ignore
        assert new_performance.performance_date == str_2_date("2023-11-22") # type: ignore
        assert new_performance.performance_time == str_2_time("16:45:00") # type: ignore
        assert new_performance.release_type == "IMAX/Digital" # type: ignore
        assert new_performance.is_imax # type: ignore
        assert new_performance.is_ov  is False# type: ignore
        assert new_performance.is_3d is False # type: ignore
        assert new_performance.auditorium_id == "30000000015UHQLKCP" # type: ignore
        assert new_performance.auditorium_name == "Kino 3" # type: ignore
        assert start <= new_performance.last_updated <= end # type: ignore

        upsert_case_test = film_db_manager._get_performance_by_performance_id("B5C45000023UHQLKCP")

        assert upsert_case_test is not None
        assert upsert_case_test.performance_id == "B5C45000023UHQLKCP" # type: ignore
        assert upsert_case_test.film_id == "DCC63000012BHGWDVI" # type: ignore
        assert upsert_case_test.film_id_p == "DCC63000012BHGWDVI" # type: ignore
        assert upsert_case_test.performance_datetime == str_2_datetime("2023-11-14 17:00:00") # type: ignore
        assert upsert_case_test.performance_date == str_2_date("2023-11-14") # type: ignore
        assert upsert_case_test.performance_time == str_2_time("17:00:00") # type: ignore
        assert upsert_case_test.release_type == "Digital" # type: ignore
        assert upsert_case_test.is_imax is False# type: ignore
        assert upsert_case_test.is_ov is False# type: ignore
        assert upsert_case_test.is_3d is False # type: ignore
        assert upsert_case_test.auditorium_id == "30000000015UHQLKCP" # type: ignore
        assert upsert_case_test.auditorium_name == "Kino 4" # type: ignore
        assert start <= upsert_case_test.last_updated <= end # type: ignore


@pytest.mark.skipif(not dckr.is_image_running(CONTAINER_NAME), reason=f"There is no container based on the {CONTAINER_NAME} is running.")
@pytest.mark.skipif(IntegrationDb.db_int_not_available(), reason=f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
def test_update_upcoming_table(schemas, init_scripts):

    with IntegrationDb(schemas, init_scripts) as CONNECTION_STRING:

        # Prepare
        exists = {
            "title": "Napoleon",
            "release_date": "2023-11-23",
            "last_updated": datetime.now(),
            }

        upsert_case = {
            "title": "Wish",
            "release_date": "2023-11-23",
            "last_updated": datetime.now(),
        }

        dont_exist = {
            "title": "WONKA",
            "release_date": "2023-12-07",
            "last_updated": datetime.now(),
            }

        # Execute
        start = datetime.now() - timedelta(seconds=1)  # adding buffer

        film_db_manager = FilmDatabaseManager(CONNECTION_STRING) # type: ignore
        film_db_manager.update_upcoming_films_table(upcoming_films_list=[exists, upsert_case, dont_exist])

        end = datetime.now() + timedelta(seconds=1)  # adding buffer

        # Verify

        # exists and don't change
        film_napoleon = film_db_manager._get_upcoming_film_by_title(exists.get("title").lower()) # type: ignore

        assert film_napoleon is not None
        assert film_napoleon.upcoming_film_id == 1 # type: ignore
        assert film_napoleon.title.lower() == exists.get("title").lower() # type: ignore
        assert film_napoleon.release_date == str_2_date(exists.get("release_date").lower()) # type: ignore
        assert film_napoleon.film_id is None # type: ignore
        assert film_napoleon.is_released is False # type: ignore
        assert film_napoleon.is_trackable is True # type: ignore
        assert start <= film_napoleon.last_updated <= end # type: ignore

        # exists and updates
        film_wish = film_db_manager._get_upcoming_film_by_title("Wish")

        assert film_wish is not None
        assert film_wish.upcoming_film_id == 3 # type: ignore
        assert film_wish.title.lower() == "Wish".lower() # type: ignore
        assert film_wish.release_date == str_2_date("2023-11-23") # type: ignore
        assert film_wish.film_id is None # type: ignore
        assert film_wish.is_released is False # type: ignore
        assert film_wish.is_trackable is True # type: ignore
        assert start <= film_wish.last_updated <= end # type: ignore

        # don't exist
        film_wonka = film_db_manager._get_upcoming_film_by_title(dont_exist.get("title").lower()) # type: ignore

        assert film_wonka is not None
        assert film_wonka.title.lower() == dont_exist.get("title").lower() # type: ignore
        assert film_wonka.release_date == str_2_date(dont_exist.get("release_date").lower()) # type: ignore
        assert film_wonka.film_id is None # type: ignore
        assert film_wonka.is_released is False # type: ignore
        assert film_wonka.is_trackable is True # type: ignore
        assert start <= film_wonka.last_updated <= end # type: ignore

@pytest.mark.skipif(not dckr.is_image_running(CONTAINER_NAME), reason=f"There is no container based on the {CONTAINER_NAME} is running.")
@pytest.mark.skipif(IntegrationDb.db_int_not_available(), reason=f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
def test_update_upcoming_table_cardinality_violation(schemas, init_scripts):
    """This test is written for a situation when CardinalityViolation is raised."""

    with IntegrationDb(schemas, init_scripts) as CONNECTION_STRING:

        # Prepare
        exists = {
            "title": "Napoleon",
            "release_date": "2023-11-23",
            "last_updated": datetime.now(),
            }

        upsert_case = {
            "title": "Wish",
            "release_date": "2023-11-23",
            "last_updated": datetime.now(),
        }

        upsert_case_duplicate = {
            "title": "Wish",
            "release_date": "2023-11-25",
            "last_updated": datetime.now(),
        }

        dont_exist = {
            "title": "WONKA",
            "release_date": "2023-12-07",
            "last_updated": datetime.now(),
            }

        # Execute
        start = datetime.now() - timedelta(seconds=1)  # adding buffer

        film_db_manager = FilmDatabaseManager(CONNECTION_STRING) # type: ignore
        film_db_manager.update_upcoming_films_table(upcoming_films_list=[exists, upsert_case, upsert_case_duplicate, dont_exist])

        end = datetime.now() + timedelta(seconds=1)  # adding buffer

        # Verify

        # exists and don't change
        film_napoleon = film_db_manager._get_upcoming_film_by_title(exists.get("title").lower()) # type: ignore

        assert film_napoleon is not None
        assert film_napoleon.upcoming_film_id == 1 # type: ignore
        assert film_napoleon.title.lower() == exists.get("title").lower() # type: ignore
        assert film_napoleon.release_date == str_2_date(exists.get("release_date").lower()) # type: ignore
        assert film_napoleon.film_id is None # type: ignore
        assert film_napoleon.is_released is False # type: ignore
        assert film_napoleon.is_trackable is True # type: ignore
        assert start <= film_napoleon.last_updated <= end # type: ignore

        # exists and updates
        film_wish = film_db_manager._get_upcoming_film_by_title("Wish")

        assert film_wish is not None
        assert film_wish.upcoming_film_id == 3 # type: ignore
        assert film_wish.title.lower() == "Wish".lower() # type: ignore
        assert film_wish.release_date == str_2_date("2023-11-25") # type: ignore
        assert film_wish.film_id is None # type: ignore
        assert film_wish.is_released is False # type: ignore
        assert film_wish.is_trackable is True # type: ignore
        assert start <= film_wish.last_updated <= end # type: ignore

        # don't exist
        film_wonka = film_db_manager._get_upcoming_film_by_title(dont_exist.get("title").lower()) # type: ignore

        assert film_wonka is not None
        assert film_wonka.title.lower() == dont_exist.get("title").lower() # type: ignore
        assert film_wonka.release_date == str_2_date(dont_exist.get("release_date").lower()) # type: ignore
        assert film_wonka.film_id is None # type: ignore
        assert film_wonka.is_released is False # type: ignore
        assert film_wonka.is_trackable is True # type: ignore
        assert start <= film_wonka.last_updated <= end # type: ignore

@pytest.mark.skipif(not dckr.is_image_running(CONTAINER_NAME), reason=f"There is no container based on the {CONTAINER_NAME} is running.")
@pytest.mark.skipif(IntegrationDb.db_int_not_available(), reason=f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
def test_update_released_films_in_upcoming_films_table(schemas, init_scripts):

    with IntegrationDb(schemas, init_scripts) as CONNECTION_STRING:

        # Execute
        film_db_manager = FilmDatabaseManager(CONNECTION_STRING) # type: ignore
        film_db_manager.update_released_films_in_upcoming_films_table()

        # Verify

        film_sawx_u = film_db_manager._get_upcoming_film_by_title("SAW X")
        film_sawx_f = film_db_manager._get_film_by_title("SAW X")

        assert film_sawx_u.is_released # type: ignore
        assert film_sawx_u.film_id == film_sawx_f.film_id # type: ignore

        film_wish_u = film_db_manager._get_upcoming_film_by_title("Wish")
        film_wish_f = film_db_manager._get_film_by_title("Wish")

        assert film_wish_u.is_released # type: ignore
        assert film_wish_u.film_id == film_wish_f.film_id # type: ignore

@pytest.mark.skipif(not dckr.is_image_running(CONTAINER_NAME), reason=f"There is no container based on the {CONTAINER_NAME} is running.")
@pytest.mark.skipif(IntegrationDb.db_int_not_available(), reason=f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
def test_update_users_table(schemas, init_scripts):

    with IntegrationDb(schemas, init_scripts) as CONNECTION_STRING:

        # Execute
        film_db_manager = FilmDatabaseManager(CONNECTION_STRING) # type: ignore
        film_db_manager.update_released_films_in_upcoming_films_table()
        film_db_manager.update_users_table()

        # Verify

        user_wish = film_db_manager._get_upcoming_user_by_title("Wish")
        film_wish = film_db_manager._get_film_by_title("Wish")

        assert user_wish.film_id == film_wish.film_id # type: ignore

@pytest.mark.skipif(not dckr.is_image_running(CONTAINER_NAME), reason=f"There is no container based on the {CONTAINER_NAME} is running.")
@pytest.mark.skipif(IntegrationDb.db_int_not_available(), reason=f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
def test_get_performance_based_on_versions(schemas, init_scripts):

    perfomance_1 = PerformanceInfo(film_id='58E63000012BHGWDVI', performance_id='88D45000023UHQLKCP', date=date(2023, 11, 15), time=time(20, 0, 0), is_imax=True, is_ov=True, is_3d=True)
    perfomance_2 = PerformanceInfo(film_id='58E63000012BHGWDVI', performance_id='99D45000023UHQLKCP', date=date(2023, 11, 16), time=time(17, 0, 0), is_imax=True, is_ov=True, is_3d=False)

    with IntegrationDb(schemas, init_scripts) as CONNECTION_STRING:

        versions = {"is_ov": True, "is_imax": True}

        # Execute
        film_db_manager = FilmDatabaseManager(CONNECTION_STRING) # type: ignore
        performances = film_db_manager._get_performance_info_by_film_id("58E63000012BHGWDVI", versions)

        # Verify
        assert len(performances) > 0 # type: ignore

        # sourcery skip: no-loop-in-tests
        # sourcery skip: no-conditionals-in-tests
        for performance in performances:
            if performance.performance_id == perfomance_1.performance_id:
                assert performance == perfomance_1
            elif performance.performance_id == perfomance_2.performance_id:
                assert performance == perfomance_2


@pytest.mark.skipif(not dckr.is_image_running(CONTAINER_NAME), reason=f"There is no container based on the {CONTAINER_NAME} is running.")
@pytest.mark.skipif(IntegrationDb.db_int_not_available(), reason=f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
def test_get_users_to_notify(schemas,init_scripts):

    perfomance_1 = PerformanceInfo(film_id='58E63000012BHGWDVI', performance_id='88D45000023UHQLAAA', date=date(2023, 11, 15), time=time(20, 0, 0), is_imax=True, is_ov=True, is_3d=True)
    perfomance_2 = PerformanceInfo(film_id='58E63000012BHGWDVI', performance_id='99D45000023UHQLAAA', date=date(2023, 11, 16), time=time(17, 0, 0), is_imax=True, is_ov=True, is_3d=False)

    with IntegrationDb(schemas, init_scripts) as CONNECTION_STRING:

        # Execute
        film_db_manager = FilmDatabaseManager(CONNECTION_STRING) # type: ignore
        user_list = film_db_manager.get_users_to_notify()

        # Verify
        assert len(user_list) > 0 # type: ignore

        user_dict = {item.user_id: item for item in user_list}
        user = user_dict.get(5)

        assert user.user_id == 5
        assert user.chat_id == "444411111"
        assert user.message_id == "1050"
        assert user.title == "Creator"
        assert user.notified is False
        assert user.film_id is not None
        assert user.film_id == "58E63000012BHGWDVI"
        assert user.flags == "1,ov|1,imax|2,3d"
        assert user.name == "Creator"
        assert user.last_updated.strftime('%Y-%m-%d %H:%M:%S') == '2023-11-13 19:14:38'

        performance_dict = {item.performance_id: item for item in user.performances}
        actual_performance_1 = performance_dict.get("88D45000023UHQLAAA")
        actual_performance_2 = performance_dict.get("99D45000023UHQLAAA")

        assert actual_performance_1 == perfomance_1
        assert actual_performance_2 == perfomance_2

@pytest.mark.skipif(not dckr.is_image_running(CONTAINER_NAME), reason=f"There is no container based on the {CONTAINER_NAME} is running.")
@pytest.mark.skipif(IntegrationDb.db_int_not_available(), reason=f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
def test_update_notified_users_table(schemas,init_scripts):

    with IntegrationDb(schemas, init_scripts) as CONNECTION_STRING:

        # Execute
        film_db_manager = FilmDatabaseManager(CONNECTION_STRING) # type: ignore
        user_list = film_db_manager.get_users_to_notify()
        film_db_manager.update_notified_users_table(user_list)

        # Verify
        # user_id = user_list[0].user_id
        user_dict = {item.user_id: item for item in user_list}
        user = user_dict.get(5)
        user = film_db_manager._get_user_by_user_id(user.user_id)

        assert user.user_id == 5
        assert user.chat_id == "444411111"
        assert user.message_id == "1050"
        assert user.title == "Creator"
        assert user.notified is True
        assert user.film_id is not None
        assert user.film_id == "58E63000012BHGWDVI"
