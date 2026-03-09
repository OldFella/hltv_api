from src.domain.errors import NotFoundError
from typing import TypeVar, Literal
from src.domain.ports import ReadPort, RankingsPort, CountsPort, PlayersPort
from src.domain.models import (
    Ranking, Item, CountResponse,
    PlayerDetail, PlayerStatRow,
    PlayerGroupedStats,
)
from datetime import date

T = TypeVar('T')


def get_all(port: ReadPort[T]) -> list[T]:
    """Return all items from the given read port."""
    return port.get_all()


def get_one(port: ReadPort[T], id: int, label: str) -> T:
    """
    Return a single item by ID.
    Raises NotFoundError if the adapter returns None.
    """
    one = port.get_one(id)
    if not one:
        raise NotFoundError(f"{label} {id}")
    return one


def get_rankings(port: RankingsPort, date: date) -> Ranking:
    """
    Return the rankings snapshot for the given date.
    Defaults to the most recent snapshot when date is None.
    Raises NotFoundError if no snapshot exists.
    """
    ranking = port.get_rankings(date)
    if not ranking:
        raise NotFoundError(f"Ranking for {date}")
    return ranking


def get_counts(port: CountsPort) -> CountResponse:
    """Return distinct counts of players, teams, and matches in the database."""
    return port.get_counts()


def get_all_fuzzy(
    port: PlayersPort,
    name: str | None,
    limit: int,
    offset: int,
) -> list[Item]:
    """
    Return a paginated list of players.
    When name is provided, results are filtered and ordered by fuzzy name similarity.
    """
    return port.get_all_fuzzy(name, limit, offset)


def get_player(
    port: PlayersPort,
    playerid: int,
    start_date: date,
    end_date: date,
) -> PlayerDetail:
    """
    Return aggregated stats and current team for a single player.
    Raises NotFoundError if the player has no stats in the given date range.
    """
    player = port.get_one(playerid, start_date, end_date)
    if not player:
        raise NotFoundError(f"Player {playerid}")
    return player


def get_player_stats(
    port: PlayersPort,
    mapid: int | None,
    sideid: int | None,
    limit: int,
    offset: int,
) -> list[PlayerStatRow]:
    """
    Return a paginated log of raw per-player per-match stat rows.
    Pass mapid=0 or sideid=0 for overall stats; None excludes the id=0 summary rows.
    """
    return port.get_stats(mapid, sideid, limit, offset)


def get_player_stats_by_outcome(
    port: PlayersPort,
    outcome: Literal["win", "lose"],
    mapid: int | None,
    limit: int,
    offset: int,
) -> list[PlayerStatRow]:
    """
    Return a paginated log of raw stat rows filtered by match outcome.
    Outcome is derived at query time by comparing scores across teams.
    """
    return port.get_stats_by_outcome(outcome, mapid, limit, offset)


def get_player_grouped_stats(
    port: PlayersPort,
    playerid: int,
    group: Literal["maps", "sides", "events"],
    mapid: int | None,
    start_date: date,
    end_date: date,
) -> list[PlayerGroupedStats]:
    """
    Return a player's stats aggregated by the given dimension (maps, sides, or events).
    Raises NotFoundError if no stats are found for the player in the given date range.
    """
    result = port.get_grouped_stats(playerid, group, mapid, start_date, end_date)
    if not result:
        raise NotFoundError(f"Player {playerid}")
    return result