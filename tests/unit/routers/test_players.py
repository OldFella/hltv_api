from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.main import app
from src.domain.models import (
    Item, PlayerDetail, PlayerStats,
    PlayerStatRow, PlayerGroupedStats,
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


