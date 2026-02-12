import sys
sys.path.append('../')
from db.classes import teams, sides, maps, matches, match_overview
from db.session import engine 
from db.models import Item
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, and_
import numpy as np
from sqlalchemy.orm import aliased
from typing import List, Optional

router = APIRouter(prefix = '/teams',
                   tags = ['teams'])


def get_db_values():
    query = select(teams.name, teams.teamid)
    with engine.connect() as con:
        result = np.array(con.execute(query).fetchall()).T
        return result[0], result[1]

TEAM_NAMES, TEAM_IDS = get_db_values()

@router.get("/", response_model=List[Item])
async def get_teams(name: Optional[str] = Query(None, description="Filter by team name")) -> list[Item]:
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