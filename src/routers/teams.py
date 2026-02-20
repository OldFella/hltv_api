from typing import Optional
from fastapi import APIRouter, Query
from sqlalchemy import select

from src.db.classes import teams
from src.db.models import Item, MatchResponse

from src.repositories.match_repository import format_matches, build_match_query
from src.repositories.base import execute_query, add_fuzzy_filter

router = APIRouter(prefix = '/teams',
                   tags = ['teams'])



# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/", response_model=list[Item])
async def get_teams(
    name: Optional[str] = Query(None, description="Filter by team name"),
    limit: Optional[int] = Query(20, description="Limit number of entries"),
    offset: Optional[int] = Query(0, description="Limit number of entries")
    ) -> list[Item]:

    filters, order_bys = [],[]

    add_fuzzy_filter(teams.name, name, filters, order_bys)

    stmnt = (
        select(teams.teamid.label('id'), teams.name.label('name'))
        .where(*filters)
        .offset(offset)
        .limit(limit)
        .order_by(*order_bys)
    )
    rows = execute_query(stmnt)
    return [{'id': r['id'], 'name': r['name']} for r in rows]

@router.get("/{teamid}")
async def get_team_name(teamid:int) -> Item:
    stmnt = select(teams.teamid.label('id'), teams.name.label('name')).where(teams.teamid == teamid)
    row = execute_query(stmnt, many=False)
    return {'id': row['id'], 'name': row['name']}

@router.get("/{teamid}/matchhistory")
async def get_matchhistory(
    teamid: int,
    limit: Optional[int] = Query(5, description="Limit number of entries"),
    offset: Optional[int] = Query(0, description="Limit number of entries")
) -> list[MatchResponse]:

    stmnt = build_match_query(teamid = teamid, limit = limit, offset = offset)

    rows = execute_query(stmnt)

    return format_matches(rows)
