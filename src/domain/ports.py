from typing import Protocol, TypeVar, Literal
from src.domain.models import (
    Ranking, CountResponse,
    PlayerDetail, PlayerStatRow,
    PlayerGroupedStats, Item

)
from datetime import date

T = TypeVar('T')

class ReadPort(Protocol[T]):
    def get_all(self) -> list[T]: ...
    def get_one(self, id:int) -> T | None: ...

class RankingsPort(Protocol):
    def get_rankings(self, date: date | None = None) -> Ranking | None: ...

class CountsPort(Protocol):
    def get_counts(self) -> CountResponse: ...

class TeamsPort(Protocol):
    def get_all(self): ...
    def get_one(self, id:int): ...
    def get_matchhistory(self): ...
    def get_stats(self): ...

class PlayersPort(Protocol):
    def get_all_fuzzy(
        self,
        name: str | None,
        limit: int,
        offset: int,
    ) -> list[Item]: ...

    def get_one(
        self,
        playerid: int,
        start_date: date,
        end_date: date,
    ) -> PlayerDetail | None: ...

    def get_raw_stats(
        self,
        mapid: int | None,
        sideid: int | None,
        limit: int,
        offset: int,
    ) -> list[PlayerStatRow]: ...

    def get_raw_stats_by_outcome(
        self,
        outcome: Literal["win", "lose"],
        mapid: int | None,
        limit: int,
        offset: int,
    ) -> list[PlayerStatRow]: ...

    def get_grouped_stats(
        self,
        playerid: int,
        group: Literal["maps", "sides", "events"],
        mapid: int | None,
        start_date: date,
        end_date: date,
    ) -> list[PlayerGroupedStats]: ...