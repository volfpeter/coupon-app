from typing import Generator, Protocol

from datetime import datetime, timezone

from pydantic.datetime_parse import parse_datetime
from sqlmodel import Session


class SessionContextProvider(Protocol):
    """
    Session context provider FastAPI dependency/context manager.
    """

    def __call__(self) -> Generator[Session, None, None]:
        ...


class UTCDatetime(datetime):
    @classmethod
    def __get_validators__(cls):
        yield parse_datetime  # default pydantic behavior
        yield cls.ensure_utc

    @classmethod
    def ensure_utc(cls, value: datetime) -> datetime:
        """
        Makes sure the given datetime is in UTC.
        If `value` has no timezone info, the method sets UTC.
        Raises:
            ValueError: If `value` has timezone info but it's not UTC.
        """
        tzinfo = value.tzinfo
        if tzinfo is None:  # No timezone info, assume UTC.
            return value.replace(tzinfo=timezone.utc)

        if tzinfo == timezone.utc:  # Timezone is UTC, no-op.
            return value

        # Non-UTC timezone info, raise exception.
        raise ValueError("Non-UTC timezone.")
