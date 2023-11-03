import os
import sys
import pytest

from datetime import datetime

from integeration_db.integration_db import IntegrationDb, EnvVar
from integeration_db.docker_container import Docker

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from miner.miner_helpers.film_database_manager import FilmDatabaseManager  # noqa: E402

CONTAINER_NAME = "postgres:alpine3.18"

dckr = Docker()

@pytest.mark.skipif(not dckr.is_image_running(CONTAINER_NAME), reason=f"There is no container based on the {CONTAINER_NAME} is running.")
@pytest.mark.skipif(IntegrationDb.db_int_not_available(), reason=f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
def test_get_films_db_status():

    schemas = ['kino']
    init_scripts = ["init-db/init-db.sql", "init-db/sample-data.sql"]

    with IntegrationDb(schemas, init_scripts) as CONNECTION_STRING:

        # Execute
        film_db_manager = FilmDatabaseManager(CONNECTION_STRING)
        films_list = film_db_manager.get_films_db_status()

        # Test
        equalizer_film = films_list[0]
        assert len(films_list) == 1
        assert equalizer_film.get('title') == 'The Equalizer 3'
        assert equalizer_film.get('availability')
        assert equalizer_film.get('imax_3d_ov') is False
        assert equalizer_film.get('imax_ov') is False
        assert equalizer_film.get('hd_ov')
        assert equalizer_film.get('last_checked') == datetime(2023, 7, 20, 0, 4, 53)
        assert equalizer_film.get('link') == 'https://www.filmpalast.net/film/the-equalizer-3.html'
        assert equalizer_film.get('chat_id') == '200788221'
        assert equalizer_film.get('message_id') == '1073'
