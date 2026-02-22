from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import HTTPException
from src.main import app

client = TestClient(app)

MOCK_FANTASY = {'id': 1, 'name': 'Fantasy 2024'}
MOCK_FANTASY_PLAYER = {
    'player_id': 1, 'player_name': 's1mple',
    'team_id': 1, 'team_name': 'NaVi',
    'cost': 100.0
}

# ---------------------------------------------------------------------------
# GET /fantasy/
# ---------------------------------------------------------------------------

@patch("src.routers.fantasy.execute_query", return_value=[MOCK_FANTASY])
class TestGetFantasies:
    def test_returns_200(self, mock_eq):
        assert client.get("/fantasy/").status_code == 200

    def test_returns_list(self, mock_eq):
        assert isinstance(client.get("/fantasy/").json(), list)

    def test_returns_correct_shape(self, mock_eq):
        data = client.get("/fantasy/").json()[0]
        assert "id" in data and "name" in data


@patch("src.routers.fantasy.execute_query", side_effect=HTTPException(status_code=404, detail="Not found"))
class TestGetFantasiesNotFound:
    def test_not_found(self, mock_eq):
        assert client.get("/fantasy/").status_code == 404


# ---------------------------------------------------------------------------
# GET /fantasy/{fantasyid}
# ---------------------------------------------------------------------------

@patch("src.routers.fantasy.execute_query")
class TestGetFantasy:
    def test_returns_200(self, mock_eq):
        mock_eq.side_effect = [MOCK_FANTASY, [MOCK_FANTASY_PLAYER]]
        assert client.get("/fantasy/1").status_code == 200

    def test_returns_correct_shape(self, mock_eq):
        mock_eq.side_effect = [MOCK_FANTASY, [MOCK_FANTASY_PLAYER]]
        data = client.get("/fantasy/1").json()
        assert all(k in data for k in ["id", "name", "salary_cap", "currency", "teams"])

    def test_teams_have_players(self, mock_eq):
        mock_eq.side_effect = [MOCK_FANTASY, [MOCK_FANTASY_PLAYER]]
        data = client.get("/fantasy/1").json()
        assert len(data["teams"]) == 1
        assert len(data["teams"][0]["players"]) == 1

    def test_player_shape(self, mock_eq):
        mock_eq.side_effect = [MOCK_FANTASY, [MOCK_FANTASY_PLAYER]]
        data = client.get("/fantasy/1").json()
        player = data["teams"][0]["players"][0]
        assert all(k in player for k in ["id", "name", "cost"])


@patch("src.routers.fantasy.execute_query", side_effect=HTTPException(status_code=404, detail="Not found"))
class TestGetFantasyNotFound:
    def test_not_found(self, mock_eq):
        assert client.get("/fantasy/999").status_code == 404