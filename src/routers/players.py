from src.db.classes import players, matches, sides, maps, match_overview, player_stats
from src.db.session import engine 
from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from sqlalchemy import select, func
from src.db.models import Item, PlayerStats, PlayerAverageStats
import numpy as np
from sqlalchemy.orm import aliased



router = APIRouter(prefix = '/players',
                   tags = ['players'])


entries = ['k', 'd', 'swing', 'adr', 'kast', 'rating']


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
    event: Optional[str] = Query(None, description="Filter by team name")
    )-> PlayerAverageStats:

    stmnt = get_player_stats_query(
            playerid=playerid,
            mapid=None, 
            sideid=0, 
            matchid=None,
            event=event
            )
    with engine.connect() as con:
        row = con.execute(stmnt).mappings().all()
        if len(row) == 0:
            raise HTTPException(status_code=404, detail="Item not found")
        
        row = dict(row[0])

    
    for entry in entries:
            row[entry] = round(row[entry], 3)
    
    

    return {
            'id': row['player_id'],
            'name': row['player_name'],
            'k': row['k'],
            'd': row['d'],
            'swing': row['swing'],
            'adr': row['adr'],
            'kast': row['kast'],
            'rating': row['rating'],
            'maps_played': row['n']
        }

@router.get("/{playerid}/stats/maps")
async def get_player_stats_maps(
    playerid
    ):

    stmnt = get_player_stats_query(
            playerid=playerid,
            mapid=None, 
            sideid=0, 
            matchid=None,
            group_by = ['maps']
            )
    with engine.connect() as con:
        rows = con.execute(stmnt).mappings().all()
    
    results = []
    for row in rows:
        row = dict(row)
        for entry in entries:
            row[entry] = round(row[entry], 3)
        results.append({
            'id': row['map_id'],
            'name': row['map_name'],
            'k': row['k'],
            'd': row['d'],
            'swing': row['swing'],
            'adr': row['adr'],
            'kast': row['kast'],
            'rating': row['rating'],
            'maps_played': row['n']
        })
    return results

@router.get("/{playerid}/stats/sides")
async def get_player_stats_sides(
    playerid
    ):

    stmnt = get_player_stats_query(
            playerid=playerid,
            mapid=None, 
            sideid=None, 
            matchid=None,
            group_by = ['sides']
            )
    with engine.connect() as con:
        rows = con.execute(stmnt).mappings().all()
    

    
    results = []
    for row in rows:
        row = dict(row)
        for entry in entries:
            row[entry] = round(row[entry], 3)
        results.append({
            'id': row['side_id'],
            'name': row['side_name'],
            'k': row['k'],
            'd': row['d'],
            'swing': row['swing'],
            'adr': row['adr'],
            'kast': row['kast'],
            'rating': row['rating'],
            'maps_played': row['n']
        })
    return results


def get_player_stats_query(
    playerid,
    mapid = None,
    sideid = None,
    matchid = None,
    event = None,
    group_by = None
    ) -> list[PlayerStats]:

    ps = aliased(player_stats)

    filters = [ps.playerid == playerid]
    order_bys = []

    if mapid is not None:
        filters.append(ps.mapid == mapid)
    else:
        filters.append(ps.mapid != 0)
    
    if sideid is not None:
        filters.append(ps.sideid == sideid)
    else:
        filters.append(ps.sideid != 0)
    
    if matchid is not None:
        filters.append(ps.matchid == matchid)
    
    if event:
        similarity = func.similarity(match_overview.event, event)
        filters.append(similarity > 0.3)
        order_bys.append(similarity.desc())
    
    selects =[
        ps.playerid.label('player_id'),
        players.name.label('player_name'),
        func.coalesce(func.avg(ps.k), 0).label("k"),
        func.coalesce(func.avg(ps.d), 0).label("d"),
        func.coalesce(func.avg(ps.roundswing), 0).label("swing"),
        func.coalesce(func.avg(ps.adr), 0).label("adr"),
        func.coalesce(func.avg(ps.kast), 0).label("kast"),
        func.coalesce(func.avg(ps.rating), 0).label("rating"),
        func.count().label('n')
    ]

    group_bys = [ps.playerid, players.name]

    if group_by:
        if  'maps' in group_by:
            selects.extend([
                ps.mapid.label('map_id'),
                maps.name.label('map_name')
                ])
            group_bys.extend([ps.mapid,maps.name])

        if 'sides' in group_by:
            selects.extend([
                ps.sideid.label('side_id'),
                sides.name.label('side_name')
                ])
            group_bys.extend([ps.sideid,sides.name])
        
        if 'events' in group_by:
            selects.extend([
                match_overview.events.label('events')
            ])
            group_bys.extend([match_overview.events])

    
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