from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.main import app
from src.domain.models import (
    Item, PlayerDetail, PlayerStats,
    PlayerStatRow, PlayerGroupedStats,
    PlayerAggregatedStats
)
from src.domain.errors import NotFoundError

client = TestClient(app)

# ---------------------------------------------------------------------------
# Mock data
# ---------------------------------------------------------------------------

MOCK_ITEM = Item(id=1, name="zywoo")

MOCK_PLAYER_STAT_ROW = PlayerStatRow(
    id=1, name="zywoo",
    team_id=1, team_name="Vitality",
    k=23.0, d=2.0, swing=5.3,
    adr=85.0, kast=0.72, rating=1.3,
    N=20,
)

MOCK_PLAYER_DETAIL = PlayerDetail(
    id=1, name="zywoo",
    team=Item(id=1, name="Vitality"),
    stats=PlayerStats(
        k=23.0, d=2.0, swing=5.3,
        adr=85.0, kast=0.72, rating=1.3,
        N=20,
    )
)

MOCK_GROUPED_STATS = PlayerGroupedStats(
    id=1, name="Mirage",
    k=1.2, d=0.8, swing=0.1,
    adr=85.0, kast=0.72, rating=1.3,
    N=20,
)

MOCK_AGGREGATED_STATS = PlayerAggregatedStats(
    rank=1, id=1, name="zywoo",
    k=500, d=200, swing=0.3,
    adr=85.0, kast=0.72, rating=1.3,
    N=100,
)
# ---------------------------------------------------------------------------
# GET /players/
# ---------------------------------------------------------------------------

class TestGetPlayers:
    def test_returns_200(self):
        with patch("src.routers.players.get_all_fuzzy", return_value=[MOCK_ITEM]):
            assert client.get("/players/").status_code == 200

    def test_returns_list(self):
        with patch("src.routers.players.get_all_fuzzy", return_value=[MOCK_ITEM]):
            assert isinstance(client.get("/players/").json(), list)

    def test_returns_correct_shape(self):
        with patch("src.routers.players.get_all_fuzzy", return_value=[MOCK_ITEM]):
            data = client.get("/players/").json()[0]
            assert "id" in data and "name" in data

    def test_pagination(self):
        with patch("src.routers.players.get_all_fuzzy", return_value=[MOCK_ITEM]):
            assert client.get("/players/?limit=5&offset=0").status_code == 200

    def test_name_filter(self):
        with patch("src.routers.players.get_all_fuzzy", return_value=[MOCK_ITEM]):
            assert client.get("/players/?name=zywoo").status_code == 200

    def test_empty_returns_200(self):
        with patch("src.routers.players.get_all_fuzzy", return_value=[]):
            assert client.get("/players/").status_code == 200


# ---------------------------------------------------------------------------
# GET /players/stats
# ---------------------------------------------------------------------------

class TestGetPlayerAggregatedStats:
    def test_returns_200(self):
        with patch("src.routers.players.get_aggregated_stats", return_value=[MOCK_AGGREGATED_STATS]):
            assert client.get("/players/stats").status_code == 200

    def test_returns_list(self):
        with patch("src.routers.players.get_aggregated_stats", return_value=[MOCK_AGGREGATED_STATS]):
            assert isinstance(client.get("/players/stats").json(), list)

    def test_returns_correct_shape(self):
        with patch("src.routers.players.get_aggregated_stats", return_value=[MOCK_AGGREGATED_STATS]):
            data = client.get("/players/stats").json()[0]
            assert all(k in data for k in ["rank", "id", "name", "k", "d", "rating", "N"])

    def test_mapid_filter(self):
        with patch("src.routers.players.get_aggregated_stats", return_value=[MOCK_AGGREGATED_STATS]):
            assert client.get("/players/stats?mapid=2").status_code == 200

    def test_sideid_filter(self):
        with patch("src.routers.players.get_aggregated_stats", return_value=[MOCK_AGGREGATED_STATS]):
            assert client.get("/players/stats?sideid=1").status_code == 200

    def test_min_played_filter(self):
        with patch("src.routers.players.get_aggregated_stats", return_value=[MOCK_AGGREGATED_STATS]):
            assert client.get("/players/stats?min_played=20").status_code == 200

    def test_empty_returns_200(self):
        with patch("src.routers.players.get_aggregated_stats", return_value=[]):
            assert client.get("/players/stats").status_code == 200


# ---------------------------------------------------------------------------
# GET /players/stats/raw
# ---------------------------------------------------------------------------

class TestGetPlayerRawStats:
    def test_returns_200(self):
        with patch("src.routers.players.get_raw_stats", return_value=[MOCK_PLAYER_STAT_ROW]):
            assert client.get("/players/stats/raw").status_code == 200

    def test_returns_list(self):
        with patch("src.routers.players.get_raw_stats", return_value=[MOCK_PLAYER_STAT_ROW]):
            assert isinstance(client.get("/players/stats/raw").json(), list)

    def test_returns_correct_shape(self):
        with patch("src.routers.players.get_raw_stats", return_value=[MOCK_PLAYER_STAT_ROW]):
            data = client.get("/players/stats/raw").json()[0]
            assert all(k in data for k in ["id", "name", "k", "d", "rating", "N"])

    def test_mapid_filter(self):
        with patch("src.routers.players.get_raw_stats", return_value=[MOCK_PLAYER_STAT_ROW]):
            assert client.get("/players/stats/raw?mapid=2").status_code == 200

    def test_sideid_filter(self):
        with patch("src.routers.players.get_raw_stats", return_value=[MOCK_PLAYER_STAT_ROW]):
            assert client.get("/players/stats/raw?sideid=1").status_code == 200


