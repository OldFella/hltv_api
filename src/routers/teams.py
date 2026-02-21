from typing import Optional
from fastapi import APIRouter, Query
from sqlalchemy import select
from src.db.classes import teams
from src.db.models import Item, MatchResponse, TeamResponse
from src.repositories.match_repository import format_matches, build_match_query, build_roster_query, get_streak
from src.repositories.base import execute_query, add_fuzzy_filter

router = APIRouter(prefix='/teams', tags=['teams'])


@router.get("/", response_model=list[Item], summary="List teams")
async def get_teams(
    name: Optional[str] = Query(None, description="Filter by team name (fuzzy match)"),
    limit: Optional[int] = Query(20, description="Max results to return"),
    offset: Optional[int] = Query(0, description="Pagination offset")
) -> list[Item]:
    """
    Returns a paginated list of all professional CS teams.

    - **name**: optionally filter by name using fuzzy matching
    - **limit**: number of results to return (default 20)
    - **offset**: pagination offset (default 0)
    """
    filters, order_bys = [], []
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


@router.get("/{teamid}", response_model=TeamResponse, summary="Team details")
async def get_team_info(teamid: int) -> TeamResponse:
    """
    Returns detailed information for a specific team including their current
    win/loss streak and most recent roster.

    - **teamid**: unique team ID
    """
    stmnt = select(teams.teamid.label('id'), teams.name.label('name')).where(teams.teamid == teamid)
    row = execute_query(stmnt, many=False)

    history_stmnt = build_match_query(teamid=teamid, limit=20)
    history = format_matches(execute_query(history_stmnt))
    streak = get_streak(history, teamid)

    roster = execute_query(build_roster_query(teamid=teamid))

    return {
        'id': row['id'],
        'name': row['name'],
        'streak': streak,
        'roster': [{'id': r['id'], 'name': r['name']} for r in roster]
    }


@router.get("/{teamid}/matchhistory", response_model=list[MatchResponse], summary="Team match history")
async def get_matchhistory(
    teamid: int,
    limit: Optional[int] = Query(5, description="Max results to return"),
    offset: Optional[int] = Query(0, description="Pagination offset")
) -> list[MatchResponse]:
    """
    Returns the most recent matches played by a specific team.

    - **teamid**: unique team ID
    - **limit**: number of results to return (default 5)
    - **offset**: pagination offset (default 0)
    """
    stmnt = build_match_query(teamid=teamid, limit=limit, offset=offset)
    rows = execute_query(stmnt)
    return format_matches(rows)