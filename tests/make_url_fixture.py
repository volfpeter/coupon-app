from typing import Callable

import pytest

from app.settings import get_settings


@pytest.fixture(name="make_url")
def make_url_fixture() -> Callable[[str], str]:
    settings = get_settings()
    api_prefx = settings.api_prefix

    def make_url(subpath: str) -> str:
        return f"{api_prefx.rstrip('/')}/{subpath.lstrip('/')}"

    return make_url
