from typing import Any, Callable

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from tests.api_tester import TestAPI as _TestAPI

ROUTER_PREFIX = "customer"


class TestCustomerAPI(_TestAPI):
    __slots__ = ()

    router_prefix = ROUTER_PREFIX

    def test_create_fail(self, client: TestClient, make_url: Callable[[str], str]):
        url = make_url(self.router_prefix)

        payloads: dict[str, dict] = {
            "empty": {},
            "incomplete-name-missing": {"username": "whoami"},
            "incomplete-username-missing": {"name": "Yoda"},
            "complete-invalid-bad-name": {"username": "whoami", "name": {}},
            "complete-invalid-bad-username": {"username": "x", "name": "Too short"},
        }

        for name, data in payloads.items():
            response = client.post(url, json=data)
            assert response.status_code == 422, f"Data name: {name}"

    def test_create_success(self, client: TestClient, make_url: Callable[[str], str]):
        base_url = make_url(self.router_prefix)

        data = {"name": "Jack", "username": "jack"}

        dt_start = datetime.utcnow().astimezone(timezone.utc)

        response = client.post(base_url, json=data)
        assert response.status_code == 200

        response_data = response.json()

        assert response_data["id"] == 1
        assert response_data["name"] == data["name"]
        assert response_data["username"] == data["username"]

        created_at = datetime.fromisoformat(response_data["created_at"])
        assert isinstance(created_at, datetime)
        assert created_at.tzinfo == timezone.utc
        assert dt_start < created_at < datetime.utcnow().astimezone(timezone.utc)

    def test_all_rest(self, client: TestClient, make_url: Callable[[str], str]):
        base_url = make_url(self.router_prefix)
        id_url = make_url(f"{self.router_prefix}/1")

        # -- Create

        data = {"name": "Jack", "username": "jack"}

        dt_before_create = datetime.utcnow().astimezone(timezone.utc)

        response = client.post(base_url, json=data)
        assert response.status_code == 200

        dt_after_create = datetime.utcnow().astimezone(timezone.utc)

        def assert_result_valid(result: Any, stage: str, override: dict | None = None):
            expected = {**data, **(override or {})}
            assert isinstance(result, dict), stage
            assert result["id"] == 1, stage
            assert result["name"] == expected["name"], stage
            assert result["username"] == expected["username"], stage

            created_at = datetime.fromisoformat(result["created_at"])
            assert isinstance(created_at, datetime), stage
            assert created_at.tzinfo == timezone.utc, stage
            assert dt_before_create < created_at < dt_after_create, stage

        assert_result_valid(response.json(), "create")

        # -- Get all

        response = client.get(base_url)
        assert response.status_code == 200

        response_data = response.json()

        assert isinstance(response_data, list)
        assert len(response_data) == 1
        assert_result_valid(response_data[0], "get_all")

        # -- Get by ID

        response = client.get(id_url)
        assert response.status_code == 200

        assert_result_valid(response.json(), "get_all")

        # -- Update

        changes = {"name": "New Name"}
        response = client.put(id_url, json=changes)
        assert response.status_code == 200
        assert_result_valid(response.json(), "update name", changes)

        # -- Delete

        response = client.delete(id_url)
        assert response.status_code == 200

        # -- End state

        response = client.get(base_url)
        response_data = response.json()
        assert response.status_code == 200
        assert isinstance(response_data, list)
        assert len(response_data) == 0

        response = client.get(id_url)
        assert response.status_code == 404

        response = client.delete(id_url)
        assert response.status_code == 404
