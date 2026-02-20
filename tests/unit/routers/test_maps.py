from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import HTTPException
from src.main import app

client = TestClient(app)

MOCK_MAP = {"id": 1, "name": "Mirage"}


@patch("src.routers.maps.execute_query", return_value=[MOCK_MAP])
class TestGetMaps:
    def test_returns_200(self, mock_eq):
        assert client.get("/maps/").status_code == 200

    def test_returns_list(self, mock_eq):
        assert isinstance(client.get("/maps/").json(), list)

    def test_returns_correct_shape(self, mock_eq):
        data = client.get("/maps/").json()[0]
        assert "id" in data and "name" in data


@patch("src.routers.maps.execute_query", return_value=MOCK_MAP)
class TestGetMap:
    def test_returns_200(self, mock_eq):
        assert client.get("/maps/1").status_code == 200

    def test_returns_correct_shape(self, mock_eq):
        data = client.get("/maps/1").json()
        assert "id" in data and "name" in data


@patch("src.routers.maps.execute_query", side_effect=HTTPException(status_code=404, detail="Item not found"))
class TestGetMapNotFound:
    def test_not_found(self, mock_eq):
        assert client.get("/maps/999999").status_code == 404