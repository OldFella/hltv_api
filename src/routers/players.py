from datetime import date
from typing import Optional, Literal

from fastapi import APIRouter, Query
from sqlalchemy import select

from src.db.classes import players
from src.db.models import Item, PlayerAverageStats
from src.repositories.base import add_fuzzy_filter, execute_query
from src.repositories.player_repository import (
    build_player_stats_query,
    default_date_range,
    format_stats,
    FIELDS,
    GROUP_CONFIG,
)

router = APIRouter(prefix = '/players',
                   tags = ['players'])



# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get("/")
async def get_players(
    name: Optional[str] = Query(None, description="Filter by player name"),
    limit: Optional[int] = Query(20, description="Max results to return"),
    offset: Optional[int] = Query(0, description="Pagination offset")
    )->list[Item]:
       
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

@router.get("/stats/")
async def get_player_stats(
    limit: Optional[int] = Query(20, description="Max results to return"),
    offset: Optional[int] = Query(0, description="Pagination offset")
    ):

    start, end = default_date_range()

    stmnt = build_player_stats_query(
            mapid=0, 
            sideid=0, 
            start_date = start,
            end_date = end
            ).offset(offset).limit(limit)


    rows = execute_query(stmnt)

    return format_stats(rows, "players")


@router.get("/{playerid}")
async def get_player(playerid:int)->Item:
    stmnt = select(
        players.name.label('name'),
        players.playerid.label('id')
    ).where(players.playerid == playerid)

    row = execute_query(stmnt, many=False)

    return {"id": row["id"], "name": row["name"]}


@router.get("/{playerid}/stats")
async def get_average_player_stats(
    playerid: int,
    event: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
) -> PlayerAverageStats:
    """
    Returns the average per map performance of the player from the last 3 months
    """

    start, end = start_date or default_date_range()[0], end_date or default_date_range()[1]

    stmnt = build_player_stats_query(
            playerid=playerid,
            sideid=0, 
            event=event,
            start_date=start,
            end_date=end
            )
    
    row = execute_query(stmnt, many=False)
        
    
    return format_stats([row],"players")[0]



@router.get("/{playerid}/stats/{group}")
async def get_player_grouped_stats(
   playerid: int,
    group: Literal["maps", "sides", "events"],
    mapid: Optional[int] = Query(None),
):
    """Player stats aggregated by map, side, or event."""

    stmnt = build_player_stats_query(
        playerid=playerid,
        mapid=mapid, 
        sideid=None if group=='sides' else 0,
        group_by=[group]
    )

    rows = execute_query(stmnt)

    return format_stats(rows, group)