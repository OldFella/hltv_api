from typing import Protocol, TypeVar, Literal
from src.domain.models import (
    Ranking, CountResponse,
    PlayerDetail, PlayerStatRow,
    PlayerGroupedStats, Item,
    PlayerAggregatedStats,
    TeamDetail, MatchResult,
    TeamMapStats, MatchPlayerStats
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

    def get_aggregated_stats(
        self,
        mapid: int | None,
        sideid: int | None,
        start_date: int | None,
        end_date: int | None,
        limit: int,
        offset: int,
        min_played: int,
    ) -> list[PlayerAggregatedStats]: ...

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

class TeamsPort(Protocol):
    def get_all_fuzzy(
        self,
        name: str | None,
        limit: int,
        offset: int,
    ) -> list[Item]: ...

    def get_one(
        self,
        teamid: int,
        start_date: date,
        end_date: date,
    ) -> TeamDetail | None: ...


    def get_matchhistory(
        self,
        teamid: int,
        limit: int,
        offset: int,
    ) -> list[MatchResult]: ...

    def get_stats(
        self,
        teamid: int,
        start_date: date,
        end_date: date,
        ) -> list[TeamMapStats]: ...
 

class MatchPort(Protocol):
    def get_all(self, offset:int, limit:int) -> list[MatchResult]:...
    def get_one(self, matchid: int) -> MatchResult:...
    def get_player_stats(self, matchid: int, by_map: bool)-> MatchPlayerStats:...
