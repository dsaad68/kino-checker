# %%
import logging

from typing import Type, Callable

from sqlalchemy.sql import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Update
from psycopg2.errors import CardinalityViolation
from sqlalchemy.dialects.postgresql import Insert
from sqlalchemy.exc import SQLAlchemyError, ProgrammingError

#%%

class DBManager:
    """This class is used to manage the database connection and session."""

    def __init__(self, connection_uri: str):
        self.connection_uri = connection_uri
        self.session_maker = self._session_maker()

    def _session_maker(self) -> sessionmaker:
        """Creates a session factory for connecting to the database."""

        # Define the database connection
        engine = create_engine(self.connection_uri, pool_size=2, max_overflow=2)
        # Define a session factory
        return sessionmaker(bind=engine)

    def execute_insert_stmt(self, stmt: Insert | Update) -> None:
        """Execute an upsert statement."""

        try:
            # Create a new session
            with self.session_maker() as session:
                # Execute the upsert statement
                session.execute(stmt)
                # Commit the changes and close the session
                session.commit()
        except ProgrammingError as error:
            # Check if the original error is a CardinalityViolation
            if isinstance(error.orig, CardinalityViolation):
                logging.error("CardinalityViolation error occurred", exc_info=True)
                session.rollback()
                raise CardinalityViolation from error
            else:
                logging.error(f"ProgrammingError: {error}", exc_info=True)
            # Rollback the transaction
            session.rollback()
        except Exception as error:
            logging.error(f"ERROR : {error}", exc_info=True)
            session.rollback()  # type: ignore

    # INFO: old name: execute_query
    def execute_fetch_one(self, model: Type, filter_condition: Callable) -> Type | None:
        """Execute a query with a given a statement."""

        # sourcery skip: class-extract-method, extract-duplicate-method
        try:
            with self.session_maker() as session:
                return session.execute(select(model).where(filter_condition(model))).scalars().first()
        except SQLAlchemyError as error:
            logging.error(f"Database Error: {error}", exc_info=True)
            session.rollback()  # type: ignore
            return None
        except Exception as error:
            logging.error(f"ERROR : {error}", exc_info=True)
            session.rollback()  # type: ignore
            return None

    def execute_query_mapping_all(self, stmt) -> list[dict] | None:
        """Execute a query with a given a statement."""

        # sourcery skip: class-extract-method, extract-duplicate-method
        try:
            with self.session_maker() as session: # type: ignore
                return session.execute(stmt).mappings().all()
        except SQLAlchemyError as error:
            logging.error(f"Database Error: {error}", exc_info=True)
            session.rollback()  # type: ignore
            return None
        except Exception as error:
            logging.error(f"ERROR : {error}", exc_info=True)
            session.rollback()  # type: ignore
            return None

    def execute_query_all(self, stmt) -> list[Type] | None:
        """Execute a query with a given a statement."""

        # sourcery skip: class-extract-method, extract-duplicate-method
        try:
            with self.session_maker() as session: # type: ignore
                return session.execute(stmt).scalars().all()
        except SQLAlchemyError as error:
            logging.error(f"Database Error: {error}", exc_info=True)
            session.rollback()  # type: ignore
            return None
        except Exception as error:
            logging.error(f"ERROR : {error}", exc_info=True)
            session.rollback()  # type: ignore
            return None
