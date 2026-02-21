from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import HTTPException
from src.main import app

client = TestClient(app)

MOCK_TEAM = {
  "id": 1,
  "name": "NaVi"
}
MOCK_ROSTER = {
    "id":1,
    "name":'s1mple'
}
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
# GET /teams/
# ---------------------------------------------------------------------------

@patch("src.routers.teams.execute_query", return_value=[MOCK_TEAM])
class TestGetTeams:
    def test_returns_200(self, mock_eq):
        assert client.get("/teams/").status_code == 200

    def test_returns_list(self, mock_eq):
        assert isinstance(client.get("/teams/").json(), list)

    def test_returns_correct_shape(self, mock_eq):
        data = client.get("/teams/").json()[0]
        assert "id" in data and "name" in data

    def test_name_filter(self, mock_eq):
        assert client.get("/teams/?name=NaVi").status_code == 200

    def test_pagination(self, mock_eq):
        assert client.get("/teams/?limit=5&offset=0").status_code == 200


@patch("src.routers.teams.execute_query", side_effect=HTTPException(status_code=404, detail="Item not found"))
class TestGetTeamsNotFound:
    def test_not_found(self, mock_eq):
        assert client.get("/teams/").status_code == 404


# ---------------------------------------------------------------------------
# GET /teams/{teamid}
# ---------------------------------------------------------------------------

@patch("src.routers.teams.build_roster_query")
@patch("src.routers.teams.build_match_query")
@patch("src.routers.teams.format_matches", return_value=[MOCK_MATCH])
@patch("src.routers.teams.execute_query")
class TestGetTeam:
    def test_returns_200(self, mock_eq, mock_fm, mock_bm, mock_br):
        mock_eq.side_effect = [MOCK_TEAM, [MOCK_MATCH], [MOCK_ROSTER]]
        assert client.get("/teams/1").status_code == 200

    def test_returns_correct_shape(self, mock_eq, mock_eq2, mock_fm, mock_eq3):
        mock_eq.side_effect = [MOCK_TEAM, [MOCK_MATCH], [MOCK_ROSTER]]
        data = client.get("/teams/1").json()
        assert all(k in data for k in ["id", "name", "streak", "roster"])



@patch("src.routers.teams.execute_query", side_effect=HTTPException(status_code=404, detail="Item not found"))
class TestGetTeamNotFound:
    def test_not_found(self, mock_eq):
        assert client.get("/teams/999999").status_code == 404


# ---------------------------------------------------------------------------
# GET /teams/{teamid}/matchhistory
# ---------------------------------------------------------------------------

@patch("src.routers.teams.format_matches", return_value=[MOCK_MATCH])
@patch("src.routers.teams.execute_query", return_value=[MOCK_MATCH])
class TestGetMatchHistory:
    def test_returns_200(self, mock_eq, mock_fm):
        assert client.get("/teams/1/matchhistory").status_code == 200

    def test_returns_list(self, mock_eq, mock_fm):
        assert isinstance(client.get("/teams/1/matchhistory").json(), list)

    def test_returns_correct_shape(self, mock_eq, mock_fm):
        data = client.get("/teams/1/matchhistory").json()[0]
        assert all(k in data for k in ["id", "maps", "team1", "team2", "best_of", "winner"])

    def test_pagination(self, mock_eq, mock_fm):
        assert client.get("/teams/1/matchhistory?limit=3&offset=0").status_code == 200


@patch("src.routers.teams.execute_query", side_effect=HTTPException(status_code=404, detail="Item not found"))
class TestGetMatchHistoryNotFound:
    def test_not_found(self, mock_eq):
        assert client.get("/teams/999999/matchhistory").status_code == 404