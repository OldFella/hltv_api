from src.domain.errors import NotFoundError
from typing import TypeVar
from src.domain.ports import ReadPort, RankingsPort
from src.domain.models import Ranking

T = TypeVar('T')

# --- Sides ---

def get_all(port: ReadPort[T]) -> list[T]:
    return port.get_all()

def get_one(id: int, port: ReadPort[T]) -> T:
    one = port.get_one(id)
    if not one:
        raise NotFoundError(f"Item {id}")
    return one

def get_rankings(port: RankingsPort) -> Ranking:
    ...

