from typing import Generator

from functools import lru_cache

from fastapi import FastAPI, Depends
from sqlalchemy.future import Engine
from sqlmodel import Session, create_engine


@lru_cache(maxsize=1)
def get_database_engine() -> "Engine":
    """
    Returns a database engine instance.
    """
    sqlite_file_name = "database.db"
    sqlite_url = f"sqlite:///{sqlite_file_name}"
    connect_args = {"check_same_thread": False}

    return create_engine(sqlite_url, echo=True, connect_args=connect_args)


def get_session(engine: "Engine" = Depends(get_database_engine)) -> Generator[Session, None, None]:
    """
    Session provider FastAPI dependency.
    """
    with Session(engine) as session:
        yield session


def register_routes(app: FastAPI, *, api_prefix="/api/v1") -> None:
    """
    Registers all the routes of the application.

    Arguments:
        app: The FastAPI application where the routes should be registered.
        api_prefix: API prefix for the included routes.
    """
    from app_model.coupon.api import make_api as make_coupon_api
    from app_model.customer.api import make_api as make_customer_api

    # Register all APIs with the same settings.
    for make_api in (make_coupon_api, make_customer_api):
        app.include_router(make_api(session_provider=get_session), prefix=api_prefix)


def create_app() -> FastAPI:
    """
    Creates a new application instance.
    """
    # -- Application config

    app = FastAPI()

    @app.on_event("startup")
    def on_startup() -> None:
        from app_model import initialize_database

        engine = get_database_engine()
        initialize_database(engine)

    # -- Routing

    register_routes(app)

    return app
