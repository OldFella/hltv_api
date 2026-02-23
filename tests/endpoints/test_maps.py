import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from src.main import app
from tests.endpoints.schemas import assert_item

class TestMapsEndpoints:

    @pytest.mark.asyncio
    async def test_list_maps(self, client: AsyncClient):
        r = await client.get("/maps/")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        for item in data:
            assert_item(item)

    @pytest.mark.asyncio
    async def test_map_by_id(self, client: AsyncClient):
        maps = (await client.get("/maps/")).json()
        if not maps:
            pytest.skip("No maps in DB")
        r = await client.get(f"/maps/{maps[0]['id']}")
        assert r.status_code == 200
        assert_item(r.json())

    @pytest.mark.asyncio
    async def test_map_invalid_id_type(self, client: AsyncClient):
        r = await client.get("/maps/not-an-int")
        assert r.status_code == 422

