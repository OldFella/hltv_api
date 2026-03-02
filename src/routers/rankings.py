from src.db.classes import rankings, teams
from fastapi import APIRouter
from sqlalchemy import select, func
from src.repositories.base import execute_query
from src.db.models import Item, Ranking
from sqlalchemy.orm import aliased

router = APIRouter(prefix = '/rankings',
                   tags = ['rankings'])


@router.get("/", response_model=Ranking, summary="Get Most Recent VRS Ranking")
async def get_rankings() -> Ranking:
    stmnt = (
        select(
            rankings.teamid.label('id'),
            teams.name.label('name'),
            func.rank().over(order_by=rankings.points.desc()).label('rank'),
            rankings.points.label('points'),
            rankings.date.label('date')
        )
        .join(teams, teams.teamid == rankings.teamid)
        .where(rankings.date == select(func.max(rankings.date)).scalar_subquery())
        .order_by(rankings.points.desc())
    )

    rows = execute_query(stmnt)

    return {
        'date': rows[0]['date'],
        'rankings': rows
    }