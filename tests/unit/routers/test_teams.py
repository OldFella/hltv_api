from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.main import app
from src.domain.models import Item, TeamDetail, MatchResult, TeamScore, MapScore, TeamMapStats
from src.domain.errors import NotFoundError
from datetime import date

client = TestClient(app, raise_server_exceptions=False)

MOCK_ITEM = Item(id=1, name="NaVi")

MOCK_TEAM_DETAIL = TeamDetail(
    id=1,
    name="NaVi",
    streak=3,
    roster=[Item(id=1, name="s1mple")]
)

MOCK_MAP_SCORE = MapScore(id=1, name="Mirage", team1_score=16, team2_score=14)

MOCK_MATCH = MatchResult(
    id=1,
    maps=[MOCK_MAP_SCORE],
    team1=TeamScore(id=1, name="NaVi", score=1, rank=1),
    team2=TeamScore(id=2, name="Astralis", score=0, rank=2),
    best_of=1,
    date=date(2024, 1, 1),
    event="ESL Pro League",
    winner=Item(id=1, name="NaVi")
)

MOCK_STATS = [TeamMapStats(id=1, name="Mirage", n=10, n_wins=7)]

# ---------------------------------------------------------------------------
# GET /teams/
# ---------------------------------------------------------------------------

@patch("src.routers.teams.use_cases.get_all_fuzzy", return_value=[MOCK_ITEM])
class TestGetTeams:
    def test_returns_200(self, mock_uc):
        assert client.get("/teams/").status_code == 200

    def test_returns_list(self, mock_uc):
        assert isinstance(client.get("/teams/").json(), list)

    def test_returns_correct_shape(self, mock_uc):
        data = client.get("/teams/").json()[0]
        assert "id" in data and "name" in data

    def test_name_filter(self, mock_uc):
        assert client.get("/teams/?name=NaVi").status_code == 200

    def test_pagination(self, mock_uc):
        assert client.get("/teams/?limit=5&offset=0").status_code == 200

@patch("src.routers.teams.use_cases.get_all_fuzzy", side_effect=Exception("DB error"))
class TestGetTeamsError:
    def test_server_error(self, mock_uc):
        assert client.get("/teams/").status_code == 500

# ---------------------------------------------------------------------------
# GET /teams/{teamid}
# ---------------------------------------------------------------------------

@patch("src.routers.teams.use_cases.get_team", return_value=MOCK_TEAM_DETAIL)
class TestGetTeam:
    def test_returns_200(self, mock_uc):
        assert client.get("/teams/1").status_code == 200

    def test_returns_correct_shape(self, mock_uc):
        data = client.get("/teams/1").json()
        assert all(k in data for k in ["id", "name", "streak", "roster"])

@patch("src.routers.teams.use_cases.get_team", side_effect=NotFoundError("Team 999"))
class TestGetTeamNotFound:
    def test_not_found(self, mock_uc):
        assert client.get("/teams/999").status_code == 404

# ---------------------------------------------------------------------------
# GET /teams/{teamid}/matchhistory
# ---------------------------------------------------------------------------

@patch("src.routers.teams.use_cases.get_team_matchhistory", return_value=[MOCK_MATCH])
class TestGetMatchHistory:
    def test_returns_200(self, mock_uc):
        assert client.get("/teams/1/matchhistory").status_code == 200

    def test_returns_list(self, mock_uc):
        assert isinstance(client.get("/teams/1/matchhistory").json(), list)

    def test_returns_correct_shape(self, mock_uc):
        data = client.get("/teams/1/matchhistory").json()[0]
        assert all(k in data for k in ["id", "maps", "team1", "team2", "best_of", "winner"])

    def test_pagination(self, mock_uc):
        assert client.get("/teams/1/matchhistory?limit=3&offset=0").status_code == 200

@patch("src.routers.teams.use_cases.get_team_matchhistory", side_effect=NotFoundError("Team 999"))
class TestGetMatchHistoryNotFound:
    def test_not_found(self, mock_uc):
        assert client.get("/teams/999999/matchhistory").status_code == 404

# ---------------------------------------------------------------------------
# GET /teams/{teamid}/stats
# ---------------------------------------------------------------------------

@patch("src.routers.teams.use_cases.get_team_stats", return_value=MOCK_STATS)
class TestGetTeamStats:
    def test_returns_200(self, mock_uc):
        assert client.get("/teams/1/stats").status_code == 200

    def test_returns_list(self, mock_uc):
        assert isinstance(client.get("/teams/1/stats").json(), list)

    def test_returns_correct_shape(self, mock_uc):
        data = client.get("/teams/1/stats").json()[0]
        assert all(k in data for k in ["id", "name", "n", "n_wins"])

@patch("src.routers.teams.use_cases.get_team_stats", side_effect=NotFoundError("Team 999"))
class TestGetTeamStatsNotFound:
    def test_not_found(self, mock_uc):
        assert client.get("/teams/999/stats").status_code == 404