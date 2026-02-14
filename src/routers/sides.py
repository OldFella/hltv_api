from src.db.classes import sides
from src.db.session import engine 
from fastapi import APIRouter
from sqlalchemy import select
from src.db.models import Item
import numpy as np


router = APIRouter(prefix = '/sides',
                   tags = ['sides'])


@router.get("/")
async def get_sides()->list[Item]:
    statement = select(sides.sideid,sides.name)
    with engine.connect() as con:

        results = np.array(con.execute(statement).fetchall())
        
        value = [{'id':r[0], 'name':r[1]} for r in results]

    return value


@router.get("/{sideid}")
async def get_side_name(sideid)->Item:
    statement = select(sides.name).where(sides.sideid == sideid)
    value = {'id':sideid}
    with engine.connect() as con:

        results = con.execute(statement).all()
        for res in results:
            value['name'] = res[0]

    return value