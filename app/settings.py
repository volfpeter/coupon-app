from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite///database.db"
    database_echo: bool = False

    class Config:
        env_file = ".env"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    FastAPI dependency that returns the application's settings.
    """
    return Settings()
