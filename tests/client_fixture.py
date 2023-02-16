from typing import Generator

import pytest

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.main import create_app, get_database_session

from .session_fixture import session_fixture  # noqa


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    app = create_app()

    try:
        app.dependency_overrides[get_database_session] = lambda: session

        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
