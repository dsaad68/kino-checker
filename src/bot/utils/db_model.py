#%%
from sqlalchemy import MetaData
from dataclasses import dataclass
from datetime import date, datetime
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Time, ForeignKey, Sequence

#%%
# Define the schema for the tracker database
metadata_obj = MetaData(schema="tracker")

# Define a base class for declarative models
Base = declarative_base(metadata=metadata_obj)

# Define a model for the tracker.films table
class Films(Base):
    __tablename__ = "films"
    film_id = Column(String(255), primary_key=True)
    title = Column(String(255), nullable=False)
    name = Column(String(255))
    production_year = Column(Integer)
    length_in_minutes = Column(Integer)
    nationwide_start = Column(String(255))
    image_url = Column(String(255))
    last_updated = Column(DateTime)


# Define a model for the tracker.performances table
class Performances(Base):
    __tablename__ = "performances"
    performance_id = Column(String(255), primary_key=True)
    film_id = Column(String(255), ForeignKey("tracker.films.film_id"))
    film_id_p = Column(String(255))
    performance_datetime = Column(DateTime)
    performance_date = Column(Date)
    performance_time = Column(Time)
    release_type = Column(String(255))
    is_imax = Column(Boolean)
    is_ov = Column(Boolean)
    is_3d = Column(Boolean)
    auditorium_id = Column(String(255))
    auditorium_name = Column(String(255))
    last_updated = Column(DateTime)


# Define a model for the tracker.upcoming_films table
class UpcomingFilms(Base):
    __tablename__ = "upcoming_films"

    # Define the sequence for upcoming_film_id
    upcoming_film_id_seq = Sequence('upcoming_film_id_seq', metadata=Base.metadata, increment=1, start=1, cycle=False, schema='tracker')

    # Define the columns
    upcoming_film_id = Column(Integer, upcoming_film_id_seq, server_default=upcoming_film_id_seq.next_value(), primary_key=True)
    title = Column(String(255), nullable=False, unique=True)
    release_date = Column(Date)
    film_id = Column(String(255), ForeignKey("tracker.films.film_id"))
    last_updated = Column(DateTime)
    is_released = Column(Boolean, default=False)
    is_trackable = Column(Boolean, default=True)


# Define a model for the tracker.users table
class Users(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    chat_id = Column(String(255), nullable=False)
    message_id = Column(String(255), nullable=False)
    film_id = Column(String(255), ForeignKey("tracker.films.film_id"), nullable=False)
    title = Column(String(255), nullable=False)
    notified = Column(Boolean, default=False)


@dataclass
class UsersFilmInfo:
    """Dataclass for users film info"""
    user_id: int
    chat_id: str
    message_id: str
    notified: bool
    film_id: str
    title: str
    length_in_minutes: int
    last_updated: datetime
    nationwide_start: date
    is_imax: bool
    is_ov: bool
    is_3d: bool

    def get_last_updated(self) -> str:
        return self.last_updated.strftime('%Y-%m-%d %H:%M:%S')
