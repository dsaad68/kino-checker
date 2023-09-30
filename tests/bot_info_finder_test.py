import os
import sys
import pytest
import datetime

from integeration_db.integration_db import IntegrationDb, EnvVar
from integeration_db.docker_container import Docker

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from bot.bot_helpers.info_finder import session_maker, get_films_list_db, get_film_info_db, update_users_db # noqa: E402
from bot.bot_helpers.db_model import Users # noqa: E402

CONTAINER_NAME = "postgres:16-bookworm"

dckr = Docker()

@pytest.mark.skipif(not dckr.is_image_running(CONTAINER_NAME), reason=f"There is no container based on the {CONTAINER_NAME} is running.")
@pytest.mark.skipif(IntegrationDb.db_int_not_available(), reason=f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
def test_get_films_list_db():

    schemas = ['kino']
    init_scripts = ["init-db/init-db.sql", "init-db/sample-data.sql"]

    with IntegrationDb(schemas, init_scripts) as CONNECTION_STRING:

        Session_Maker = session_maker(CONNECTION_STRING)

        Result = get_films_list_db(Session_Maker)

        assert Result == ['The Equalizer 3', 'Oppenheimer', 'The Flash', 'Transformers - Aufstieg der Bestien']

@pytest.mark.skipif(not dckr.is_image_running(CONTAINER_NAME), reason=f"There is no container based on the {CONTAINER_NAME} is running.")
@pytest.mark.skipif(IntegrationDb.db_int_not_available(), reason=f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
def test_get_film_info_db():

    schemas = ['kino']
    init_scripts = ["init-db/init-db.sql", "init-db/sample-data.sql"]

    with IntegrationDb(schemas, init_scripts) as CONNECTION_STRING:

        Session_Maker = session_maker(CONNECTION_STRING)

        Result = get_film_info_db(title= 'Transformers - Aufstieg der Bestien', Session_Maker= Session_Maker)

        assert Result == {'title': 'Transformers - Aufstieg der Bestien',
                        'availability': True,
                        'imax_3d_ov': True,
                        'imax_ov': False,
                        'hd_ov': False,
                        'last_checked': datetime.datetime(2023, 6, 8, 0, 3, 14),
                        'link': 'https://www.filmpalast.net/film/transformers-aufstieg-der-bestien.html'}

@pytest.mark.skipif(not dckr.is_image_running(CONTAINER_NAME), reason=f"There is no container based on the {CONTAINER_NAME} is running.")
@pytest.mark.skipif(IntegrationDb.db_int_not_available(), reason=f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
def test_update_users_db():

    schemas = ['kino']
    init_scripts = ["init-db/init-db.sql"]

    with IntegrationDb(schemas, init_scripts) as CONNECTION_STRING:

        Session_Maker = session_maker(CONNECTION_STRING)
        update_users_db(chat_id=222, message_id=333, title='Oppenheimer', Session_Maker= Session_Maker)

        with Session_Maker() as session:
            user = session.query(Users).first()

            assert user.chat_id == '222'
            assert user.message_id == '333'
            assert user.title == 'Oppenheimer'
