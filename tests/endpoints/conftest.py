"""
Root conftest.py for endpoint tests.

Creates a throw-away PostgreSQL database for the test session,
seeds it with minimal fixture rows, overrides the app's engine,
and tears everything down afterwards.

Requirements:
  - A running local Postgres instance
  - A database named `csapi_test` (or set TEST_DATABASE_URL in .env.test)
  - pg_trgm extension enabled on that database:
      CREATE EXTENSION IF NOT EXISTS pg_trgm;
"""

import os
import pytest
import pytest_asyncio
from pathlib import Path
from sqlalchemy import create_engine, text
from httpx import AsyncClient, ASGITransport

# ---------------------------------------------------------------------------
# Test DB URL — reads from env, falls back to local default
# ---------------------------------------------------------------------------

def _build_db_url() -> str:
    user     = os.environ.get("POSTGRES_USER",     "postgres")
    password = os.environ.get("POSTGRES_PASSWORD", "postgres")
    server   = os.environ.get("POSTGRES_SERVER",   "localhost")
    port     = os.environ.get("POSTGRES_PORT",     "5432")
    db       = os.environ.get("POSTGRES_DB",       "csapi_test")
    return f"postgresql://{user}:{password}@{server}:{port}/{db}"

TEST_DATABASE_URL = _build_db_url()

# ---------------------------------------------------------------------------
# Override the app's engine BEFORE importing the app
# ---------------------------------------------------------------------------

import src.db.session as _session_module
_test_engine = create_engine(TEST_DATABASE_URL)
_session_module.engine = _test_engine

from src.main import app
from src.db.base_class import Base
from src.db.classes import (
    teams, players, maps, sides,
    matches, match_overview, player_stats, rankings
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ps(matchid, playerid, teamid, mapid, sideid, k, d, swing, adr, kast, rating):
    """Build a full player_stats row, mirroring ek/eadr/ekast = k/adr/kast."""
    return {
        "matchid": matchid, "playerid": playerid, "teamid": teamid,
        "mapid": mapid, "sideid": sideid,
        "k": k, "d": d, "ek": k, "ed": d,
        "roundswing": swing,
        "adr": adr,  "eadr": adr,
        "kast": kast, "ekast": kast,
        "rating": rating,
    }


# ---------------------------------------------------------------------------
# Schema + seed — session-scoped so it runs once per pytest session
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create schema, seed fixture data, yield, then drop everything."""

    Base.metadata.create_all(bind=_test_engine)

    with _test_engine.begin() as con:
        # Enable pg_trgm (idempotent)
        con.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))

        # --- Teams ---
        con.execute(teams.__table__.insert().values([
            {"teamid": 1, "name": "Vitality"},
            {"teamid": 2, "name": "FURIA"},
        ]))

        # --- Players ---
        con.execute(players.__table__.insert().values([
            {"playerid": 1, "name": "zywoo"},
            {"playerid": 2, "name": "apex"},
            {"playerid": 3, "name": "arT"},
            {"playerid": 4, "name": "yuurih"},
        ]))

        # --- Maps ---
        con.execute(maps.__table__.insert().values([
            {"mapid": 0, "name": "Overall"},
            {"mapid": 1, "name": "Mirage"},
            {"mapid": 2, "name": "Inferno"},
        ]))

        # --- Sides ---
        con.execute(sides.__table__.insert().values([
            {"sideid": 0, "name": "Both"},
            {"sideid": 1, "name": "CT"},
            {"sideid": 2, "name": "T"},
        ]))

        # --- Match overview ---
        con.execute(match_overview.__table__.insert().values([
            {"matchid": 1, "date": "2026-01-01", "event": "Test Event"},
        ]))

        # --- Matches ---
        # mapid=0 sideid=0 = overall score row (used by format_matches)
        # per-map rows needed for by_map stats and outcome subquery
        con.execute(matches.__table__.insert().values([
            {"matchid": 1, "teamid": 1, "mapid": 0, "sideid": 0, "score": 2},
            {"matchid": 1, "teamid": 2, "mapid": 0, "sideid": 0, "score": 1},
            {"matchid": 1, "teamid": 1, "mapid": 1, "sideid": 0, "score": 13},
            {"matchid": 1, "teamid": 2, "mapid": 1, "sideid": 0, "score": 8},
            {"matchid": 1, "teamid": 1, "mapid": 2, "sideid": 0, "score": 16},
            {"matchid": 1, "teamid": 2, "mapid": 2, "sideid": 0, "score": 14},
        ]))

        # --- Player stats ---
        # Overall rows (mapid=0, sideid=0) — used by /players/{id} and /players/stats
        # Per-map rows (mapid=1, sideid=0) — used by /matches/{id}/stats?by_map=true
        con.execute(player_stats.__table__.insert().values([
            _ps(1, 1, 1, 0, 0, 25, 14, 11.0, 95.0, 80.0, 1.50),  # zywoo overall
            _ps(1, 2, 1, 0, 0, 18, 15,  3.0, 72.0, 75.0, 1.10),  # apex overall
            _ps(1, 3, 2, 0, 0, 20, 18,  2.0, 78.0, 70.0, 1.05),  # arT overall
            _ps(1, 4, 2, 0, 0, 17, 16,  1.0, 68.0, 72.0, 1.00),  # yuurih overall
            _ps(1, 1, 1, 1, 0, 22, 12, 10.0, 98.0, 82.0, 1.55),  # zywoo Mirage
            _ps(1, 2, 1, 1, 0, 16, 14,  2.0, 70.0, 74.0, 1.08),  # apex Mirage
            _ps(1, 3, 2, 1, 0, 15, 18, -3.0, 65.0, 68.0, 0.90),  # arT Mirage
            _ps(1, 4, 2, 1, 0, 14, 17, -3.0, 62.0, 66.0, 0.88),  # yuurih Mirage
        ]))

        # --- Rankings ---
        con.execute(rankings.__table__.insert().values([
            {"teamid": 1, "points": 1000, "date": "2026-01-01"},
            {"teamid": 2, "points": 850,  "date": "2026-01-01"},
        ]))

    yield

    Base.metadata.drop_all(bind=_test_engine)


# ---------------------------------------------------------------------------
# HTTP client — function-scoped
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def create_last_updated_file():
    f = Path("last_updated.txt")
    f.write_text("2024-01-01")
    yield
    f.unlink(missing_ok=True)