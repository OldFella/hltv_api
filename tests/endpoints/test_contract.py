import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from src.main import app

class TestAPIContract:

    @pytest.mark.asyncio
    @pytest.mark.parametrize("path", [
        "/sides/",
        "/maps/",
        "/matches/",
        "/matches/latest",
        "/teams/",
        "/players/",
        "/players/stats",
        "/fantasy/",
    ])
    async def test_returns_json_content_type(self, client: AsyncClient, path: str):
        r = await client.get(path)
        assert r.status_code == 200
        assert "application/json" in r.headers["content-type"]

    @pytest.mark.asyncio
    async def test_unknown_route_is_404(self, client: AsyncClient):
        r = await client.get("/nonexistent/route")
        assert r.status_code == 404

    @pytest.mark.asyncio
    @pytest.mark.parametrize("path", [
        "/teams/",
        "/matches/",
        "/players/",
        "/fantasy/",
    ])
    async def test_post_not_allowed(self, client: AsyncClient, path: str):
        """All endpoints are GET-only — POST must return 405."""
        r = await client.post(path)
        assert r.status_code == 405