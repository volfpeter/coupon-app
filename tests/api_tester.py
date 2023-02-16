from typing import Callable

from fastapi.testclient import TestClient


class TestAPI:
    __slots__ = ()

    router_prefix = ""

    def test_get_all_empty(self, client: TestClient, make_url: Callable[[str], str]):
        url = make_url(self.router_prefix)
        response = client.get(url)
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_by_id_missing(self, client: TestClient, make_url: Callable[[str], str]):
        url = make_url(f"{self.router_prefix}/1")
        response = client.get(url)
        assert response.status_code == 404

    def test_update_missing(self, client: TestClient, make_url: Callable[[str], str]):
        url = make_url(f"{self.router_prefix}/1")
        response = client.put(url, json={})
        assert response.status_code == 404

    def test_delete_missing(self, client: TestClient, make_url: Callable[[str], str]):
        url = make_url(f"{self.router_prefix}/1")
        response = client.delete(url)
        assert response.status_code == 404
