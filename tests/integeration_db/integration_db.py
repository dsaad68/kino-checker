import os
import enum
import logging

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.engine import create_engine


class EnvVar(enum.Enum):
    INT_DB_URL = enum.auto


class IntegrationDb:

    def __init__(self, schemas: list[str], init_scripts: list[str]):
        if IntegrationDb.db_int_not_available():
            raise ValueError(f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
        self.schemas = schemas
        self.ini_scripts = init_scripts

    def __enter__(self):
        url = os.environ.get(EnvVar.INT_DB_URL.name)
        self.engine = create_engine(url if url is not None else "")
        with self.engine.connect() as connection:
            self._create_schemas(connection)
            try:
                self._execute_init_scripts(connection)
            except Exception as e:
                self._drop_schemas()
                logging.error(e)
                raise e
            connection.commit()
        return url

    def __exit__(self, type, value, traceback):
        self._drop_schemas()

        try:
            del os.environ[EnvVar.INT_DB_URL.name]
        except Exception as e:
            logging.error(e)
            raise e

    def _create_schemas(self, connection):
        for schema in self.schemas:
            connection.execute(text(f"CREATE SCHEMA {schema}"))
            logging.info(f"--- Schema with name {schema} was created! ---")

    def _execute_init_scripts(self, connection):
        for init_script in self.ini_scripts:
            with open(init_script) as file:
                script_sql = file.read()
                connection.execute(text(script_sql))
                logging.info(f"--- Init script with name {init_script} was successfully executed! ---")

    def _drop_schemas(self):
        try:
            with self.engine.connect() as connection:
                for schema in self.schemas:
                    connection.execute(text(f"DROP SCHEMA {schema} CASCADE;"))
                    logging.info(f"--- Cleaned up schema {schema} ----")
                connection.commit()
        except Exception as e:
            logging.warning(e)

    @staticmethod
    def _get_db_url():
        # Load environment variables from .env file
        load_dotenv()
        return os.environ.get(EnvVar.INT_DB_URL.name)

    @staticmethod
    def db_int_not_available():
        return IntegrationDb._get_db_url() is None
