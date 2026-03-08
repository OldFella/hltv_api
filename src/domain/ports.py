from typing import Protocol, TypeVar
from src.domain.models import Side, Map, Ranking

T = TypeVar('T')

class ReadPort(Protocol[T]):
    def get_all(self) -> list[T]: ...
    def get_one(self, id:int) -> T | None: ...

class RankingsPort(Protocol):
    def get_rankings(self) -> Ranking: ...
