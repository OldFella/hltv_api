from src.db.classes import maps
from src.db.session import engine 
from fastapi import APIRouter
from sqlalchemy import select
from src.db.models import Item
import numpy as np

router = APIRouter(prefix = '/maps',
                   tags = ['map'])



@router.get("/")
async def get_maps()->list[Item]:
    statement = select(maps.mapid,maps.name)
    with engine.connect() as con:

        results = np.array(con.execute(statement).fetchall())
        
        value = [{'id':r[0], 'name':r[1]} for r in results]

    return value

@router.get("/{mapid}")
async def get_map_name(mapid)->Item:
    statement = select(maps.name).where(maps.mapid == mapid)
    value = {'id':mapid}
    with engine.connect() as con:

        results = con.execute(statement).all()
        for res in results:
            value['name'] = res[0]

    return value