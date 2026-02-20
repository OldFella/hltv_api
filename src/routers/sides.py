from src.db.classes import sides
from fastapi import APIRouter
from sqlalchemy import select
from src.db.models import Item

from src.repositories.base import execute_query


router = APIRouter(prefix = '/sides',
                   tags = ['sides'])


@router.get("/")
async def get_sides()->list[Item]:
    stmnt = select(sides.sideid.label('id'),sides.name.label('name'))
    rows = execute_query(stmnt)
    return [{'id':r['id'], 'name':r['name']} for r in rows]



@router.get("/{sideid}")
async def get_side_name(sideid)->Item:
    stmnt = select(sides.name.label('name')).where(sides.sideid == sideid)

    row = execute_query(stmnt, many=False)
  
    return {'id': sideid, 'name': row['name']}