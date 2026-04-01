import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from src.main import app
from tests.endpoints.schemas import assert_item, assert_fantasy_response

class TestFantasyEndpoints:

    @pytest.mark.asyncio
    async def test_list_fantasies(self, client: AsyncClient):
        r = await client.get("/fantasy/")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        for item in data:
            assert_item(item)

    @pytest.mark.asyncio
    async def test_fantasy_by_id(self, client: AsyncClient):
        fantasies = (await client.get("/fantasy/")).json()
        if not fantasies:
            pytest.skip("No fantasy events available")
        fantasy_id = fantasies[0]["id"]
        r = await client.get(f"/fantasy/{fantasy_id}")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == fantasy_id
        print(data)
        assert_fantasy_item_response(data)

    @pytest.mark.asyncio
    async def test_fantasy_salary_cap_and_costs_are_integers(self, client: AsyncClient):
        """Salary cap and player costs are integers expressed in thousands."""
        fantasies = (await client.get("/fantasy/")).json()
        if not fantasies:
            pytest.skip("No fantasy events available")
        r = await client.get(f"/fantasy/{fantasies[0]['id']}")
        data = r.json()
        assert isinstance(data["salary_cap"], int)
        for team in data["teams"]:
            for player in team["players"]:
                assert isinstance(player["cost"], int)

    @pytest.mark.asyncio
    async def test_fantasy_invalid_id_type(self, client: AsyncClient):
        r = await client.get("/fantasy/not-an-int")
        assert r.status_code == 422