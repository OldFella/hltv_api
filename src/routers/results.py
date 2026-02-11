import sys
sys.path.append('../')
from db.classes import teams, sides, maps, matches, match_overview
from db.session import engine 
from db.models import item, matchhistory
from fastapi import APIRouter, HTTPException
from sqlalchemy import select, and_
from sqlalchemy.sql.expression import func
import numpy as np
from sqlalchemy.orm import aliased

router = APIRouter(prefix="/results")

@router.get("/latest")
async def read_item() -> list[matchhistory]:
    side = 'total'
    map = 'All'
   # get_latest_date = select(func.max(match_overview.date))
    get_sideid = select(sides.sideid).where(sides.name == side)
    get_mapid = select(maps.mapid).where(maps.name == map)

    with engine.connect() as con:
        #latest_date = np.array(con.execute(get_latest_date).fetchone()).item()
        sideid = np.array(con.execute(get_sideid).fetchone()).item()
        mapid = np.array(con.execute(get_mapid).fetchone()).item()

        m1 = aliased(matches)
        m2 = aliased(matches)
        get_matchhistory = select(m1.matchid,
                                  m1.teamid,
                                m1.score,
                                m2.score,
                                m2.teamid,
                                match_overview.date,
                                match_overview.event).distinct().join(m2,
                                                and_(m1.matchid == m2.matchid,
                                                    m1.teamid != m2.teamid))
        get_matchhistory = get_matchhistory.join(match_overview, m1.matchid == match_overview.matchid)
        get_matchhistory = get_matchhistory.where(and_(m1.sideid == m2.sideid, m1.mapid == m2.mapid))
        get_matchhistory = get_matchhistory.where(and_(m1.sideid == sideid, m1.mapid == mapid))
       # get_matchhistory = get_matchhistory.where(match_overview.date == latest_date)
        get_matchhistory= get_matchhistory.order_by(match_overview.date.desc()).limit(20)
        matchhistory = np.array(con.execute(get_matchhistory).fetchall())
    
        result = []
        matchids = []
        for m in matchhistory:
            if m[0] in matchids:
                continue
            matchids.append(m[0])
            get_teamname = select(teams.name).where(teams.teamid == m[1])
            team_name = np.array(con.execute(get_teamname).fetchone()).item()
            get_vsname = select(teams.name).where(teams.teamid == m[4])
            vs_name = np.array(con.execute(get_vsname).fetchone()).item()
            match = {'matchid':m[0],
                     'map': map,
                     'side':side,
                     'team':team_name,
                     'score':m[2],
                     'opponent':vs_name,
                     'score_opponent':m[3],
                     'date': m[5],
                     'event': m[6]}
            
            result.append(match)
    return result
