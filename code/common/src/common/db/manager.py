from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from loguru import logger
from psycopg2.errors import CardinalityViolation
from sqlalchemy import Update, create_engine
from sqlalchemy.dialects.postgresql import Insert
from sqlalchemy.exc import ProgrammingError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql import select

T = TypeVar("T")


class DBManager:
    """This class is used to manage the database connection and session."""

    def __init__(self, connection_uri: str) -> None:
        self.connection_uri: str = connection_uri
        self.session_maker: sessionmaker[Session] = self._session_maker()

    def _session_maker(self) -> sessionmaker[Session]:
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
                logger.error("CardinalityViolation error occurred", exc_info=True)
                raise CardinalityViolation from error
            else:
                logger.error(f"ProgrammingError: {error}", exc_info=True)
        except Exception as error:
            logger.error(f"ERROR : {error}", exc_info=True)

    # INFO: old name: execute_query
    def execute_fetch_one(self, model: type[T], filter_condition: Callable[[type[T]], bool]) -> T | None:
        """Execute a query with a given a statement."""
        try:
            with self.session_maker() as session:
                return session.execute(select(model).where(filter_condition(model))).scalars().first()
        except SQLAlchemyError as error:
            logger.error(f"Database Error: {error}", exc_info=True)
            return None
        except Exception as error:
            logger.error(f"ERROR : {error}", exc_info=True)
            return None

    def execute_query_mapping_all(self, stmt: select) -> list[dict] | None:
        """Execute a query with a given a statement."""
        try:
            with self.session_maker() as session:
                return session.execute(stmt).mappings().all()
        except SQLAlchemyError as error:
            logger.error(f"Database Error: {error}", exc_info=True)
            return None
        except Exception as error:
            logger.error(f"ERROR : {error}", exc_info=True)
            return None

    def execute_query_all(self, stmt: select[tuple[T]]) -> list[T] | None:
        """Execute a query with a given a statement."""
        try:
            with self.session_maker() as session:
                return session.execute(stmt).scalars().all()
        except SQLAlchemyError as error:
            logger.error(f"Database Error: {error}", exc_info=True)
            return None
        except Exception as error:
            logger.error(f"ERROR : {error}", exc_info=True)
            return None
