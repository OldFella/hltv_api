from datetime import date
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from src.main import app
from src.db.get_db import get_db
from src.domain.models import Item, Ranking, TeamRank, Fantasy, FantasyPlayer, FantasyTeam, CountResponse

# === In-memory adapters ===

class MockReadAdapter:
    def __init__(self, items: list[Item]):
        self.items = items

    def get_all(self) -> list[Item]:
        return self.items

    def get_one(self, id: int) -> Item | None:
        return next((i for i in self.items if i.id == id), None)


class MockRankingsAdapter:
    def __init__(self, ranking: Ranking | None):
        self.ranking = ranking

    def get_rankings(self, date: date | None) -> Ranking | None:
        return self.ranking


class MockFantasyAdapter:
    def __init__(self, items: list[Item], fantasy: Fantasy | None):
        self.items = items
        self.fantasy = fantasy

    def get_all(self) -> list[Item]:
        return self.items

    def get_one(self, id: int) -> Fantasy | None:
        if self.fantasy and self.fantasy.id == id:
            return self.fantasy
        return None


class MockCountsAdapter:
    def __init__(self, counts: CountResponse):
        self.counts = counts

    def get_counts(self) -> CountResponse:
        return self.counts


# === Fixtures ===

SIDES = [Item(id=1, name="T"), Item(id=2, name="CT")]
MAPS = [Item(id=1, name="Mirage"), Item(id=2, name="Inferno")]
RANKING = Ranking(
    date=date(2024, 1, 1),
    rankings=[
        TeamRank(id=1, name="NaVi", rank=1, points=900),
        TeamRank(id=2, name="FaZe", rank=2, points=850),
    ]
)
FANTASY_ITEMS = [Item(id=1, name="Fantasy 1"), Item(id=2, name="Fantasy 2")]
FANTASY = Fantasy(
    id=1,
    name="Fantasy 1",
    salary_cap=1000,
    currency="$",
    teams=[
        FantasyTeam(
            id=1,
            name="NaVi",
            players=[FantasyPlayer(id=1, name="s1mple", cost=300)]
        )
    ]
)
COUNTS = CountResponse(players=500, teams=100, matches=2000)

# override get_db to return a dummy connection — adapters are patched so it's never used
app.dependency_overrides[get_db] = lambda: MagicMock()


# === Sides ===

def test_list_sides():
    with patch("src.adapters.sqlalchemy_reference_data.SqlAlchemySideAdapter.get_all", return_value=SIDES):
        response = TestClient(app).get("/sides/")
    assert response.status_code == 200

def test_get_side_found():
    with patch("src.adapters.sqlalchemy_reference_data.SqlAlchemyReadAdapter.get_one", return_value=SIDES[0]):
        response = TestClient(app).get("/sides/1")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "T"}

def test_get_side_not_found():
    with patch("src.adapters.sqlalchemy_reference_data.SqlAlchemyReadAdapter.get_one", return_value=None):
        response = TestClient(app).get("/sides/99")
    assert response.status_code == 404

# === Maps ===

def test_list_maps():
    with patch("src.adapters.sqlalchemy_reference_data.SqlAlchemyMapAdapter.get_all", return_value=MAPS):
        response = TestClient(app).get("/maps/")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_map_found():
    with patch("src.adapters.sqlalchemy_reference_data.SqlAlchemyMapAdapter.get_one", return_value=MAPS[0]):
        response = TestClient(app).get("/maps/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Mirage"

def test_get_map_not_found():
    with patch("src.adapters.sqlalchemy_reference_data.SqlAlchemyMapAdapter.get_one", return_value=None):
        response = TestClient(app).get("/maps/99")
    assert response.status_code == 404


# === Rankings ===

def test_get_rankings_by_date():
    with patch("src.routers.reference_data.SqlAlchemyRankingsAdapter", return_value=MockRankingsAdapter(RANKING)):
        response = TestClient(app).get("/rankings/?date=2024-01-01")
    assert response.status_code == 200


def test_get_rankings():
    with patch("src.adapters.sqlalchemy_reference_data.SqlAlchemyRankingsAdapter.get_rankings", return_value=RANKING):
        response = TestClient(app).get("/rankings/")
    assert response.status_code == 200

def test_get_rankings_not_found():
    with patch("src.adapters.sqlalchemy_reference_data.SqlAlchemyRankingsAdapter.get_rankings", return_value=None):
        response = TestClient(app).get("/rankings/")
    assert response.status_code == 404


# === Fantasy ===

def test_list_fantasies():
    with patch("src.adapters.sqlalchemy_reference_data.SqlAlchemyFantasyAdapter.get_all", return_value=FANTASY_ITEMS):
        response = TestClient(app).get("/fantasy/")
    assert response.status_code == 200

def test_get_fantasy_found():
    with patch("src.adapters.sqlalchemy_reference_data.SqlAlchemyFantasyAdapter.get_one", return_value=FANTASY):
        response = TestClient(app).get("/fantasy/1")
    assert response.status_code == 200

def test_get_fantasy_not_found():
    with patch("src.adapters.sqlalchemy_reference_data.SqlAlchemyFantasyAdapter.get_one", return_value=None):
        response = TestClient(app).get("/fantasy/99")
    assert response.status_code == 404


# === Counts ===

def test_get_counts():
    with patch("src.adapters.sqlalchemy_reference_data.SqlAlchemyCountsAdapter.get_counts", return_value=COUNTS):
        response = TestClient(app).get("/counts/")
    assert response.status_code == 200