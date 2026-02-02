import sys
sys.path.append('../')
from db.classes import matches
from db.session import engine 
from db.models import match
from fastapi import APIRouter
from sqlalchemy import select


router = APIRouter(prefix = '/matches',
                   tags = ['matches'])





@router.get("/all")
async def read_item()->list[match]:
    return match_handler()

@router.get("/{matchid}")
async def read_item(matchid,teamid = None, sideid = None, mapid = None)->list[match]:
    return match_handler(matchid, teamid, sideid, mapid)


def match_handler(matchid = None,teamid = None, sideid = None, mapid = None):
    statement = select(matches)
    if matchid != None:
        statement = statement.where(matches.matchid == matchid)

    if teamid != None:
        statement = statement.where(matches.teamid == teamid)

    if sideid != None:
        statement = statement.where(matches.sideid == sideid)

    if mapid != None:
        statement = statement.where(matches.mapid == mapid) 
    result = []
    keys = ['matchid', 'teamid', 'mapid', 'sideid', 'score', 'date']
    with engine.connect() as con:

        query = con.execute(statement).all()
        for q in query:
            result.append(dict(zip(keys, list(q))))
    
    return result

