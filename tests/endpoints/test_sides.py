import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from src.main import app
from tests.endpoints.schemas import assert_item

class TestSidesEndpoints:

    @pytest.mark.asyncio
    async def test_list_sides(self, client: AsyncClient):
        r = await client.get("/sides/")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        for item in data:
            assert_item(item)

    @pytest.mark.asyncio
    async def test_side_by_id(self, client: AsyncClient):
        sides = (await client.get("/sides/")).json()
        if not sides:
            pytest.skip("No sides in DB")
        r = await client.get(f"/sides/{sides[0]['id']}")
        assert r.status_code == 200
        assert_item(r.json())

    @pytest.mark.asyncio
    async def test_side_invalid_id_type(self, client: AsyncClient):
        r = await client.get("/sides/not-an-int")
        assert r.status_code == 422