from datetime import date
from typing import Optional, Literal
from fastapi import APIRouter, Query, Depends
from sqlalchemy.engine import Connection
from src.db.get_db import get_db
from src.domain.models import Item, PlayerDetail, PlayerStatRow, PlayerGroupedStats, PlayerAggregatedStats
from src.domain.use_cases import (
    get_all_fuzzy,
    get_player,
    get_raw_stats,
    get_raw_stats_by_outcome,
    get_player_grouped_stats,
    get_aggregated_stats,
)
from src.adapters.sqlalchemy_players import SqlAlchemyPlayersAdapter

from src.utils.helpers import default_date_range

router = APIRouter(prefix='/players', tags=['players'])


@router.get("/", response_model=list[Item], summary="List players")
async def list_players(
    name: Optional[str] = Query(None, description="Filter by player name (fuzzy match)"),
    limit: Optional[int] = Query(20, description="Max results to return"),
    offset: Optional[int] = Query(0, description="Pagination offset"),
    connection: Connection = Depends(get_db),
) -> list[Item]:
    """
    Returns a paginated list of all professional CS players.

    - **name**: optionally filter by name using fuzzy matching
    - **limit**: number of results to return (default 20)
    - **offset**: pagination offset (default 0)
    """
    adapter = SqlAlchemyPlayersAdapter(connection)
    return get_all_fuzzy(adapter, name, limit, offset)


@router.get("/stats", response_model=list[PlayerAggregatedStats], summary="Aggregated player stats")
async def list_player_aggregated_stats(
    mapid: Optional[int] = Query(None, description="Map ID. 0 for overall match stats."),
    sideid: Optional[int] = Query(0, description="Side ID. 0 for both sides."),
    start_date: Optional[date] = Query(None, description="Start date for stats filter (default: 3 months ago)"),
    end_date: Optional[date] = Query(None, description="End date for stats filter (default: today)"),
    limit: Optional[int] = Query(20, description="Max results to return"),
    offset: Optional[int] = Query(0, description="Pagination offset"),
    min_played: Optional[int] = Query(20, description="Minimum maps played to be included in rankings"),
    connection: Connection = Depends(get_db),
) -> list[PlayerAggregatedStats]:
    """
    Returns aggregated player stats ranked by rating.

    - **mapid**: map ID to filter by, 0 for overall match stats
    - **sideid**: side ID to filter by, 0 for both sides
    - **limit**: number of results to return (default 20)
    - **offset**: pagination offset (default 0)
    - **min_played**: minimum maps played threshold to qualify for rankings (default 20)
    """
    start, end = start_date or default_date_range()[0], end_date or default_date_range()[1]
    adapter = SqlAlchemyPlayersAdapter(connection)
    return get_aggregated_stats(adapter, mapid, sideid, start, end, limit, offset, min_played)

@router.get("/stats/raw", response_model=list[PlayerStatRow], summary="All player stats")
async def list_player_stats(
    mapid: Optional[int] = Query(0, description="Map ID. 0 for overall match stats."),
    sideid: Optional[int] = Query(0, description="Side ID. 0 for both sides."),
    limit: Optional[int] = Query(20, description="Max results to return"),
    offset: Optional[int] = Query(0, description="Pagination offset"),
    connection: Connection = Depends(get_db),
) -> list[PlayerStatRow]:
    """
    Returns a paginated log of raw player stats, one row per player per match.

    - **mapid**: map ID to filter by, 0 for overall match stats
    - **sideid**: side ID to filter by, 0 for both sides
    - **limit**: number of results to return (default 20)
    - **offset**: pagination offset (default 0)
    """
    adapter = SqlAlchemyPlayersAdapter(connection)
    return get_raw_stats(adapter, mapid, sideid, limit, offset)


@router.get("/stats/raw/{outcome}", response_model=list[PlayerStatRow], summary="Player stats by outcome")
async def list_player_stats_by_outcome(
    outcome: Literal["win", "lose"],
    mapid: Optional[int] = Query(0, description="Map ID. 0 for overall match stats."),
    limit: Optional[int] = Query(100, description="Max results to return"),
    offset: Optional[int] = Query(0, description="Pagination offset"),
    connection: Connection = Depends(get_db),
) -> list[PlayerStatRow]:
    """
    Returns a paginated log of raw player stats filtered by match outcome.

    - **outcome**: `win` or `lose`
    - **mapid**: map ID to filter by, 0 for overall match stats
    - **limit**: number of results to return (default 100)
    - **offset**: pagination offset (default 0)
    """
    adapter = SqlAlchemyPlayersAdapter(connection)
    return get_raw_stats_by_outcome(adapter, outcome, None if mapid == -1 else mapid, limit, offset)


@router.get("/{playerid}", response_model=PlayerDetail, summary="Player details")
async def get_player_info(
    playerid: int,
    start_date: Optional[date] = Query(None, description="Start date for stats filter (default: 3 months ago)"),
    end_date: Optional[date] = Query(None, description="End date for stats filter (default: today)"),
    connection: Connection = Depends(get_db),
) -> PlayerDetail:
    """
    Returns detailed information for a specific player including their current
    team and aggregated stats over the given date range (default: last 3 months).

    - **playerid**: unique player ID
    - **start_date**: start of the stats window (default: 3 months ago)
    - **end_date**: end of the stats window (default: today)
    """
    start, end = start_date or default_date_range()[0], end_date or default_date_range()[1]
    adapter = SqlAlchemyPlayersAdapter(connection)
    return get_player(adapter, playerid, start, end)


@router.get("/{playerid}/stats/{group}", response_model=list[PlayerGroupedStats], summary="Player stats by group")
async def get_player_grouped_stats_route(
    playerid: int,
    group: Literal["maps", "sides", "events"],
    mapid: Optional[int] = Query(None, description="Filter by map ID. Only applicable when group is `sides` or `events`."),
    start_date: Optional[date] = Query(None, description="Start date for stats filter (default: 3 months ago)"),
    end_date: Optional[date] = Query(None, description="End date for stats filter (default: today)"),
    connection: Connection = Depends(get_db),
) -> list[PlayerGroupedStats]:
    """
    Returns a player's aggregated stats grouped by map, side, or event.

    - **playerid**: unique player ID
    - **group**: grouping dimension — one of `maps`, `sides`, or `events`
    - **mapid**: filter by map ID; only applies when group is `sides` or `events`
    - **start_date**: start of the stats window (default: 3 months ago)
    - **end_date**: end of the stats window (default: today)
    """
    start, end = start_date or default_date_range()[0], end_date or default_date_range()[1]
    adapter = SqlAlchemyPlayersAdapter(connection)
    return get_player_grouped_stats(adapter, playerid, group, mapid, start, end)