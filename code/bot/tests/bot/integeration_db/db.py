from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


def session_maker(connection_url: str) -> sessionmaker[Session]:
    # Define the database connection
    engine = create_engine(connection_url, pool_size=2, max_overflow=2)

    # Define a session factory
    return sessionmaker(bind=engine)
