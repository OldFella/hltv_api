from datetime import date
from typing import Optional, Literal
from fastapi import APIRouter, Query
from sqlalchemy import select
from src.db.classes import players
from src.db.models import Item, GroupedStats, PlayerResponse
from src.repositories.base import add_fuzzy_filter, execute_query
from src.repositories.player_repository import (
    build_player_stats_query,
    default_date_range,
    format_stats,
    build_team_query
)

router = APIRouter(prefix='/players', tags=['players'])


@router.get("/", response_model=list[Item], summary="List players")
async def get_players(
    name: Optional[str] = Query(None, description="Filter by player name (fuzzy match)"),
    limit: Optional[int] = Query(20, description="Max results to return"),
    offset: Optional[int] = Query(0, description="Pagination offset")
) -> list[Item]:
    """
    Returns a paginated list of all professional CS players.

    - **name**: optionally filter by name using fuzzy matching
    - **limit**: number of results to return (default 20)
    - **offset**: pagination offset (default 0)
    """
    filters, order_bys = [], []
    add_fuzzy_filter(players.name, name, filters, order_bys)
    stmnt = (
        select(players.playerid.label('id'), players.name.label('name'))
        .where(*filters)
        .offset(offset)
        .limit(limit)
        .order_by(*order_bys)
    )
    rows = execute_query(stmnt)
    return [{"id": r["id"], "name": r["name"]} for r in rows]


@router.get("/stats", response_model=list[GroupedStats], summary="All player stats")
async def get_player_stats(
    limit: Optional[int] = Query(20, description="Max results to return"),
    offset: Optional[int] = Query(0, description="Pagination offset")
) -> list[GroupedStats]:
    """
    Returns aggregated stats for all players over the default date range (last 3 months).

    - **limit**: number of results to return (default 20)
    - **offset**: pagination offset (default 0)
    """
    start, end = default_date_range()
    stmnt = build_player_stats_query(
        mapid=0,
        sideid=0,
        start_date=start,
        end_date=end
    ).offset(offset).limit(limit)
    rows = execute_query(stmnt)
    return format_stats(rows, "players")


@router.get("/{playerid}", response_model=PlayerResponse, summary="Player details")
async def get_player_info(
    playerid: int,
    start_date: Optional[date] = Query(None, description="Start date for stats filter (default: 3 months ago)"),
    end_date: Optional[date] = Query(None, description="End date for stats filter (default: today)")
    ) -> PlayerResponse:
    """
    Returns detailed information for a specific player including their current team
    and overall stats over the default date range (last 3 months).

    - **playerid**: unique player ID
    - **start_date**: Start date for stats filter (default: 3 months ago)
    - **end_date**: End date for stats filter (default: today)
    """
    start, end = default_date_range() if (not start_date and not end_date) else (start_date, end_date)

    stmnt_stats = build_player_stats_query(playerid=playerid, sideid=0, start_date= start, end_date=end)
    row_stats = execute_query(stmnt_stats, many=False)
    stats = format_stats([row_stats], "players")[0]

    stmnt_team = build_team_query(playerid)
    team = execute_query(stmnt_team, many=False)

    return {
        'id': stats['id'],
        'name': stats['name'],
        'team': {'id': team['id'], 'name': team['name']},
        'stats': {k: stats[k] for k in ('k', 'd', 'swing', 'adr', 'kast', 'rating', 'maps_played')}
    }


@router.get("/{playerid}/stats/{group}", response_model=list[GroupedStats], summary="Player stats by group")
async def get_player_grouped_stats(
    playerid: int,
    group: Literal["maps", "sides", "events"],
    mapid: Optional[int] = Query(None, description="Filter by map ID")
) -> list[GroupedStats]:
    """
    Returns a player's average stats grouped by map, side, or event.

    - **playerid**: unique player ID
    - **group**: grouping dimension — one of `maps`, `sides`, or `events`
    - **mapid**: optionally filter by a specific map ID
    """
    stmnt = build_player_stats_query(
        playerid=playerid,
        mapid=mapid,
        sideid=None if group == 'sides' else 0,
        group_by=[group]
    )
    rows = execute_query(stmnt)
    return format_stats(rows, group)