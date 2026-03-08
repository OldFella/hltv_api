from fastapi import APIRouter, Depends
from sqlalchemy.engine import Connection
from src.domain.models import Side, Map
from src.domain.use_cases.reference_data import get_one, get_all
from src.db.get_db import get_db
from src.adapters.sqlalchemy_reference_data import get_side_adapter, get_map_adapter
from typing import Callable, TypeVar

T = TypeVar('T')

def make_read_router(prefix: str, tag: str, model: type, get_adapter: Callable) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=[tag])

    @router.get(
        "/",
        response_model=list[model],
        summary=f"List {tag}",
        description=f"Returns all {tag} with their names and unique IDs."
    )
    def list_all(connection: Connection = Depends(get_db)):
        return get_all(get_adapter(connection))

    @router.get(
        "/{id}",
        response_model=model,
        summary=f"Get {tag} by ID",
        description=f"Returns a specific {tag} by its unique ID. \n- **id**: unique {tag} ID"
    )
    def get_by_id(id: int, connection: Connection = Depends(get_db)):
        return get_one(id, get_adapter(connection))

    return router


sides_router = make_read_router("/sides", "sides", Side, get_side_adapter)
maps_router = make_read_router("/maps", "maps", Map, get_map_adapter)