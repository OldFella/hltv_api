from src.db.classes import teams, sides, maps, matches, match_overview
from src.db.session import engine 
from src.db.models import Item, match, MatchResponse, MapResponse

from typing import List, Optional

from fastapi import APIRouter, Query
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import aliased


from src.repositories.base import execute_query
from src.repositories.match_repository import build_match_query, format_matches


router = APIRouter(prefix = '/matches',
                   tags = ['matches'])



@router.get("/")
async def get_matches(
    limit: Optional[int] = Query(100, description="Limit number of entries"),
    offset: Optional[int] = Query(0, description="Limit number of entries")
) -> list[MatchResponse]:

    stmnt = build_match_query(limit = limit, offset = offset)

    rows = execute_query(stmnt)

    return format_matches(rows)

@router.get("/latest")
async def get_latest_matches(
    limit: Optional[int] = Query(10, description="Limit number of entries"),
    offset: Optional[int] = Query(0, description="Limit number of entries")
) -> list[MatchResponse]:

    stmnt = build_match_query(limit = limit, offset = offset)

    rows = execute_query(stmnt)

    return format_matches(rows)

@router.get("/{matchid}")
async def get_match_results(matchid:int) -> MatchResponse:

    stmnt = build_match_query(matchid = matchid)

    rows = execute_query(stmnt)

    return format_matches(rows)[0]

@router.get("/{matchid}/maps")
async def get_map_results(matchid:int)-> MapResponse:
    
    stmnt = build_match_query(matchid = matchid)

    rows = execute_query(stmnt)

    return format_matches(rows)[0]
    