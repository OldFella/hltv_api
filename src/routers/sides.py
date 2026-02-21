from fastapi import APIRouter
from sqlalchemy import select
from src.db.classes import sides
from src.db.models import Item
from src.repositories.base import execute_query

router = APIRouter(prefix='/sides', tags=['sides'])


@router.get("/", response_model=list[Item], summary="List sides")
async def get_sides() -> list[Item]:
    """
    Returns all available sides (T/CT) with their names and unique IDs.
    """
    stmnt = select(sides.sideid.label('id'), sides.name.label('name'))
    rows = execute_query(stmnt)
    return [{'id': r['id'], 'name': r['name']} for r in rows]


@router.get("/{sideid}", response_model=Item, summary="Side details")
async def get_side(sideid: int) -> Item:
    """
    Returns a specific side by its unique ID.

    - **sideid**: unique side ID
    """
    stmnt = select(sides.name.label('name')).where(sides.sideid == sideid)
    row = execute_query(stmnt, many=False)
    return {'id': sideid, 'name': row['name']}