from fastapi import APIRouter
from sqlalchemy import select
from src.db.classes import maps
from src.db.models import Item
from src.repositories.base import execute_query

router = APIRouter(prefix='/maps', tags=['maps'])


@router.get("/", response_model=list[Item], summary="List maps")
async def get_maps() -> list[Item]:
    """
    Returns all available CS maps with their names and unique IDs.
    """
    stmnt = select(maps.mapid.label('id'), maps.name.label('name')).order_by(maps.mapid)
    rows = execute_query(stmnt)
    return [{'id': r['id'], 'name': r['name']} for r in rows]


@router.get("/{mapid}", response_model=Item, summary="Map details")
async def get_map(mapid: int) -> Item:
    """
    Returns a specific map by its unique ID.

    - **mapid**: unique map ID
    """
    stmnt = select(maps.name.label('name')).where(maps.mapid == mapid)
    row = execute_query(stmnt, many=False)
    return {'id': mapid, 'name': row['name']}