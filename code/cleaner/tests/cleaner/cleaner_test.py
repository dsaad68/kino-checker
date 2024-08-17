#%%
import pytest

from integeration_db.docker_container import Docker
from integeration_db.integration_db import IntegrationDb, EnvVar

from cleaner.utils.db_cleaner import DBCleaner


#%%

CONTAINER_NAME = "postgres:alpine3.18"

dckr = Docker()

#%%

@pytest.mark.skipif(not dckr.is_image_running(CONTAINER_NAME), reason=f"There is no container based on the {CONTAINER_NAME} is running.")
@pytest.mark.skipif(IntegrationDb.db_int_not_available(), reason=f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
def test_update_trackable_rows(schemas, init_scripts):

    with IntegrationDb(schemas, init_scripts) as CONNECTION_STRING:

        # Execute
        db_cleaner = DBCleaner(CONNECTION_STRING) # type: ignore
        db_cleaner.update_trackable_rows(120)

        # Verify

        # Case 1
        napoleon_film = db_cleaner._get_upcoming_film_by_title("Napoleon")
        assert napoleon_film is not None
        assert napoleon_film.is_released is True
        assert napoleon_film.is_trackable is False

        # Case 2
        saw_x_film = db_cleaner._get_upcoming_film_by_title("SAW X")
        assert saw_x_film is not None
        assert saw_x_film.is_released is True
        assert saw_x_film.is_trackable is False

        # Case 3
        wish_film = db_cleaner._get_upcoming_film_by_title("Wish")
        assert wish_film is not None
        assert wish_film.is_released is True
        assert wish_film.is_trackable is True

        # Case 4
        raus_aus_dem_teich_film = db_cleaner._get_upcoming_film_by_title("Raus aus dem Teich")
        assert raus_aus_dem_teich_film is not None
        assert raus_aus_dem_teich_film.is_released is False
        assert raus_aus_dem_teich_film.is_trackable is True
