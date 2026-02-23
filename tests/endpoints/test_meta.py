import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from src.main import app
from tests.endpoints.conftest import *


class TestMetaEndpoints:

    @pytest.mark.asyncio
    async def test_status(self, client: AsyncClient):
        r = await client.get("/status")
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_homepage(self, client: AsyncClient):
        r = await client.get("/")
        assert r.status_code == 200
