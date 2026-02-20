from src.db.classes import maps
from fastapi import APIRouter
from sqlalchemy import select
from src.db.models import Item

from src.repositories.base import execute_query

router = APIRouter(prefix = '/maps',
                   tags = ['map'])



@router.get("/")
async def get_maps()->list[Item]:
    stmnt = select(maps.mapid.label('id'), maps.name.label('name')).order_by(maps.mapid)

    rows = execute_query(stmnt)
        
    return [{'id':r['id'], 'name':r['name']} for r in rows]


@router.get("/{mapid}")
async def get_map_name(mapid: int)->Item:
    stmnt = select(maps.name.label('name')).where(maps.mapid == mapid)
    
    row = execute_query(stmnt, many=False)

    return {'id': mapid, 'name' : row['name']}