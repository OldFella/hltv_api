import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from src.main import app
from tests.endpoints.schemas import assert_item, assert_team_response, assert_match_response

class TestTeamsEndpoints:

    @pytest.mark.asyncio
    async def test_list_teams_default(self, client: AsyncClient):
        r = await client.get("/teams/")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) <= 20            # default limit
        for team in data:
            assert_item(team)

    @pytest.mark.asyncio
    async def test_list_teams_limit_offset(self, client: AsyncClient):
        r = await client.get("/teams/", params={"limit": 3, "offset": 0})
        assert r.status_code == 200
        assert len(r.json()) <= 3

    @pytest.mark.asyncio
    async def test_list_teams_name_filter(self, client: AsyncClient):
        r = await client.get("/teams/", params={"name": "Vit", "limit": 50})
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        for team in data:
            assert_item(team)

    @pytest.mark.asyncio
    async def test_team_by_id(self, client: AsyncClient):
        teams = (await client.get("/teams/")).json()
        if not teams:
            pytest.skip("No teams in DB")
        team_id = teams[0]["id"]
        r = await client.get(f"/teams/{team_id}")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == team_id
        assert_team_response(data)

    @pytest.mark.asyncio
    async def test_team_invalid_id_type(self, client: AsyncClient):
        r = await client.get("/teams/not-an-int")
        assert r.status_code == 422

    @pytest.mark.asyncio
    async def test_team_match_history_default(self, client: AsyncClient):
        teams = (await client.get("/teams/")).json()
        if not teams:
            pytest.skip("No teams in DB")
        team_id = teams[0]["id"]
        r = await client.get(f"/teams/{team_id}/matchhistory")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) <= 5             # default limit
        for match in data:
            assert_match_response(match)

    @pytest.mark.asyncio
    async def test_team_match_history_limit(self, client: AsyncClient):
        teams = (await client.get("/teams/")).json()
        if not teams:
            pytest.skip("No teams in DB")
        team_id = teams[0]["id"]
        r = await client.get(f"/teams/{team_id}/matchhistory", params={"limit": 2})
        assert r.status_code == 200
        assert len(r.json()) <= 2