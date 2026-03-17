from typing import Optional
from fastapi import APIRouter, Query, Depends
from src.db.get_db import get_db
from src.domain.models import(
    MatchResult,
    MatchPlayerStats,
)
from sqlalchemy.engine import Connection

from src.domain.use_cases import (
    get_all_matches,
    get_match,
    get_match_player_stats,
)
from src.adapters.sqlalchemy_matches import SqlAlchemyMatchesAdapter

router = APIRouter(prefix = '/matches',
                   tags = ['matches'])



@router.get("/", response_model=list[MatchResult], summary="List matches")
def list_all_matches(
    limit: Optional[int] = Query(100, description="Limit number of entries"),
    offset: Optional[int] = Query(0, description="Limit number of entries"),
    connection: Connection = Depends(get_db),
    ) -> list[MatchResult]:
    """
    Returns a paginated list of all professional CS matches.

    - **limit**: number of results to return (default 100)
    - **offset**: pagination offset (default 0)
    """
    adapter = SqlAlchemyMatchesAdapter(connection)
    m = get_all_matches(adapter, offset, limit)
    return m

@router.get("/latest", response_model=list[MatchResult], summary="Latest match results")
def get_latest_matches(
    limit: Optional[int] = Query(10, description="Limit number of entries"),
    offset: Optional[int] = Query(0, description="Limit number of entries"),
    connection: Connection = Depends(get_db),
    ) -> list[MatchResult]:
    """
    Returns the most recent professional CS match results.
    - **limit**: number of results to return (default 10)
    - **offset**: pagination offset (default 0)
    """
    adapter = SqlAlchemyMatchesAdapter(connection)
    return get_all_matches(adapter, offset, limit)


@router.get("/{matchid}", response_model=MatchResult, summary="Match details")
def get_match_results(matchid:int, connection: Connection = Depends(get_db)) -> MatchResult:
    """
    Returns detailed results for a specific match including map scores and winner.

    - **matchid**: unique match ID
    """
    adapter = SqlAlchemyMatchesAdapter(connection)

    return get_match(adapter, matchid)


@router.get("/{matchid}/stats", summary="Match player stats")
def get_match_stats(
    matchid: int,
    by_map: bool = Query(False, description="Break down stats per map"),
    connection: Connection = Depends(get_db),
)->list[MatchPlayerStats]:
    """
    Returns player stats for both teams in a specific match.

    - **matchid**: unique match ID
    - **by_map**: if true, returns stats broken down per map
    """
    adapter = SqlAlchemyMatchesAdapter(connection)

    return get_match_player_stats(adapter, matchid, by_map)