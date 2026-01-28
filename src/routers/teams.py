from ..db.classes import teams, sides, maps, matches
from ..db.session import engine 
from ..db.models import item, matchhistory
from fastapi import APIRouter, HTTPException
from sqlalchemy import select, and_
import numpy as np
from sqlalchemy.orm import aliased

router = APIRouter(prefix = '/teams',
                   tags = ['teams'])


def get_db_values():
    query = select(teams.name, teams.teamid)
    with engine.connect() as con:
        result = np.array(con.execute(query).fetchall()).T
        return result[0], result[1]

TEAM_NAMES, TEAM_IDS = get_db_values()

@router.get("/id/{teamid}")
async def read_item(teamid) -> item:
    if teamid not in TEAM_IDS:
        raise HTTPException(status_code=404, detail="Item not found")
    statement = select(teams.name).where(teams.teamid == teamid)
    value = {'id': int(teamid)}
    with engine.connect() as con:
        result = np.array(con.execute(statement).fetchone()).squeeze()
        value['name'] = str(result)
    return value

@router.get("/name/{team}")
async def read_item(team)->item:
    if team not in TEAM_NAMES:
        raise HTTPException(status_code=404, detail="Item not found")
    statement = select(teams.teamid).where(teams.name == team)
    value = {}
    with engine.connect() as con:
        result = np.array(con.execute(statement).fetchone()).squeeze()
        value['id']= str(result)
    value['name'] = team
    return value


@router.get("/matchhistory/{team}")
async def read_item(team, vs = None ,side = 'total', map = 'All') -> list[matchhistory]:
    get_teamid = select(teams.teamid).where(teams.name == team)
    get_sideid = select(sides.sideid).where(sides.name == side)
    get_mapid = select(maps.mapid).where(maps.name == map)

    with engine.connect() as con:
        teamid = np.array(con.execute(get_teamid).fetchone()).item()
        sideid = np.array(con.execute(get_sideid).fetchone()).item()
        mapid = np.array(con.execute(get_mapid).fetchone()).item()

        m1 = aliased(matches)
        m2 = aliased(matches)
        get_matchhistory = select(m1.matchid,
                                m1.score,
                                m2.score,
                                m2.teamid,
                                m1.date).join(m2,
                                                and_(m1.matchid == m2.matchid, 
                                                     m1.teamid != m2.teamid)).where(m1.teamid == teamid)
        get_matchhistory = get_matchhistory.where(and_(m1.sideid == m2.sideid, m1.mapid == m2.mapid))
        get_matchhistory = get_matchhistory.where(and_(m1.sideid == sideid, m1.mapid == mapid))
        if vs != None:
            get_vsid = select(teams.teamid).where(teams.name == vs)
            vsid = np.array(con.execute(get_vsid).fetchone()).item()
            get_vsid
            get_matchhistory = get_matchhistory.where(m2.teamid == vsid)
        get_matchhistory= get_matchhistory.order_by(m1.date.desc())
        matchhistory = np.array(con.execute(get_matchhistory).fetchall())
    
        result = []
        for m in matchhistory:
            match = {'matchid':m[0],
                     'map': map,
                     'side':side,
                     'team':team,
                     'score':m[1],
                     'opponent':vs,
                     'score_opponent':m[2],
                     'date': m[4]}
            if vs == None:
                get_vsname = select(teams.name).where(teams.teamid == m[3])
                vs_name = np.array(con.execute(get_vsname).fetchone()).item()
                match['opponent'] = vs_name
            result.append(match)
    return result