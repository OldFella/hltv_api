from fastapi import APIRouter
from sqlalchemy import select, func, distinct
from src.db.classes import players, match_overview, teams
from src.db.models import Item
from src.repositories.base import execute_query

router = APIRouter(prefix='/counts', tags=['counts'])


@router.get("/", summary="counts")
async def get_counts():
    """
    Returns all available CS maps with their names and unique IDs.
    """

    result = {'players': 0, 'teams': 0, 'matches': 0}

    count_players = select(func.count(distinct(players.playerid)).label('count'))
    count_teams = select(func.count(teams.teamid).label('count'))
    count_matches = select(func.count(match_overview.matchid).label('count'))

    queries = [('players',count_players), ('teams', count_teams), ('matches', count_matches)]

    for key, q in queries:
        value = execute_query(q, many = False)
        result[key] = value['count']
    return result
