from ..db.classes import sides
from ..db.session import engine 
from fastapi import APIRouter
from sqlalchemy import select
from ..db.models import item


router = APIRouter(prefix = '/sides',
                   tags = ['sides'])


@router.get("/{sideid}")
async def read_item(sideid)->item:
    statement = select(sides.name).where(sides.sideid == sideid)
    value = {'id':sideid}
    with engine.connect() as con:

        results = con.execute(statement).all()
        for res in results:
            value['name'] = res[0]

    return value