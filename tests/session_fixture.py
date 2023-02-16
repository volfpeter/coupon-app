import pytest

from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool

from app_model import initialize_database


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    initialize_database(engine)

    with Session(engine) as session:
        yield session
