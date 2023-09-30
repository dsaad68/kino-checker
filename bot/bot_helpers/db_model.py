
from sqlalchemy import Column, Integer, String, Boolean, Text, TIMESTAMP
from sqlalchemy.orm import declarative_base

# Define a base class for declarative models
Base = declarative_base()

# Define a model for the kino.films table
class Films(Base):
    __tablename__ = "films"
    __table_args__ = {"schema": "kino"}
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    link = Column(Text)
    img_link = Column(Text)
    last_checked = Column(TIMESTAMP)
    availability = Column(Boolean, default=False)
    availability_date = Column(TIMESTAMP)
    imax_3d_ov = Column(Boolean, default=False)
    imax_ov = Column(Boolean, default=False)
    hd_ov = Column(Boolean, default=False)
    last_update = Column(Boolean, default=False)
    trackable = Column(Boolean, default=True)

# Define a model for the kino.users table
class Users(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "kino"}
    id = Column(Integer, primary_key=True)
    chat_id = Column(String(255), nullable=False)
    message_id = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    notified = Column(Boolean, default=False)