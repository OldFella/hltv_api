from datetime import date
from typing import Optional, Literal
from fastapi import APIRouter, Query, Depends
from sqlalchemy.engine import Connection

from src.db.get_db import get_db
from src.domain.models import Item, PlayerDetail, PlayerStatRow, PlayerGroupedStats
from src.domain.use_cases import (
    get_all_fuzzy,
    get_player,
    get_player_stats,
    get_player_stats_by_outcome,
    get_player_grouped_stats,
)
from src.adapters.sqlalchemy_players import SqlAlchemyPlayersAdapter
from dateutil.relativedelta import relativedelta

router = APIRouter(prefix='/players', tags=['players'])

def default_date_range() -> tuple[date, date]:
    return date.today() - relativedelta(months=3), date.today()


@router.get("/", response_model=list[Item], summary="List players")
async def list_players(
    name: Optional[str] = Query(None, description="Filter by player name (fuzzy match)"),
    limit: Optional[int] = Query(20, description="Max results to return"),
    offset: Optional[int] = Query(0, description="Pagination offset"),
    connection: Connection = Depends(get_db),
) -> list[Item]:
    adapter = SqlAlchemyPlayersAdapter(connection)
    return get_all_fuzzy(adapter, name, limit, offset)


@router.get("/stats", response_model=list[PlayerStatRow], summary="All player stats")
async def list_player_stats(
    mapid: Optional[int] = Query(0, description="Map ID. 0 for overall match stats."),
    sideid: Optional[int] = Query(0, description="Side ID. 0 for both sides."),
    limit: Optional[int] = Query(20, description="Max results to return"),
    offset: Optional[int] = Query(0, description="Pagination offset"),
    connection: Connection = Depends(get_db),
) -> list[PlayerStatRow]:
    adapter = SqlAlchemyPlayersAdapter(connection)
    return get_player_stats(adapter, mapid, sideid, limit, offset)


@router.get("/stats/{outcome}", response_model=list[PlayerStatRow], summary="Player stats by outcome")
async def list_player_stats_by_outcome(
    outcome: Literal["win", "lose"],
    mapid: Optional[int] = Query(0, description="Map ID. 0 for overall match stats."),
    limit: Optional[int] = Query(100, description="Max results to return"),
    offset: Optional[int] = Query(0, description="Pagination offset"),
    connection: Connection = Depends(get_db),
) -> list[PlayerStatRow]:
    adapter = SqlAlchemyPlayersAdapter(connection)
    return get_player_stats_by_outcome(adapter, outcome, None if mapid == -1 else mapid, limit, offset)


@router.get("/{playerid}", response_model=PlayerDetail, summary="Player details")
async def get_player_info(
    playerid: int,
    start_date: Optional[date] = Query(None, description="Start date for stats filter (default: 3 months ago)"),
    end_date: Optional[date] = Query(None, description="End date for stats filter (default: today)"),
    connection: Connection = Depends(get_db),
) -> PlayerDetail:
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
    start, end = start_date or default_date_range()[0], end_date or default_date_range()[1]
    adapter = SqlAlchemyPlayersAdapter(connection)
    return get_player_grouped_stats(adapter, playerid, group, mapid, start, end)