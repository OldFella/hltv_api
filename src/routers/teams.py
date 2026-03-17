from fastapi import APIRouter, Query, Depends
from datetime import date
from sqlalchemy.engine import Connection
from src.db.get_db import get_db
from src.domain import use_cases
from src.domain.models import Item, TeamDetail, MatchResult, TeamMapStats
from src.adapters.sqlalchemy_teams import SqlAlchemyTeamsAdapter

from src.utils.helpers import default_date_range


router = APIRouter(prefix='/teams', tags=['teams'])

@router.get("/", response_model=list[Item])
def get_teams(
    name: str | None = Query(None),
    limit: int = Query(20),
    offset: int = Query(0),
    conn: Connection = Depends(get_db)
) -> list[Item]:
    port = SqlAlchemyTeamsAdapter(conn)
    return use_cases.get_all_fuzzy(port, name, limit, offset)

@router.get("/{teamid}", response_model=TeamDetail)
def get_team(
    teamid: int,
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    conn: Connection = Depends(get_db)
) -> TeamDetail:
    start, end = start_date or default_date_range()[0], end_date or default_date_range()[1]
    port = SqlAlchemyTeamsAdapter(conn)
    return use_cases.get_team(port, teamid, start, end)

@router.get("/{teamid}/matchhistory", response_model=list[MatchResult])
def get_matchhistory(
    teamid: int,
    limit: int = Query(5),
    offset: int = Query(0),
    conn: Connection = Depends(get_db)
) -> list[MatchResult]:
    port = SqlAlchemyTeamsAdapter(conn)
    return use_cases.get_team_matchhistory(port, teamid, limit, offset)

@router.get("/{teamid}/stats", response_model=list[TeamMapStats])
def get_team_stats(
    teamid: int,
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    conn: Connection = Depends(get_db)
) -> list[TeamMapStats]:
    start, end = start_date or default_date_range()[0], end_date or default_date_range()[1]
    port = SqlAlchemyTeamsAdapter(conn)
    return use_cases.get_team_stats(port, teamid, start, end)