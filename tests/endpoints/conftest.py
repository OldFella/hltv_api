import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from pathlib import Path

from src.main import app

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

@pytest.fixture(autouse=True)
def create_last_updated_file(tmp_path, monkeypatch):
    f = Path("last_updated.txt")
    f.write_text("2024-01-01")
    yield
    f.unlink(missing_ok=True)