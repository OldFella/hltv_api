from src.domain.errors import NotFoundError
from typing import TypeVar, Literal
from src.domain.ports import ReadPort, RankingsPort, CountsPort, PlayersPort, TeamsPort, MatchPort
from src.domain.models import (
    Ranking, Item, CountResponse,
    PlayerDetail, PlayerStatRow,
    PlayerGroupedStats, PlayerAggregatedStats,
    TeamDetail, TeamMapStats, MatchResult,
    MatchupProbabilities, MatchPlayerStats
)
from src.utils.stats import strength_maps, strength_ranking, bradley_terry

from datetime import date

import numpy as np

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
    port: PlayersPort | TeamsPort,
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


def get_raw_stats(
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
    return port.get_raw_stats(mapid, sideid, limit, offset)


def get_raw_stats_by_outcome(
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
    return port.get_raw_stats_by_outcome(outcome, mapid, limit, offset)


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

def get_aggregated_stats(
    port: PlayersPort,
    mapid: int | None,
    sideid: int | None,
    start_date: date | None,
    end_date: date | None,
    limit: int,
    offset: int,
    min_played: int,
) -> list[PlayerAggregatedStats]:
    return port.get_aggregated_stats(mapid, sideid, start_date, end_date, limit, offset, min_played)

def get_team(
    port: TeamsPort, 
    teamid:int, 
    start_date: date,
    end_date: date,
    ) -> TeamDetail:
    result = port.get_one(teamid = teamid, start_date = start_date, end_date = end_date)
    if not result:
        raise NotFoundError(f"Team {teamid}")
    return result

def get_team_matchhistory(
    port: TeamsPort,
    teamid: int,
    limit: int,
    offset: int,
    ) -> list[MatchResult]:
    return port.get_matchhistory(teamid = teamid, limit = limit, offset = offset)

def get_team_stats(
    port: TeamsPort,
    teamid: int,
    start_date: date,
    end_date: date,
    ) -> list[TeamMapStats]:
    return port.get_stats(teamid, start_date, end_date)

# --- Matches ---

def get_all_matches(
    port: MatchPort,
    offset: int,
    limit: int,
    ):
    return port.get_all(offset, limit)

def get_match(
    port: MatchPort,
    matchid: int,
    ):
    match = port.get_one(matchid)
    if not match:
        raise NotFoundError(f"Match {matchid}")
    return match

def get_match_player_stats(
    port: MatchPort,
    matchid: int,
    by_map: bool,
    ) -> list[MatchPlayerStats]:
    return port.get_player_stats(matchid, by_map)

# --- predict ---

def get_map_win_probs(
    teams_port: TeamsPort,
    rankings_port: RankingsPort,
    team_id_a: int,
    team_id_b: int,
    start_date: date | None = None,
    end_date: date | None = None,
    use_rankings: bool = True,
) -> MatchupProbabilities:
    stats_a = teams_port.get_stats(team_id_a, start_date, end_date)
    stats_b = teams_port.get_stats(team_id_b, start_date, end_date)
    rankings = rankings_port.get_rankings()

    if not stats_a:
        raise NotFoundError(f"Team {team_id_a}")
    if not stats_b:
        raise NotFoundError(f"Team {team_id_b}")

    # compute map_win_probs here
    stats_b_lookup = {s.id: s for s in stats_b}

    map_win_probs = []

    for map_a in stats_a:
        map_b = stats_b_lookup.get(map_a.id)
        if map_b is None:
            continue
        
        strengths = [0,0]
        for i,m in enumerate([map_a, map_b]):
            n_wins = np.array([m.n_wins])
            n = np.array([m.n])
            strength = strength_maps(n_wins, n)[0]
            strengths[i] = strength

        map_win_probs.append(bradley_terry(strengths[0], strengths[1])) 


    rankings_lookup = {r.id: r.points for r in rankings.rankings}
    points_a = rankings_lookup.get(team_id_a)
    points_b = rankings_lookup.get(team_id_b)

    ranking_win_prob = bradley_terry(strength_ranking(points_a), strength_ranking(points_b))

    return MatchupProbabilities(
        map_win_probs = map_win_probs,
        ranking_win_prob = ranking_win_prob
    )
