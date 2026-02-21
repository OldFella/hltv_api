from typing import Optional
from fastapi import APIRouter, Query
from src.db.models import MatchResponse
from src.repositories.base import execute_query
from src.repositories.match_repository import (
    build_match_query, format_matches, 
    build_match_stats_query, 
    format_match_stats
)
router = APIRouter(prefix = '/matches',
                   tags = ['matches'])



def get_matches(limit, offset):
    stmnt = build_match_query(limit = limit, offset = offset)

    rows = execute_query(stmnt)

    return format_matches(rows)

@router.get("/", response_model=list[MatchResponse], summary="List matches")
async def get_all_matches(
    limit: Optional[int] = Query(100, description="Limit number of entries"),
    offset: Optional[int] = Query(0, description="Limit number of entries")
    ) -> list[MatchResponse]:
    """
    Returns a paginated list of all professional CS matches.

    - **limit**: number of results to return (default 100)
    - **offset**: pagination offset (default 0)
    """
    return get_matches(limit = limit, offset = offset)

@router.get("/latest", response_model=list[MatchResponse], summary="Latest match results")
async def get_latest_matches(
    limit: Optional[int] = Query(10, description="Limit number of entries"),
    offset: Optional[int] = Query(0, description="Limit number of entries")
    ) -> list[MatchResponse]:
    """
    Returns the most recent professional CS match results.
    - **limit**: number of results to return (default 10)
    - **offset**: pagination offset (default 0)
    """

    return get_matches(limit=limit, offset=offset)

@router.get("/{matchid}", response_model=MatchResponse, summary="Match details")
async def get_match_results(matchid:int) -> MatchResponse:
    """
    Returns detailed results for a specific match including map scores and winner.

    - **matchid**: unique match ID
    """

    stmnt = build_match_query(matchid = matchid)

    rows = execute_query(stmnt)

    return format_matches(rows)[0]


@router.get("/{matchid}/stats", summary="Match player stats")
async def get_match_stats(
    matchid: int,
    by_map: bool = Query(False, description="Break down stats per map")
):
    """
    Returns player stats for both teams in a specific match.

    - **matchid**: unique match ID
    - **by_map**: if true, returns stats broken down per map
    """
    stmnt = build_match_stats_query(matchid=matchid, by_map=by_map)
    rows = execute_query(stmnt)

    return format_match_stats(rows, by_map=by_map)