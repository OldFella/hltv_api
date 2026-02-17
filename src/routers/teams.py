from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select, func
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
    name: Optional[str] = Query(None, description="Filter by team name"),
    limit: Optional[int] = Query(20, description="Limit number of entries"),
    offset: Optional[int] = Query(0, description="Limit number of entries")
    ) -> list[Item]:

    filters = []
    order_bys = []

    if name:
        similarity = func.similarity(teams.name, name)
        filters.append(similarity > 0.3)
        order_bys.append(similarity.desc())

    statement = (
        select(
            teams.teamid.label('id'),
            teams.name.label('name')
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
