import os
import sys
import pytest

from integeration_db.integration_db import IntegrationDb, EnvVar  # noqa: E402
from integeration_db.docker_container import Docker               # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from miner.miner_helpers.db_updater import session_maker, update_films_list, update_films_status # noqa: E401, E402

CONTAINER_NAME = "postgres:16-bookworm"

dckr = Docker()

@pytest.mark.skipif(not dckr.is_image_running(CONTAINER_NAME), reason=f"There is no container based on the {CONTAINER_NAME} is running.")
@pytest.mark.skipif(IntegrationDb.db_int_not_available(), reason=f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
def test_something():
    
    schemas = ['kino']
    init_scripts = ["init-db/init-db.sql"]

    with IntegrationDb(schemas, init_scripts) as CONNECTION_STRING:
        
        Session_Maker = session_maker(CONNECTION_STRING)