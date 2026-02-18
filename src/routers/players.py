from src.db.classes import players, matches, sides, maps, match_overview, player_stats
from src.db.session import engine 
from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from sqlalchemy import select, func, text
from src.db.models import Item, PlayerStats, PlayerAverageStats
import numpy as np
from sqlalchemy.orm import aliased
from datetime import date
from dateutil.relativedelta import relativedelta
from typing import Literal



router = APIRouter(prefix = '/players',
                   tags = ['players'])


FIELDS = {
    'k': 'k',
    'd': 'd',
    'swing': 'roundswing',
    'adr': 'adr',
    'kast': 'kast',
    'rating': 'rating',
}

GROUP_CONFIG = {
    "maps": {"id": "map_id", "name": "map_name"},
    "sides": {"id": "side_id", "name": "side_name"},
    "events": {"name": "events"} 
}

@router.get("/")
async def get_players(
    name: Optional[str] = Query(None, description="Filter by team name"),
    limit: Optional[int] = Query(20, description="Limit number of entries"),
    offset: Optional[int] = Query(0, description="Limit number of entries")
    )->list[Item]:
       

    filters = []
    order_bys = []
    if name:
        similarity = func.similarity(players.name, name)
        filters.append(similarity > 0.3)
        order_bys.append(similarity.desc())

    statement = (
        select(
            players.playerid.label('id'),
            players.name.label('name')
            )
            .where(*filters)
            .offset(offset)
            .limit(limit)
            .order_by(*order_bys)
    )

    with engine.connect() as con:
        rows = con.execute(statement).mappings().all()
        result = [{'id':r['id'], 'name':r['name']} for r in rows]

    return result


@router.get("/{playerid}")
async def get_player(playerid)->Item:
    statement = select(
        players.name.label('name'),
        players.playerid.label('id')
        ).where(players.playerid == playerid)

    with engine.connect() as con:
        rows = con.execute(statement).mappings().all()
        result = [{'id':r['id'], 'name':r['name']} for r in rows]

    return result[0]

@router.get("/{playerid}/stats")
async def get_average_player_stats(
    playerid,
    event: Optional[str] = Query(
        None,
        description="Filter by team name"
        ),
    startDate: Optional[date] = Query(
        date.today() - relativedelta(months = 3), 
        description="Start date for filtering stats (defaults to 3 months ago)"
        ),
    endDate: Optional[date] = Query(
        date.today(), 
        description="End date for filtering stats (defaults to today)"
        )
    )-> PlayerAverageStats:
    """
    Returns the average per map performance of the player from the last 3 months
    """

    stmnt = get_player_stats_query(
            playerid=playerid,
            mapid=None, 
            sideid=0, 
            matchid=None,
            event=event,
            startDate=startDate,
            endDate=endDate
            )
    
    with engine.connect() as con:
        row = con.execute(stmnt).mappings().all()
    row = row[0] if row else None
    if not row:
        raise HTTPException(status_code=404, detail="Item not found")
    row = dict(row)
        
    
    for key, col in FIELDS.items():
        row[key] = round(row[col], 3)
    

    result = {
        'id': row['player_id'],
        'name': row['player_name'],
        **{key: row[key] for key in FIELDS},
        'maps_played': row['n']
    }
    return result

def format_player_stats(rows, group_fields: dict):
    output = []
    for row in rows:
        row = dict(row)
        for key, col in FIELDS.items():
            row[key] = round(row[col], 3)
        
        group_info = {key: row[col] for key, col in group_fields.items()}

        output.append({
            **group_info,
            **{key: row[key] for key in FIELDS},
            'maps_played': row['n']
        })
    return output

