from unittest.mock import patch
from fastapi.testclient import TestClient
from src.main import app
from fastapi import HTTPException

client = TestClient(app)

MOCK_SIDE = {"id": 1, "name": "CT"}


@patch("src.routers.sides.execute_query", return_value=[MOCK_SIDE])
class TestGetSides:
    def test_returns_200(self, mock_eq):
        assert client.get("/sides/").status_code == 200

    def test_returns_list(self, mock_eq):
        assert isinstance(client.get("/sides/").json(), list)

    def test_returns_correct_shape(self, mock_eq):
        data = client.get("/sides/").json()[0]
        assert "id" in data and "name" in data


@patch("src.routers.sides.execute_query", return_value=MOCK_SIDE)
class TestGetSide:
    def test_returns_200(self, mock_eq):
        assert client.get("/sides/1").status_code == 200

    def test_returns_correct_shape(self, mock_eq):
        data = client.get("/sides/1").json()
        assert "id" in data and "name" in data

@patch("src.routers.sides.execute_query", side_effect=HTTPException(status_code=404, detail="Item not found"))
class TestGetSideNotFound:
    def test_not_found(self, mock_eq):
        assert client.get("/sides/999999").status_code == 404