from typing import Generator

from fastapi import FastAPI, Depends
from sqlalchemy.future import Engine
from sqlmodel import Session, create_engine

from app_utils.typing import APIFactory

from .settings import Settings, get_settings


def get_database_engine(settings: Settings = Depends(get_settings)) -> "Engine":
    """
    Returns a database engine instance.
    """
    if settings.database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    else:
        connect_args = {}

    return create_engine(settings.database_url, echo=settings.database_echo, connect_args=connect_args)


def get_database_session(engine: "Engine" = Depends(get_database_engine)) -> Generator[Session, None, None]:
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
    from app_model.customer_coupon.api import make_api as make_customer_coupon_api

    api_factories: tuple[APIFactory, ...] = (make_coupon_api, make_customer_api, make_customer_coupon_api)

    # Register all APIs with the same settings.
    for make_api in api_factories:
        app.include_router(make_api(session_provider=get_database_session), prefix=api_prefix)


def create_app() -> FastAPI:
    """
    Creates a new application instance.
    """
    # -- Application config

    settings = get_settings()

    app = FastAPI()

    @app.on_event("startup")
    def on_startup() -> None:
        from app_model import initialize_database

        engine = get_database_engine(get_settings())
        initialize_database(engine)

    # -- Routing

    register_routes(app, api_prefix=settings.api_prefix)

    return app
