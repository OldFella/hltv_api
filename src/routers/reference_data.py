from fastapi import APIRouter, Depends
from sqlalchemy.engine import Connection
from src.domain.models import Item, Ranking, Fantasy, CountResponse
from src.domain.use_cases.reference_data import get_one, get_all, get_rankings, get_counts
from src.db.get_db import get_db
from src.adapters.sqlalchemy_reference_data import(
     get_side_adapter, get_map_adapter,
    SqlAlchemyRankingsAdapter,
    SqlAlchemyFantasyAdapter,
    SqlAlchemyCountsAdapter
)
from typing import Callable, TypeVar
from datetime import date

T = TypeVar('T')

def make_read_router(
    prefix: str, 
    tag: str, 
    get_adapter: Callable, 
    list_model: Callable = Item, 
    detail_model: Callable = Item
    ) -> APIRouter:

    router = APIRouter(prefix=prefix, tags=[tag])

    @router.get(
        "/",
        response_model=list[list_model],
        summary=f"List {tag}",
        description=f"Returns all {tag} with their names and unique IDs."
    )
    def list_all(connection: Connection = Depends(get_db)):
        return get_all(get_adapter(connection))

    @router.get(
        "/{id}",
        response_model=detail_model,
        summary=f"Get {tag} by ID",
        description=f"Returns a specific {tag} by its unique ID. \n- **id**: unique {tag} ID"
    )
    def get_by_id(id: int, connection: Connection = Depends(get_db)):
        return get_one(get_adapter(connection), id, label = tag[:-1])

    return router


sides_router = make_read_router("/sides", "sides", get_side_adapter)
maps_router = make_read_router("/maps", "maps", get_map_adapter)
fantasy_router = make_read_router(
    "/fantasy", 
    "fantasy", 
    SqlAlchemyFantasyAdapter, 
    detail_model = Fantasy
    )

rankings_router = APIRouter(prefix = '/rankings',
                   tags = ['rankings'])

@rankings_router.get("/", response_model=Ranking, summary="Get Most Recent VRS Ranking")
def list_rankings(date:date|None= None, connection: Connection = Depends(get_db)) -> Ranking:
    adapter = SqlAlchemyRankingsAdapter(connection)
    return get_rankings(adapter, date)


counts_router = APIRouter(prefix = '/counts',
                   tags = ['counts'])

@counts_router.get("/", response_model=CountResponse, summary="Record Counts")
def list_counts(connection: Connection = Depends(get_db)) -> CountResponse:
    adapter = SqlAlchemyCountsAdapter(connection)
    return get_counts(adapter)