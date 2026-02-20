from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


class TestGetGoat:
    def test_returns_200(self):
        assert client.get("/goat/").status_code == 200

    def test_returns_correct_shape(self):
        data = client.get("/goat/").json()
        assert "goat" in data

    def test_returns_valid_goat(self):
        data = client.get("/goat/").json()
        assert data["goat"] in ['ZywOo', 'donk', 's0mple', 'dev1ce', 'f0rest']