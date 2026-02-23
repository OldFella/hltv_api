import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from src.main import app
from tests.endpoints.schemas import assert_match_response, assert_match_stats

class TestMatchesEndpoints:

    @pytest.mark.asyncio
    async def test_list_matches_default(self, client: AsyncClient):
        r = await client.get("/matches/")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) <= 100           # default limit
        for match in data:
            assert_match_response(match)

    @pytest.mark.asyncio
    async def test_list_matches_limit(self, client: AsyncClient):
        r = await client.get("/matches/", params={"limit": 5})
        assert r.status_code == 200
        assert len(r.json()) <= 5

    @pytest.mark.asyncio
    async def test_list_matches_pagination(self, client: AsyncClient):
        page1 = (await client.get("/matches/", params={"limit": 5, "offset": 0})).json()
        page2 = (await client.get("/matches/", params={"limit": 5, "offset": 5})).json()
        if len(page1) == 5 and len(page2) > 0:
            ids1 = {m["id"] for m in page1}
            ids2 = {m["id"] for m in page2}
            assert ids1.isdisjoint(ids2), "Paginated pages must not overlap"

    @pytest.mark.asyncio
    async def test_latest_matches_default_limit(self, client: AsyncClient):
        r = await client.get("/matches/latest")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) <= 10            # default limit is 10
        for match in data:
            assert_match_response(match)

    @pytest.mark.asyncio
    async def test_latest_matches_custom_limit(self, client: AsyncClient):
        r = await client.get("/matches/latest", params={"limit": 3})
        assert r.status_code == 200
        assert len(r.json()) <= 3

    @pytest.mark.asyncio
    async def test_match_by_id(self, client: AsyncClient):
        latest = (await client.get("/matches/latest")).json()
        if not latest:
            pytest.skip("No matches in DB")
        match_id = latest[0]["id"]
        r = await client.get(f"/matches/{match_id}")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == match_id
        assert_match_response(data)

    @pytest.mark.asyncio
    async def test_match_invalid_id_type(self, client: AsyncClient):
        r = await client.get("/matches/not-an-int")
        assert r.status_code == 422

    @pytest.mark.asyncio
    async def test_match_stats_overall(self, client: AsyncClient):
        latest = (await client.get("/matches/latest")).json()
        if not latest:
            pytest.skip("No matches in DB")
        match_id = latest[0]["id"]
        r = await client.get(f"/matches/{match_id}/stats")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        for entry in data:
            assert_match_stats(entry)

    @pytest.mark.asyncio
    async def test_match_stats_by_map(self, client: AsyncClient):
        latest = (await client.get("/matches/latest")).json()
        if not latest:
            pytest.skip("No matches in DB")
        match_id = latest[0]["id"]
        r = await client.get(f"/matches/{match_id}/stats", params={"by_map": "true"})
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        for entry in data:
            assert_match_stats(entry)

    @pytest.mark.asyncio
    async def test_match_stats_invalid_id_type(self, client: AsyncClient):
        r = await client.get("/matches/not-an-int/stats")
        assert r.status_code == 422

