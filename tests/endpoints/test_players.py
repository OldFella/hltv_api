import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from src.main import app
from tests.endpoints.schemas import assert_item, assert_player_response, assert_player_stats, assert_grouped_stats

class TestPlayersEndpoints:

    @pytest.mark.asyncio
    async def test_list_players_default(self, client: AsyncClient):
        r = await client.get("/players/")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) <= 20
        for player in data:
            assert_item(player)

    @pytest.mark.asyncio
    async def test_list_players_name_filter(self, client: AsyncClient):
        r = await client.get("/players/", params={"name": "zywoo"})
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    @pytest.mark.asyncio
    async def test_player_stats_default(self, client: AsyncClient):
        r = await client.get("/players/stats/raw")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) <= 20
        for row in data:
            assert_player_stats(row)

    @pytest.mark.asyncio
    async def test_player_stats_filter_by_map(self, client: AsyncClient):
        maps = (await client.get("/maps/")).json()
        if not maps:
            pytest.skip("No maps in DB")
        r = await client.get("/players/stats", params={"mapid": maps[0]["id"]})
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    @pytest.mark.asyncio
    async def test_player_stats_filter_by_side(self, client: AsyncClient):
        sides = (await client.get("/sides/")).json()
        if not sides:
            pytest.skip("No sides in DB")
        r = await client.get("/players/stats", params={"sideid": sides[0]["id"]})
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    @pytest.mark.asyncio
    async def test_player_stats_overall(self, client: AsyncClient):
        """sideid=0 and mapid=0 should return overall stats (the defaults)."""
        r = await client.get("/players/stats/raw", params={"mapid": 0, "sideid": 0})
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_player_by_id(self, client: AsyncClient):
        players = (await client.get("/players/")).json()
        if not players:
            pytest.skip("No players in DB")
        player_id = players[0]["id"]
        r = await client.get(f"/players/{player_id}")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == player_id
        assert_player_response(data)

    @pytest.mark.asyncio
    async def test_player_by_id_with_date_range(self, client: AsyncClient):
        players = (await client.get("/players/")).json()
        if not players:
            pytest.skip("No players in DB")
        player_id = players[0]["id"]
        r = await client.get(
            f"/players/{player_id}",
            params={"start_date": "2025-12-10", "end_date": "2026-01-31"},
        )
        assert r.status_code == 200
        assert_player_response(r.json())

    @pytest.mark.asyncio
    async def test_player_invalid_id_type(self, client: AsyncClient):
        r = await client.get("/players/not-an-int")
        assert r.status_code == 422

    @pytest.mark.asyncio
    @pytest.mark.parametrize("group", ["maps", "sides", "events"])
    async def test_player_grouped_stats(self, client: AsyncClient, group: str):
        players = (await client.get("/players/")).json()
        if not players:
            pytest.skip("No players in DB")
        player_id = players[0]["id"]
        r = await client.get(f"/players/{player_id}/stats/{group}")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        for row in data:
            assert_grouped_stats(row)

    @pytest.mark.asyncio
    async def test_player_grouped_stats_invalid_group(self, client: AsyncClient):
        """Only maps/sides/events are valid — anything else should 422."""
        players = (await client.get("/players/")).json()
        if not players:
            pytest.skip("No players in DB")
        player_id = players[0]["id"]
        r = await client.get(f"/players/{player_id}/stats/invalid_group")
        assert r.status_code == 422

    @pytest.mark.asyncio
    async def test_player_sides_stats_with_mapid(self, client: AsyncClient):
        """mapid filter is applicable when group is sides or events."""
        players = (await client.get("/players/")).json()
        # Use a real map (skip mapid=0 which is the Overall row, has no side data)
        maps = [m for m in (await client.get("/maps/")).json() if m["id"] != 0]
        if not players or not maps:
            pytest.skip("Insufficient data")
        player_id = players[0]["id"]
        r = await client.get(
            f"/players/{player_id}/stats/sides",
            params={"mapid": maps[0]["id"]},
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)
