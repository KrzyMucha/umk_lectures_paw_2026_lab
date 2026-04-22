import sys
import importlib
from pathlib import Path

from fastapi.testclient import TestClient
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

main = importlib.import_module("main")

app = main.app


class FakeCursor:
    def __init__(self, rows: list[dict] | None = None, one_row: dict | None = None):
        self._rows = rows or []
        self._one_row = one_row

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, query, params=None):
        return None

    def fetchall(self):
        return self._rows

    def fetchone(self):
        return self._one_row


class FakeConnection:
    def __init__(self, rows: list[dict] | None = None, one_row: dict | None = None):
        self._rows = rows
        self._one_row = one_row

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def cursor(self):
        return FakeCursor(rows=self._rows, one_row=self._one_row)

    def commit(self):
        return None

client = TestClient(app)


def test_get_users_returns_all_users_with_expected_shape(monkeypatch: pytest.MonkeyPatch) -> None:
    rows = [
        {
            "id": 1,
            "email": "anna.nowak@example.com",
            "first_name": "Anna",
            "last_name": "Nowak",
            "roles": "ROLE_CUSTOMER",
            "super_seller_id": None,
        },
        {
            "id": 2,
            "email": "jan.kowalski@example.com",
            "first_name": "Jan",
            "last_name": "Kowalski",
            "roles": "ROLE_SELLER",
            "super_seller_id": 4,
        },
    ]

    monkeypatch.setenv("DATABASE_URL", "postgresql://app:app@localhost:5432/app")
    monkeypatch.setattr(main.psycopg, "connect", lambda *args, **kwargs: FakeConnection(rows=rows))

    response = client.get("/users")

    assert response.status_code == 200
    payload = response.json()

    assert isinstance(payload, list)
    assert len(payload) == 2

    first = payload[0]
    expected_keys = {
        "id",
        "email",
        "firstName",
        "lastName",
        "fullName",
        "roles",
        "isCustomer",
        "isSeller",
        "superSellerId",
    }

    assert set(first.keys()) == expected_keys
    assert isinstance(first["id"], int)
    assert isinstance(first["email"], str)
    assert isinstance(first["firstName"], str)
    assert isinstance(first["lastName"], str)
    assert isinstance(first["fullName"], str)
    assert isinstance(first["roles"], list)
    assert isinstance(first["isCustomer"], bool)
    assert isinstance(first["isSeller"], bool)


def test_get_user_by_id_returns_existing_user(monkeypatch: pytest.MonkeyPatch) -> None:
    row = {
        "id": 2,
        "email": "jan.kowalski@example.com",
        "first_name": "Jan",
        "last_name": "Kowalski",
        "roles": "ROLE_SELLER",
        "super_seller_id": None,
    }

    monkeypatch.setenv("DATABASE_URL", "postgresql://app:app@localhost:5432/app")
    monkeypatch.setattr(main.psycopg, "connect", lambda *args, **kwargs: FakeConnection(one_row=row))

    response = client.get("/user/2")

    assert response.status_code == 200
    payload = response.json()

    assert payload["id"] == 2
    assert payload["email"] == "jan.kowalski@example.com"
    assert payload["roles"] == ["ROLE_SELLER"]
    assert payload["isCustomer"] is False
    assert payload["isSeller"] is True


def test_get_user_by_id_returns_404_for_missing_user(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://app:app@localhost:5432/app")
    monkeypatch.setattr(main.psycopg, "connect", lambda *args, **kwargs: FakeConnection(one_row=None))

    response = client.get("/user/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}
