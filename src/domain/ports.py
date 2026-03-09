from typing import Protocol, TypeVar
from src.domain.models import Ranking, CountResponse
from datetime import date

T = TypeVar('T')

class ReadPort(Protocol[T]):
    def get_all(self) -> list[T]: ...
    def get_one(self, id:int) -> T | None: ...

class RankingsPort(Protocol):
    def get_rankings(self, date: date | None = None) -> Ranking | None: ...

class CountsPort(Protocol):
    def get_counts(self) -> CountResponse: ...