# ---------------------------------------------------------------------------
# GET /players/stats/raw/{outcome}
# ---------------------------------------------------------------------------

class TestGetPlayerRawStatsByOutcome:
    def test_win_returns_200(self):
        with patch("src.routers.players.get_raw_stats_by_outcome", return_value=[MOCK_PLAYER_STAT_ROW]):
            assert client.get("/players/stats/raw/win").status_code == 200

    def test_lose_returns_200(self):
        with patch("src.routers.players.get_raw_stats_by_outcome", return_value=[MOCK_PLAYER_STAT_ROW]):
            assert client.get("/players/stats/raw/lose").status_code == 200

    def test_invalid_outcome_returns_422(self):
        assert client.get("/players/stats/raw/draw").status_code == 422

    def test_returns_correct_shape(self):
        with patch("src.routers.players.get_raw_stats_by_outcome", return_value=[MOCK_PLAYER_STAT_ROW]):
            data = client.get("/players/stats/raw/win").json()[0]
            assert all(k in data for k in ["id", "name", "k", "d", "rating"])


# ---------------------------------------------------------------------------
# GET /players/{playerid}
# ---------------------------------------------------------------------------

class TestGetPlayer:
    def test_returns_200(self):
        with patch("src.routers.players.get_player", return_value=MOCK_PLAYER_DETAIL):
            assert client.get("/players/1").status_code == 200

    def test_returns_correct_shape(self):
        with patch("src.routers.players.get_player", return_value=MOCK_PLAYER_DETAIL):
            data = client.get("/players/1").json()
            assert all(k in data for k in ["id", "name", "team", "stats"])
            assert all(k in data["stats"] for k in ["k", "d", "swing", "adr", "kast", "rating", "N"])

    def test_team_shape(self):
        with patch("src.routers.players.get_player", return_value=MOCK_PLAYER_DETAIL):
            data = client.get("/players/1").json()
            assert all(k in data["team"] for k in ["id", "name"])

    def test_date_filter(self):
        with patch("src.routers.players.get_player", return_value=MOCK_PLAYER_DETAIL):
            assert client.get("/players/1?start_date=2024-01-01&end_date=2024-03-01").status_code == 200

    def test_not_found(self):
        with patch("src.routers.players.get_player", side_effect=NotFoundError("Player 999")):
            assert client.get("/players/999").status_code == 404

    def test_invalid_playerid_returns_422(self):
        assert client.get("/players/abc").status_code == 422


# ---------------------------------------------------------------------------
# GET /players/{playerid}/stats/{group}
# ---------------------------------------------------------------------------

class TestGetPlayerGroupedStats:
    def test_maps_returns_200(self):
        with patch("src.routers.players.get_player_grouped_stats", return_value=[MOCK_GROUPED_STATS]):
            assert client.get("/players/1/stats/maps").status_code == 200

    def test_sides_returns_200(self):
        with patch("src.routers.players.get_player_grouped_stats", return_value=[MOCK_GROUPED_STATS]):
            assert client.get("/players/1/stats/sides").status_code == 200

    def test_events_returns_200(self):
        with patch("src.routers.players.get_player_grouped_stats", return_value=[MOCK_GROUPED_STATS]):
            assert client.get("/players/1/stats/events").status_code == 200

    def test_invalid_group_returns_422(self):
        assert client.get("/players/1/stats/invalid").status_code == 422

    def test_returns_list(self):
        with patch("src.routers.players.get_player_grouped_stats", return_value=[MOCK_GROUPED_STATS]):
            assert isinstance(client.get("/players/1/stats/maps").json(), list)

    def test_returns_correct_shape(self):
        with patch("src.routers.players.get_player_grouped_stats", return_value=[MOCK_GROUPED_STATS]):
            data = client.get("/players/1/stats/maps").json()[0]
            assert all(k in data for k in ["id", "name", "k", "d", "rating", "N"])

    def test_mapid_filter_sides(self):
        with patch("src.routers.players.get_player_grouped_stats", return_value=[MOCK_GROUPED_STATS]):
            assert client.get("/players/1/stats/sides?mapid=1").status_code == 200

    def test_mapid_filter_events(self):
        with patch("src.routers.players.get_player_grouped_stats", return_value=[MOCK_GROUPED_STATS]):
            assert client.get("/players/1/stats/events?mapid=1").status_code == 200

    def test_date_filter(self):
        with patch("src.routers.players.get_player_grouped_stats", return_value=[MOCK_GROUPED_STATS]):
            assert client.get("/players/1/stats/maps?start_date=2024-01-01&end_date=2024-03-01").status_code == 200

    def test_not_found(self):
        with patch("src.routers.players.get_player_grouped_stats", side_effect=NotFoundError("Player 999")):
            assert client.get("/players/999/stats/maps").status_code == 404