"""Pydantic models for data validation across all services."""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FilmBase(BaseModel):
    """Base model for film data."""

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    title: str = Field(..., min_length=1, max_length=500, description="Film title")
    film_id: str = Field(..., min_length=1, max_length=100, description="Unique film identifier")


class Film(FilmBase):
    """Complete film information."""

    name: str = Field(..., min_length=1, max_length=500, description="Film display name")
    description: str | None = Field(None, description="Film description")
    duration: int | None = Field(None, gt=0, description="Film duration in minutes")


class UpcomingFilm(BaseModel):
    """Model for upcoming film data."""

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    title: str = Field(..., min_length=1, max_length=500)
    upcoming_film_id: int = Field(..., gt=0)
    film_id: str | None = Field(None, max_length=100)
    is_trackable: bool = Field(default=True)
    is_released: bool = Field(default=False)
    link: str | None = Field(None, max_length=1000)


class PerformanceFlags(BaseModel):
    """Model for performance version flags."""

    model_config = ConfigDict(frozen=True)

    is_ov: bool | None = Field(None, description="Original version flag")
    is_imax: bool | None = Field(None, description="IMAX version flag")
    is_3d: bool | None = Field(None, description="3D version flag")

    @field_validator("is_ov", "is_imax", "is_3d", mode="before")
    @classmethod
    def convert_int_to_bool(cls, v: Any) -> bool | None:
        """Convert integer flags (0, 1, 2) to boolean or None."""
        if v is None or v == 2:
            return None
        if v == 1:
            return True
        if v == 0:
            return False
        if isinstance(v, bool):
            return v
        raise ValueError(f"Invalid flag value: {v}. Must be 0, 1, 2, or boolean.")


class Performance(BaseModel):
    """Model for film performance data."""

    model_config = ConfigDict(str_strip_whitespace=True)

    performance_id: str = Field(..., min_length=1, max_length=100)
    film_id: str = Field(..., min_length=1, max_length=100)
    performance_date: date
    performance_time: time
    performance_datetime: datetime
    is_ov: bool = Field(default=False)
    is_imax: bool = Field(default=False)
    is_3d: bool = Field(default=False)


class UserPreferences(BaseModel):
    """Model for user film preferences."""

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    chat_id: str = Field(..., min_length=1, max_length=100)
    message_id: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=500)
    flags: PerformanceFlags

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UserPreferences:
        """Create UserPreferences from dictionary with flags parsing."""
        from common.call_parser import CallParser

        parsed_flags = CallParser.parse(data.get("flags", ""))
        flags = PerformanceFlags(
            is_ov=parsed_flags.get("is_ov"), is_imax=parsed_flags.get("is_imax"), is_3d=parsed_flags.get("is_3d")
        )

        return cls(chat_id=data["chat_id"], message_id=data["message_id"], title=data["title"], flags=flags)


class NotificationRequest(BaseModel):
    """Model for notification request data."""

    model_config = ConfigDict(frozen=True)

    user_id: int = Field(..., gt=0)
    chat_id: str = Field(..., min_length=1)
    message_id: str = Field(..., min_length=1)
    film_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)


class APIFilmResponse(BaseModel):
    """Model for validating film data from external API."""

    model_config = ConfigDict(extra="ignore")  # Ignore extra fields from API

    film_id: str = Field(..., alias="filmId")
    title: str
    name: str | None = None
    duration: int | None = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        """Ensure title is not empty or whitespace."""
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()


class APIPerformanceResponse(BaseModel):
    """Model for validating performance data from external API."""

    model_config = ConfigDict(extra="ignore")

    performance_id: str = Field(..., alias="performanceId")
    film_id: str = Field(..., alias="filmId")
    performance_datetime: datetime = Field(..., alias="performanceDateTime")
    is_ov: bool = Field(default=False, alias="isOV")
    is_imax: bool = Field(default=False, alias="isIMAX")
    is_3d: bool = Field(default=False, alias="is3D")

    @property
    def performance_date(self) -> date:
        """Extract date from datetime."""
        return self.performance_datetime.date()

    @property
    def performance_time(self) -> time:
        """Extract time from datetime."""
        return self.performance_datetime.time()
