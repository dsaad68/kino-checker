from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Time, ForeignKey

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


# Define a model for the tracker.users table
class UpcomingFilms(Base):
    __tablename__ = "upcoming_films"
    upcoming_film_id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False, unique=True)
    release_date = Column(Date)
    film_id = Column(String(255), ForeignKey("tracker.films.film_id"), nullable=True)
    is_released = Column(Boolean, default=False)
    is_trackable = Column(Boolean, default=True)
    last_updated = Column(DateTime)


# Define a model for the tracker.users table
class Users(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    chat_id = Column(String(255), nullable=False)
    message_id = Column(String(255), nullable=False)
    film_id = Column(String(255), ForeignKey("tracker.films.film_id"), nullable=False)
    title = Column(String(255), nullable=False)
    notified = Column(Boolean, default=False)
