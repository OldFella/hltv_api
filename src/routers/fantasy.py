from src.db.classes import fantasies, fantasy_overview, players, teams
from fastapi import APIRouter
from sqlalchemy import select
from src.repositories.base import execute_query
from src.db.models import Item, FantasyResponse
from sqlalchemy.orm import aliased

router = APIRouter(prefix = '/fantasy',
                   tags = ['fantasy'])

# --- CONSTANTS ---

SALARY_CAP = 1e3
CURRENCY = '$'

# --- ROUTERS ---

@router.get("/", response_model=list[Item], summary="List fantasies")
async def get_fantasies() -> list[Item]:
    """
    Returns all available HLTV fantasies with their names and unique IDs.
    """
    fo = aliased(fantasy_overview)
    stmnt = (
        select(
            fo.fantasyid.label('id'),
            fo.name.label('name')
            )
            .order_by(fo.fantasyid.label('id').desc())
    )
    rows = execute_query(stmnt)
    return [{'id': row['id'], 'name': row['name']} for row in rows]

@router.get("/{fantasyid}", response_model=FantasyResponse, summary="Fantasy details")
async def get_fantasy(fantasyid: int) -> FantasyResponse:
    """
    Returns a specific fantasy by its unique ID.

    - **fantasyid**: unique fantasy ID
    """
    fo = aliased(fantasy_overview)
    f = aliased(fantasies)
    stmnt = (
        select(
            fo.fantasyid.label('id'),
            fo.name.label('name')
        )
        .where(fo.fantasyid == fantasyid)
    )
    row = execute_query(stmnt, many=False)

    stmnt_player = (
        select(
            f.playerid.label('player_id'),
            players.name.label('player_name'),
            f.teamid.label('team_id'),
            teams.name.label('team_name'),
            f.cost.label('cost')
        )
        .join(players, players.playerid == f.playerid)
        .join(teams, teams.teamid == f.teamid)
        .where(f.fantasyid == fantasyid)
        .order_by(f.teamid)
    )

    rows_player = execute_query(stmnt_player)

    team = {}
    for p in rows_player:
        tid = p['team_id']
        if tid not in team:
            team[tid] = {'id': tid, 'name': p['team_name'], 'players': []}
        team[tid]['players'] += [{
            'id': p['player_id'],
            'name': p['player_name'],
            'cost': p['cost']
        }]

    return {
        'id': row['id'],
        'name': row['name'],
        'salary_cap': SALARY_CAP,
        'currency': CURRENCY,
        'teams': [v for v in team.values()]
    }



