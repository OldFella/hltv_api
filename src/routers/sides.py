from fastapi import APIRouter, Depends
from sqlalchemy.engine import Connection
from src.domain.models import Side
from src.domain.use_cases.reference_data import get_one, get_all
from src.db.get_db import get_db
from src.adapters.sqlalchemy_reference_data import get_side_adapter

router = APIRouter(prefix='/sides', tags=['sides'])


@router.get("/", response_model=list[Side], summary="List sides")
def list_sides(connection: Connection = Depends(get_db)) -> list[Side]:
    """
    Returns all available sides (T/CT) with their names and unique IDs.
    """
    adapter = get_side_adapter(connection)
    return get_all(adapter)
       

@router.get("/{sideid}", response_model=Side, summary="Side details")
def list_side(
    sideid: int,
    connection: Connection = Depends(get_db)) -> Side:
    """
    Returns a specific side by its unique ID.

    - **sideid**: unique side ID
    """
    adapter = get_side_adapter(connection)
    return get_one(sideid, adapter)
    