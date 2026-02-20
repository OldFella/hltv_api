from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import HTTPException
from src.main import app

client = TestClient(app)

MOCK_MATCH = {
    "id": 1,
    "maps": [{"id": 1, "name": "Mirage", "team1_score": 16, "team2_score": 14}],
    "team1": {"id": 1, "name": "NaVi", "score": 1},
    "team2": {"id": 2, "name": "Astralis", "score": 0},
    "best_of": 1,
    "date": "2024-01-01",
    "event": "ESL Pro League",
    "winner": {"id": 1, "name": "NaVi"}
}


# ---------------------------------------------------------------------------
# GET /matches/
# ---------------------------------------------------------------------------

@patch("src.routers.matches.format_matches", return_value=[MOCK_MATCH])
@patch("src.routers.matches.execute_query", return_value=[MOCK_MATCH])
class TestGetMatches:
    def test_returns_200(self, mock_eq, mock_fm):
        assert client.get("/matches/").status_code == 200

    def test_returns_list(self, mock_eq, mock_fm):
        assert isinstance(client.get("/matches/").json(), list)

    def test_returns_correct_shape(self, mock_eq, mock_fm):
        data = client.get("/matches/").json()[0]
        assert all(k in data for k in ["id", "maps", "team1", "team2", "best_of", "winner"])

    def test_pagination(self, mock_eq, mock_fm):
        assert client.get("/matches/?limit=5&offset=0").status_code == 200


@patch("src.routers.matches.execute_query", side_effect=HTTPException(status_code=404, detail="Item not found"))
class TestGetMatchesNotFound:
    def test_not_found(self, mock_eq):
        assert client.get("/matches/").status_code == 404


# ---------------------------------------------------------------------------
# GET /matches/latest
# ---------------------------------------------------------------------------

@patch("src.routers.matches.format_matches", return_value=[MOCK_MATCH])
@patch("src.routers.matches.execute_query", return_value=[MOCK_MATCH])
class TestGetLatestMatches:
    def test_returns_200(self, mock_eq, mock_fm):
        assert client.get("/matches/latest").status_code == 200

    def test_returns_list(self, mock_eq, mock_fm):
        assert isinstance(client.get("/matches/latest").json(), list)

    def test_default_limit(self, mock_eq, mock_fm):
        assert len(client.get("/matches/latest").json()) <= 10


# ---------------------------------------------------------------------------
# GET /matches/{matchid}
# ---------------------------------------------------------------------------

@patch("src.routers.matches.format_matches", return_value=[MOCK_MATCH])
@patch("src.routers.matches.execute_query", return_value=[MOCK_MATCH])
class TestGetMatch:
    def test_returns_200(self, mock_eq, mock_fm):
        assert client.get("/matches/1").status_code == 200

    def test_returns_correct_shape(self, mock_eq, mock_fm):
        data = client.get("/matches/1").json()
        assert all(k in data for k in ["id", "maps", "team1", "team2", "best_of", "winner"])


@patch("src.routers.matches.execute_query", side_effect=HTTPException(status_code=404, detail="Item not found"))
class TestGetMatchNotFound:
    def test_not_found(self, mock_eq):
        assert client.get("/matches/999999").status_code == 404


# ---------------------------------------------------------------------------
# GET /matches/{matchid}/maps
# ---------------------------------------------------------------------------

@patch("src.routers.matches.format_matches", return_value=[MOCK_MATCH])
@patch("src.routers.matches.execute_query", return_value=[MOCK_MATCH])
class TestGetMatchMaps:
    def test_returns_200(self, mock_eq, mock_fm):
        assert client.get("/matches/1/maps").status_code == 200

    def test_returns_correct_shape(self, mock_eq, mock_fm):
        data = client.get("/matches/1/maps").json()
        assert "maps" in data


@patch("src.routers.matches.execute_query", side_effect=HTTPException(status_code=404, detail="Item not found"))
class TestGetMatchMapsNotFound:
    def test_not_found(self, mock_eq):
        assert client.get("/matches/999999/maps").status_code == 404