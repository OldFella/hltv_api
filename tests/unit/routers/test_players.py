from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import HTTPException
from src.main import app

client = TestClient(app)

MOCK_PLAYER_STATS = {
    "id": 1, "name": "zywoo",
    "k": 23, "d": 2, "swing": 5.3,
    "adr": 85.0, "kast": 0.72, "rating": 1.3,
    "maps_played": 20
}
MOCK_PLAYER = {"id": 1, "name": "zywoo", "stats": MOCK_PLAYER_STATS}

MOCK_GROUPED_STATS = [{
    "id": 1, "name": "Mirage",
    "k": 1.2, "d": 0.8, "swing": 0.1,
    "adr": 85.0, "kast": 0.72, "rating": 1.3,
    "maps_played": 20
}]
MOCK_TEAM = {'id': 1, 'name': 'Vitality'}

# ---------------------------------------------------------------------------
# GET /players/
# ---------------------------------------------------------------------------

@patch("src.routers.players.execute_query", return_value=[MOCK_PLAYER])
class TestGetPlayers:
    def test_returns_200(self, mock_eq):
        assert client.get("/players/").status_code == 200

    def test_returns_list(self, mock_eq):
        assert isinstance(client.get("/players/").json(), list)

    def test_returns_correct_shape(self, mock_eq):
        data = client.get("/players/").json()[0]
        assert "id" in data and "name" in data

    def test_pagination(self, mock_eq):
        assert client.get("/players/?limit=5&offset=0").status_code == 200

    def test_name_filter(self, mock_eq):
        assert client.get("/players/?name=s1mple").status_code == 200


@patch("src.routers.players.execute_query", side_effect=HTTPException(status_code=404, detail="Item not found"))
class TestGetPlayersNotFound:
    def test_not_found(self, mock_eq):
        assert client.get("/players/").status_code == 404


# ---------------------------------------------------------------------------
# GET /players/stats/
# ---------------------------------------------------------------------------

@patch("src.routers.players.format_stats", return_value=[MOCK_PLAYER_STATS])
@patch("src.routers.players.execute_query", return_value=[MOCK_PLAYER_STATS])
class TestGetPlayerStats:
    def test_returns_200(self, mock_eq, mock_fs):
        assert client.get("/players/stats/").status_code == 200

    def test_returns_list(self, mock_eq, mock_fs):
        assert isinstance(client.get("/players/stats/").json(), list)

    def test_pagination(self, mock_eq, mock_fs):
        assert client.get("/players/stats/?limit=5&offset=0").status_code == 200
    
    def test_returns_correct_shape(self, mock_eq, mock_fs):
        data = client.get("/players/stats/").json()[0]
        assert all(k in data for k in ["id", "name", "k", "d", "rating", "maps_played"])


# ---------------------------------------------------------------------------
# GET /players/{playerid}
# ---------------------------------------------------------------------------

@patch("src.routers.players.build_team_query")
@patch("src.routers.players.format_stats", return_value=[MOCK_PLAYER_STATS])
@patch("src.routers.players.execute_query")
class TestGetPlayer:
    def test_returns_200(self, mock_eq, mock_fs, mock_btq):
        mock_eq.side_effect = [MOCK_PLAYER_STATS, MOCK_TEAM]
        assert client.get("/players/1").status_code == 200

    def test_returns_correct_shape(self, mock_eq, mock_fs, mock_btq):
        mock_eq.side_effect = [MOCK_PLAYER_STATS, MOCK_TEAM]
        data = client.get("/players/1").json()
        assert all(k in data for k in ["id", "name", "team", "stats"])
        
    def test_date_filter(self, mock_eq, mock_fs, mock_btq):
        mock_eq.side_effect = [MOCK_PLAYER_STATS, MOCK_TEAM]
        assert client.get("/players/1?start_date=2024-01-01&end_date=2024-03-01").status_code == 200


@patch("src.routers.players.execute_query", side_effect=HTTPException(status_code=404, detail="Item not found"))
class TestGetPlayerNotFound:
    def test_not_found(self, mock_eq):
        assert client.get("/players/999999").status_code == 404


# ---------------------------------------------------------------------------
# GET /players/{playerid}/stats/{group}
# ---------------------------------------------------------------------------

@patch("src.routers.players.format_stats", return_value=MOCK_GROUPED_STATS)
@patch("src.routers.players.execute_query", return_value=MOCK_GROUPED_STATS)
class TestGetPlayerGroupedStats:
    def test_maps_returns_200(self, mock_eq, mock_fs):
        assert client.get("/players/1/stats/maps").status_code == 200

    def test_sides_returns_200(self, mock_eq, mock_fs):
        assert client.get("/players/1/stats/sides").status_code == 200

    def test_events_returns_200(self, mock_eq, mock_fs):
        assert client.get("/players/1/stats/events").status_code == 200

    def test_returns_list(self, mock_eq, mock_fs):
        assert isinstance(client.get("/players/1/stats/maps").json(), list)

    def test_mapid_filter(self, mock_eq, mock_fs):
        assert client.get("/players/1/stats/maps?mapid=1").status_code == 200
    
    def test_returns_correct_shape(self, mock_eq, mock_fs):
        data = client.get("/players/1/stats/maps").json()[0]
        assert all(k in data for k in ["id", "name", "k", "d", "rating"])


@patch("src.routers.players.execute_query", side_effect=HTTPException(status_code=404, detail="Item not found"))
class TestGetPlayerGroupedStatsNotFound:
    def test_not_found(self, mock_eq):
        assert client.get("/players/999999/stats/maps").status_code == 404