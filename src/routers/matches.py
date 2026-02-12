import sys
sys.path.append('../')
from db.classes import teams, sides, maps, matches, match_overview
from db.session import engine 
from db.models import Item, match, MatchResponse, MapResponse
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, and_
import numpy as np
from sqlalchemy.orm import aliased
from typing import List, Optional

import numpy as np

router = APIRouter(prefix = '/matches',
                   tags = ['matches'])



@router.get("/")
async def get_matches(limit: Optional[int] = Query(100, description="Limit number of entries"),
                    offset: Optional[int] = Query(0, description="Limit number of entries")) -> list[MatchResponse]:
    return get_matches(limit = limit, offset = offset)

@router.get("/{matchid}")
async def get_match_results(matchid) -> MatchResponse:
    return get_matches(matchid = matchid)[0]

@router.get("/{matchid}/maps")
async def get_map_results(matchid)-> MapResponse:
    m = get_matches(matchid = matchid)[0]
    maps = m['maps']
    result = m
    result.pop('maps')
    map_list = []
    for map in maps:
        if map['id'] == 0:
            continue
        r = get_matches(matchid, team= None, sideid = 0, mapid = map['id'])[0]
        map_dict = {
            'id':map['id'],
            'name':map['name'],
            'team1_score': r['team1']['score'],
            'team2_score': r['team2']['score']
        }
        map_list.append(map_dict)
    result['maps'] = map_list
    result['best_of']= best_of
    return result


def get_matches(matchid = None, team = None,vs=None ,sideid = 0, mapid = 0, limit = 100, offset = 0):
    with engine.connect() as con:
        m1 = aliased(matches)
        m2 = aliased(matches)
        get_matchhistory = select(m1.matchid,
                                m1.teamid,
                                m1.score,
                                m2.teamid,
                                m2.score,
                                match_overview.date,
                                match_overview.event).join(m2,
                                                and_(m1.matchid == m2.matchid,
                                                    m1.teamid != m2.teamid))
        if matchid != None:
            get_matchhistory = get_matchhistory.where(m1.matchid == matchid)
        get_matchhistory = get_matchhistory.join(match_overview, m1.matchid == match_overview.matchid)
        get_matchhistory = get_matchhistory.where(m1.sideid == sideid)
        
        if sideid != 0:
            get_matchhistory = get_matchhistory.where(and_(m2.sideid != sideid, m2.sideid != 0))
        else:
            get_matchhistory = get_matchhistory.where(m1.sideid == m2.sideid)
        get_matchhistory = get_matchhistory.where(m1.mapid == mapid)
        get_matchhistory = get_matchhistory.where(m1.mapid == m2.mapid)
        get_matchhistory = get_matchhistory.where(m1.teamid < m2.teamid)
        get_matchhistory= get_matchhistory.order_by(match_overview.date.desc())
        get_matchhistory = get_matchhistory.offset(offset).limit(limit)
        matchhistory = np.array(con.execute(get_matchhistory).fetchall())
        result = []
        for m in matchhistory:
            best_of = (2 * max(m[2], m[4])) - 1
            match = {'id':m[0],
                     'maps': get_maps(m[0]),
                     'team1': {'id': m[1],
                               'name': get_name(m[1]),
                               'score':m[2]},
                     'team2': {'id': m[3],
                               'name': get_name(m[3]),
                               'score':m[4]},
                     'best_of': best_of,
                     'date': m[5],
                     'event': m[6]}
            winner = match['team1']
            if m[4] > m[2]:
                winner = match['team2']
            match['winner'] = {
                'id': winner['id'],
                'name':winner['name']
                }
            result.append(match)
    return result

def get_name(teamid):
    get_name = select(teams.name).where(teams.teamid == teamid)
    with engine.connect() as con:
        name = np.array(con.execute(get_name).fetchone()).item()
    return name

def get_maps(matchid):
    get_maps = select(
        maps.name,
        matches.mapid
        ).distinct().join(
            maps,
            matches.mapid == maps.mapid 
            ).where(
                matches.matchid == matchid
                ).order_by(matches.mapid)

    with engine.connect() as con:
        rows = np.array(con.execute(get_maps).fetchall())

        map_list = [{'id':int(r[1]),'name':r[0]} for r in rows]
    return map_list

def match_handler(matchid = None,teamid = None, sideid = None, mapid = None):
    statement = select(
        matches.matchid,
        matches.teamid,
        matches.mapid,
        matches.sideid,
        matches.score,
        match_overview.date,
        match_overview.event
        )
    statement = statement.join(match_overview, matches.matchid == match_overview.matchid)
    if matchid != None:
        statement = statement.where(matches.matchid == matchid)

    if teamid != None:
        statement = statement.where(matches.teamid == teamid)

    if sideid != None:
        statement = statement.where(matches.sideid == sideid)

    if mapid != None:
        statement = statement.where(matches.mapid == mapid)
    statement = statement.limit(100)
    statement = statement.order_by(match_overview.date.desc())
    result = []
    keys = ['matchid', 'teamid', 'mapid', 'sideid', 'score', 'date', 'event']
    with engine.connect() as con:

        query = con.execute(statement).all()
        for q in query:
            result.append(dict(zip(keys, list(q))))
    
    return result