@router.get("/{playerid}/stats/{group}")
async def get_player_grouped_stats(
    playerid: int,
    group: Literal['maps', 'sides', 'events'],
    map_id: Optional[int] = Query(None, description="Filter by map_id"),
    ):
    """
    Retrieve a player's aggregated stats grouped by maps, sides, or events.

    This endpoint returns the average stats for a player, grouped by the specified category.
    For maps and sides, both the ID and name of the group are returned. For events, only
    the event name is returned (events do not have a unique ID).

    Args:
        playerid (int): The unique ID of the player to fetch stats for.
        group (str): The type of grouping to apply. Must be one of:
            - 'maps'   : Group stats by map (includes map_id and map_name)
            - 'sides'  : Group stats by side (includes side_id and side_name)
            - 'events' : Group stats by event (includes only event name)

    Returns:
        list[dict]: A list of grouped stats entries, each containing:
            - group info (id/name or just name for events)
            - k, d, swing, adr, kast, rating: Aggregated stats rounded to 3 decimals
            - maps_played (int): Number of matches counted for the group

    Raises:
        HTTPException: If the `group` parameter is invalid (not 'maps', 'sides', or 'events').
    """
    if group not in GROUP_CONFIG:
        raise HTTPException(
            status_code=400, 
            detail="Invalid group type. Must be 'maps', 'sides', or 'events'."
        )

    group_fields = GROUP_CONFIG[group]

    stmnt = get_player_stats_query(
        playerid=playerid,
        mapid=map_id, 
        sideid=0 if group=='maps' else None,
        matchid=None,
        group_by=[group]
    )

    with engine.connect() as con:
        rows = con.execute(stmnt).mappings().all()

    return format_player_stats(rows, group_fields)


def add_fuzzy_search(col, value, filters, order_bys, threshold = 0.3):
    """
    Adds a fuzzy search filter and ordering for a given column.

    Args:
        col: SQLAlchemy column to search on (e.g., players.name).
        value: The string value to search for.
        filters: List of filters to append to (modified in-place).
        order_bys: List of order_by clauses to append to (modified in-place).
        threshold: Minimum similarity threshold (default 0.3).
    """
    if value:
        similarity = func.similarity(col, value)
        filters.append(similarity > threshold)
        order_bys.append(similarity.desc())

def get_player_stats_query(
    playerid,
    mapid = None,
    sideid = None,
    matchid = None,
    event = None,
    startDate=None,
    endDate=None,
    group_by = None
    ) -> list[PlayerStats]:

    ps = aliased(player_stats)

    filters = [ps.playerid == playerid]
    
    optional_filters = [
        (mapid, ps.mapid, lambda col: col !=0),
        (sideid, ps.sideid, lambda col: col !=0),
        (matchid, ps.matchid, None)
        ]
    
    for value, column, default in optional_filters:
        if value is not None:
            filters.append(column == value)
        elif default:
            filters.append(default(column))

    order_bys = []

    add_fuzzy_search(match_overview.event, event, filters,order_bys)
    
    if startDate and endDate:
        filters.extend([
            match_overview.date >= startDate,
            match_overview.date <= endDate
            ])
    
    agg_cols = FIELDS.values()
    
    selects =[
        ps.playerid.label('player_id'),
        players.name.label('player_name')
    ]+[
        func.coalesce(func.avg(getattr(ps, col)), 0).label(col)
        for col in agg_cols
    ]+[
        func.count().label('n')
    ]

    group_bys = [ps.playerid, players.name]

    group_mapping = {
        'maps': ([ps.mapid.label('map_id'), maps.name.label('map_name')], [ps.mapid, maps.name]),
        'sides': ([ps.sideid.label('side_id'), sides.name.label('side_name')], [ps.sideid, sides.name]),
        'events': ([match_overview.event.label('events')], [match_overview.event])
    }

    if group_by:
        for key in group_by:
            select_cols, group_cols = group_mapping.get(key, ([], []))
            selects.extend(select_cols)
            group_bys.extend(group_cols)
    
    stmnt = (
        select(*selects)
            .join(players, players.playerid == ps.playerid)
            .join(maps, maps.mapid == ps.mapid)
            .join(sides, sides.sideid == ps.sideid)
            .join(match_overview, match_overview.matchid == ps.matchid)
            .where(*filters)
            .group_by(*group_bys)
    )

    return stmnt