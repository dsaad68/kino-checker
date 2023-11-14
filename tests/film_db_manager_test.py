import os
import sys
import pytest

from datetime import datetime, timedelta

from integeration_db.docker_container import Docker
from integeration_db.integration_db import IntegrationDb, EnvVar


sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from miner.fetcher.film_db_manager import FilmDatabaseManager # noqa: E402

CONTAINER_NAME = "postgres:alpine3.18"

dckr = Docker()

@pytest.mark.skipif(not dckr.is_image_running(CONTAINER_NAME), reason=f"There is no container based on the {CONTAINER_NAME} is running.")
@pytest.mark.skipif(IntegrationDb.db_int_not_available(), reason=f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
def test_update_films_table():

    schemas = ["tracker"]
    init_scripts = ["init-db/init-db.sql", "init-db/sample-data.sql"]

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
            "last_updated": "2023-11-13 19:14:38.574222"
        }

        # TODO: add a test case with upsert

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

        film_db_manager.update_films_table(films_list=[exists, dont_exist])
        end = datetime.now() + timedelta(seconds=1)  # adding buffer

        # Verify
        oppenheimer_film = film_db_manager._get_film_by_title("Oppenheimer")

        assert oppenheimer_film is not None
        assert oppenheimer_film.film_id == "2EE63000012BHGWDVI" # type: ignore
        assert oppenheimer_film.title == "Oppenheimer" # type: ignore
        assert oppenheimer_film.name == "Oppenheimer"  # type: ignore
        assert oppenheimer_film.production_year == 2022 # type: ignore
        assert oppenheimer_film.length_in_minutes == 180 # type: ignore
        assert oppenheimer_film.nationwide_start == "2023-07-20" # type: ignore
        assert oppenheimer_film.image_url == "https://contentservice.cineorder.shop/contents/img?q=683jXD30IV9SmgAABHGWNjb" # type: ignore
        assert start <= oppenheimer_film.last_checked <= end

        wish_film = film_db_manager._get_film_by_film_id("2EE63000012BHGWDVI")

        assert wish_film is not None
        assert wish_film.film_id == "2EE63000012BHGWDVI" # type: ignore
        assert wish_film.title == "Wish" # type: ignore
        assert wish_film.name == "Wish"  # type: ignore
        assert wish_film.production_year == 2022 # type: ignore
        assert wish_film.length_in_minutes == 95 # type: ignore
        assert wish_film.nationwide_start == "2023-11-30" # type: ignore
        assert wish_film.image_url == "https://contentservice.cineorder.shop/contents/img?q=fDJ8M3w3fDEwMjI3OTZfL3JDQ3JHNHN3a3hnRlpmbHVwNTZzeDZ5bWs1aS5qcGdffA" # type: ignore # noqa: E501
        assert start <= wish_film.last_checked <= end

