from src.domain.errors import NotFoundError
from typing import TypeVar, Literal
from src.domain.ports import ReadPort, RankingsPort, CountsPort, PlayersPort
from src.domain.models import (
    Ranking, Item, CountResponse,
    PlayerDetail, PlayerStatRow,
    PlayerGroupedStats
)

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

def get_all_fuzzy(
    port: PlayersPort, 
    name: str | None, 
    limit: int, 
    offset: int
) -> list[Item]:
    return port.get_all_fuzzy(name, limit, offset)

def get_player(
    port: PlayersPort, 
    playerid: int, 
    start_date: date, 
    end_date:date
) -> PlayerDetail: 
    player =  port.get_one(playerid, start_date, end_date)
    if not player:
        raise NotFoundError(f"Player {playerid}")
    return player

def get_player_stats(
    port: PlayersPort, 
    mapid: int | None, 
    sideid: int | None, 
    limit: int, 
    offset: int
) -> list[PlayerStatRow]:
    return port.get_player_stats(mapid, sideid, limit, offset)


def get_player_stats_by_outcome(
    port: PlayersPort, 
    outcome: Literal["win", "lose"], 
    mapid: int | None, 
    limit: int, 
    offset: int
) -> list[PlayerStatRow]:
    return port.get_player_stats_by_outcome(outcome, mapid,limit,offset)

def get_player_grouped_stats(
    port: PlayersPort, 
    playerid:int, 
    group: Literal["maps", "sides", "events"], 
    mapid: int | None, 
    start_date:date, 
    end_date:date,
) -> list[PlayerGroupedStats]:
    result = port.get_player_grouped_stats(
        playerid, 
        group, 
        mapid, 
        start_date, 
        end_date
    )
    if not result:
        raise NotFoundError(f"Player {playerid}")
    return result