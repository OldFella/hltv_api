import sys
sys.path.append('../')
from db.classes import teams, sides, maps, matches, match_overview
from db.session import engine 
from db.models import Item, match, MatchResponse, MapResponse
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, and_, or_
import numpy as np
from sqlalchemy.orm import aliased
from typing import List, Optional
from sqlalchemy import func

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
    return get_matches(matchid = matchid, mapid = None)[0]
    


def get_matches(
    matchid = None,
    teamid = None, 
    vsid=None, 
    sideid = 0, 
    mapid = None, 
    limit = 100, 
    offset = 0):


    m1 = aliased(matches)
    m2 = aliased(matches)

    t1 = aliased(teams)
    t2 = aliased(teams)

    

    filters = [
        m1.sideid == sideid,
        m1.mapid == m2.mapid
    ]

    if matchid is not None:
        filters.append(m1.matchid == matchid)
    
    if mapid is not None:
        filters.append(m1.mapid == mapid)
    
    if teamid is not None:
        filters.append(
            m1.teamid == teamid,
        )

        if vsid is not None:
            filters.append(
                m2.teamid == vsid
            )
    else:
        filters.append(m1.teamid < m2.teamid)
            
    
    if sideid != 0:
        filters.append(and_(m2.sideid != sideid, m2.sideid != 0))

    else:
        filters.append(m1.sideid == m2.sideid)



    stmnt = (
        select(
            m1.matchid.label('match_id'),
            m1.teamid.label('team1_id'),
            t1.name.label('team1_name'),
            m2.teamid.label('team2_id'),
            t2.name.label('team2_name'),
            match_overview.date.label('date'),
            match_overview.event.label('event'),
            func.array_agg(
                func.json_build_object(
                'id', maps.mapid,
                'name', maps.name,
                'team1_score', m1.score,
                'team2_score', m2.score
                )
            ).label('maps')
            )
            .join(
                m2,
                and_(
                    m1.matchid == m2.matchid,
                    m1.teamid != m2.teamid
                    )
            )
            .join(t1, m1.teamid == t1.teamid)
            .join(t2, m2.teamid == t2.teamid)
            .join(match_overview, m1.matchid == match_overview.matchid)
            .join(maps, maps.mapid == m1.mapid)
            .group_by(
                m1.matchid, m1.teamid, t1.name,
                m2.teamid, t2.name,
                match_overview.date, match_overview.event
            )
            .where(*filters)
            .order_by(match_overview.date.desc())
            .offset(offset)
            .limit(limit)
    )
    


    with engine.connect() as con:
        rows = con.execute(stmnt).mappings().all()
    result = []
    for row in rows:
        map_list = []
        team1_score = team2_score = None

        for m in row['maps']:
            if m['id'] == 0:
                team1_score = m['team1_score']
                team2_score = m['team2_score']
            else:
                map_list.append(m)

        best_of = (2 * max(team1_score, team2_score)) - 1
        if len(map_list) == 1:
            best_of = 1

        winner = {'id': row['team1_id'],
                 'name': row['team1_name']}
        if team2_score > team1_score:
            winner = {'id': row['team2_id'],
                      'name': row['team2_name']}

        match = {'id':row['match_id'],
                    'maps': map_list,
                    'team1': {'id': row['team1_id'],
                            'name': row['team1_name'],
                            'score': team1_score},
                    'team2': {'id': row['team2_id'],
                            'name': row['team2_name'],
                            'score': team2_score},
                    'best_of': best_of,
                    'date': row['date'],
                    'event': row['event'],
                    'winner': winner}
        result.append(match)
    return result

# def get_maps(matchid):
#     get_maps = (
#         select(
#         maps.name.label('map_name'),
#         matches.mapid.label('map_id')
#         )
#         .distinct()
#         .join(
#             maps,
#             matches.mapid == maps.mapid 
#         )
#         .where(
#             matches.matchid == matchid,
#             maps.mapid != 0
#         )
#         .order_by(matches.mapid)
#     )

#     with engine.connect() as con:
#         rows = con.execute(get_maps).mappings().all()

#         map_list = [{'id':int(r['map_id']),'name':r['map_name']} for r in rows]
#     return map_list

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

