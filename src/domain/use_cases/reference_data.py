from src.domain.errors import NotFoundError
from typing import TypeVar
from src.domain.ports import ReadPort, RankingsPort, CountsPort
from src.domain.models import Ranking, Item, CountResponse

from datetime import date

T = TypeVar('T')

def get_all(port: ReadPort[T]) -> list[T]:
    return port.get_all()

def get_one(port: ReadPort[T], id: int, label: str) -> T:
    one = port.get_one(id)
    if not one:
        raise NotFoundError(f"{label} {id}")
    return one

def get_rankings(port: RankingsPort, date:date) -> Ranking:
    ranking = port.get_rankings(date)
    if not ranking:
        raise NotFoundError(f"Ranking for the {date}")
    return ranking

def get_counts(port: CountsPort) -> CountResponse:
    return port.get_counts()