@pytest.mark.skipif(not dckr.is_image_running(CONTAINER_NAME), reason=f"There is no container based on the {CONTAINER_NAME} is running.")
@pytest.mark.skipif(IntegrationDb.db_int_not_available(), reason=f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
def test_update_performances_table():

    schemas = ["tracker"]
    init_scripts = ["init-db/init-db.sql", "init-db/sample-data.sql"]

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
            "last_updated": "2023-11-13 19:14:38.658222"
            }

        # TODO: add a test case with upsert

        dont_exist = {
            "performance_id": "9EC45000023UHQLKCP",
            "film_id": "4ED63000012BHGWDVI",
            "film_id_p": "4ED63000012BHGWDVI",
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

        film_db_manager.update_performances_table(performances_list=[exists, dont_exist])
        end = datetime.now() + timedelta(seconds=1)  # adding buffer

        # Verify
        existing_performance = film_db_manager._get_film_by_film_id("A6D63000012BHGWDVI")

        assert existing_performance is not None
        assert existing_performance.performance_id == "71D45000023UHQLKCP" # type: ignore
        assert existing_performance.film_id == "A6D63000012BHGWDVI" # type: ignore
        assert existing_performance.film_id_p == "A6D63000012BHGWDVI" # type: ignore
        assert existing_performance.performance_datetime == "2023-12-06 17:15:00" # type: ignore
        assert existing_performance.performance_date == "2023-12-06" # type: ignore
        assert existing_performance.performance_time == "17:15:00" # type: ignore
        assert existing_performance.release_type == "englisch/OV" # type: ignore
        assert existing_performance.is_imax is False # type: ignore
        assert existing_performance.is_ov  # type: ignore
        assert existing_performance.is_3d is False # type: ignore
        assert existing_performance.auditorium_id == "10000000015UHQLKCP" # type: ignore
        assert existing_performance.auditorium_name == "Kino 1" # type: ignore
        assert start <= existing_performance.last_checked <= end

        new_performance = film_db_manager._get_performance_by_performance_id("9EC45000023UHQLKCP")

        assert new_performance is not None
        assert new_performance.performance_id == "9EC45000023UHQLKCP" # type: ignore
        assert new_performance.film_id == "4ED63000012BHGWDVI" # type: ignore
        assert new_performance.film_id_p == "4ED63000012BHGWDVI" # type: ignore
        assert new_performance.performance_datetime == "2023-11-22 16:45:00" # type: ignore
        assert new_performance.performance_date == "2023-11-22" # type: ignore
        assert new_performance.performance_time == "16:45:00" # type: ignore
        assert new_performance.release_type == "IMAX/Digital" # type: ignore
        assert new_performance.is_imax # type: ignore
        assert new_performance.is_ov  is False# type: ignore
        assert new_performance.is_3d is False # type: ignore
        assert new_performance.auditorium_id == "30000000015UHQLKCP" # type: ignore
        assert new_performance.auditorium_name == "Kino 3" # type: ignore
        assert start <= new_performance.last_checked <= end


@pytest.mark.skipif(not dckr.is_image_running(CONTAINER_NAME), reason=f"There is no container based on the {CONTAINER_NAME} is running.")
@pytest.mark.skipif(IntegrationDb.db_int_not_available(), reason=f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
def test_update_upcoming_table():

    schemas = ["kino"]
    init_scripts = ["init-db/init-db.sql", "init-db/sample-data.sql"]

    with IntegrationDb(schemas, init_scripts) as CONNECTION_STRING:

        # Prepare

        exists = {
            "title": "Napoleon",
            "release_date": "2023-11-23",
            "last_updated": "2023-11-13 19:14:43.311786",
            }

        # TODO: add a test case with upsert

        dont_exist = {
            "title": "WONKA",
            "release_date": "2023-12-07",
            "last_updated": datetime.now()
            }

        # Execute
        start = datetime.now() - timedelta(seconds=1)  # adding buffer
        film_db_manager = FilmDatabaseManager(CONNECTION_STRING) # type: ignore

        film_db_manager.update_upcoming_films_table(upcoming_films_list=[exists, dont_exist])
        end = datetime.now() + timedelta(seconds=1)  # adding buffer

        # Verify
        film_napoleon = film_db_manager._get_upcoming_film_by_title("Napoleon")

        assert film_napoleon is not None
        assert film_napoleon.upcoming_film_id == 3 # type: ignore
        assert film_napoleon.title == "Napoleon" # type: ignore
        assert film_napoleon.release_date == "2023-11-23" # type: ignore
        assert film_napoleon.film_id is None # type: ignore
        assert start <= film_napoleon.last_updated <= end # type: ignore
        assert film_napoleon.is_released is False # type: ignore
        assert film_napoleon.is_trackable is True # type: ignore

        film_wonka = film_db_manager._get_upcoming_film_by_title("WONKA")

        assert film_wonka is not None
        assert film_wonka.upcoming_film_id == 5  # type: ignore
        assert film_wonka.title == "WONKA" # type: ignore
        assert film_wonka.release_date == "2023-12-07" # type: ignore
        assert film_wonka.film_id is None # type: ignore
        assert start <= film_wonka.last_updated <= end # type: ignore
        assert film_napoleon.is_released is False # type: ignore
        assert film_napoleon.is_trackable is True # type: ignore
