from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
import numpy as np
from sqlalchemy.orm import aliased

from src.db.classes import teams
from src.db.session import engine
from src.db.models import Item, MatchResponse
from .matches import get_matches

router = APIRouter(prefix = '/teams',
                   tags = ['teams'])


def get_db_values():
    query = select(teams.name, teams.teamid)
    with engine.connect() as con:
        result = np.array(con.execute(query).fetchall()).T
        return result[0], result[1]

TEAM_NAMES, TEAM_IDS = get_db_values()

@router.get("/", response_model=List[Item])
async def get_teams(
    name: Optional[str] = Query(None, description="Filter by team name")
) -> list[Item]:

    query = select(teams.teamid, teams.name)
    if name:
        if name not in TEAM_NAMES:
            raise HTTPException(status_code=404, detail="Item not found")
        query = query.where(teams.name == name)
    values = []
    keys = ['id', 'name']
    with engine.connect() as con:
        results = np.array(con.execute(query).fetchall())
        for result in results:
            values.append(dict(zip(keys,list(result))))
    return values

@router.get("/{teamid}")
async def get_team_name(teamid) -> Item:
    if teamid not in TEAM_IDS:
        raise HTTPException(status_code=404, detail="Item not found")
    statement = select(teams.name).where(teams.teamid == teamid)
    value = {'id': int(teamid)}
    with engine.connect() as con:
        result = np.array(con.execute(statement).fetchone()).squeeze()
        value['name'] = str(result)
    return value

@router.get("/{teamid}/matchhistory")
async def get_matchhistory(
    teamid,
    limit: Optional[int] = Query(5, description="Limit number of entries"),
    offset: Optional[int] = Query(0, description="Limit number of entries")
) -> list[MatchResponse]:
    if teamid not in TEAM_IDS:
        raise HTTPException(status_code=404, detail="Item not found")
    return get_matches(teamid=teamid,offset = offset, limit = limit)
