"""
Schema validators for endpoint tests.
Each function mirrors an OpenAPI component schema exactly.

Usage:
    from tests.endpoints.schemas import assert_item, assert_team_response, ...
"""


def assert_item(obj: dict):
    """{ id: int, name: str }"""
    assert isinstance(obj["id"], int)
    assert isinstance(obj["name"], str)


def assert_team_score(obj: dict):
    """{ id: int, name: str, score: int , rank: int}"""
    assert isinstance(obj["id"], int)
    assert isinstance(obj["name"], str)
    assert isinstance(obj["score"], int)
    assert isinstance(obj["rank"], int)


def assert_team_response(obj: dict):
    """{ id: int, name: str, streak: int, roster: Item[] }"""
    assert isinstance(obj["id"], int)
    assert isinstance(obj["name"], str)
    assert isinstance(obj["streak"], int)
    assert isinstance(obj["roster"], list)
    for member in obj["roster"]:
        assert_item(member)


def assert_map_score(obj: dict):
    """{ id: int, name: str, team1_score: int, team2_score: int }"""
    assert isinstance(obj["id"], int)
    assert isinstance(obj["name"], str)
    assert isinstance(obj["team1_score"], int)
    assert isinstance(obj["team2_score"], int)


def assert_match_response(obj: dict):
    """{ id, team1: TeamScore, team2: TeamScore, maps: MapScore[],
         best_of: int, date: str, event: str, winner: Item }"""
    assert isinstance(obj["id"], int)
    assert_team_score(obj["team1"])
    assert_team_score(obj["team2"])
    assert isinstance(obj["maps"], list)
    for m in obj["maps"]:
        assert_map_score(m)
    assert isinstance(obj["best_of"], int)
    assert isinstance(obj["date"], str)
    assert isinstance(obj["event"], str)
    assert_item(obj["winner"])


def assert_match_player_stats(obj: dict):
    """{ id: int, name: str, k: int, d: int, swing, adr, kast, rating: float }"""
    assert isinstance(obj["id"], int)
    assert isinstance(obj["name"], str)
    assert isinstance(obj["k"], int)
    assert isinstance(obj["d"], int)
    assert isinstance(obj["swing"], (int, float))
    assert isinstance(obj["adr"], (int, float))
    assert isinstance(obj["kast"], (int, float))
    assert isinstance(obj["rating"], (int, float))


def assert_match_team_stats(obj: dict):
    """{ id: int, name: str, players: MatchPlayerStats[] }"""
    assert isinstance(obj["id"], int)
    assert isinstance(obj["name"], str)
    assert isinstance(obj["players"], list)
    for p in obj["players"]:
        assert_match_player_stats(p)


def assert_match_stats(obj: dict):
    """{ id: int, name: str, team1: MatchTeamStats, team2: MatchTeamStats }"""
    assert isinstance(obj["id"], int)
    assert isinstance(obj["name"], str)
    assert_match_team_stats(obj["team1"])
    assert_match_team_stats(obj["team2"])


def assert_player_stats_values(obj: dict):
    """{ k, d, swing, adr, kast, rating: float, maps_played: int }"""
    for field in ("k", "d", "swing", "adr", "kast", "rating"):
        assert isinstance(obj[field], (int, float)), f"'{field}' should be numeric"
    assert isinstance(obj["maps_played"], int)


def assert_player_response(obj: dict):
    """{ id: int, name: str, team: Item, stats: PlayerStatsValues }"""
    assert isinstance(obj["id"], int)
    assert isinstance(obj["name"], str)
    assert_item(obj["team"])
    assert_player_stats_values(obj["stats"])


def assert_player_stats(obj: dict):
    """{ id: int, name: str, team_id: int, team_name: str,
         k: int, d: int, swing, adr, kast, rating: float }"""
    assert isinstance(obj["id"], int)
    assert isinstance(obj["name"], str)
    assert isinstance(obj["team_id"], int)
    assert isinstance(obj["team_name"], str)
    assert isinstance(obj["k"], int)
    assert isinstance(obj["d"], int)
    for field in ("swing", "adr", "kast", "rating"):
        assert isinstance(obj[field], (int, float))


def assert_grouped_stats(obj: dict):
    """{ id: int|None, name: str, k, d, swing, adr, kast, rating: float,
         maps_played: int }"""
    assert obj.get("id") is None or isinstance(obj["id"], int)
    assert isinstance(obj["name"], str)
    for field in ("k", "d", "swing", "adr", "kast", "rating"):
        assert isinstance(obj[field], (int, float))
    assert isinstance(obj["maps_played"], int)


def assert_fantasy_player(obj: dict):
    """{ id: int, name: str, cost: int }"""
    assert isinstance(obj["id"], int)
    assert isinstance(obj["name"], str)
    assert isinstance(obj["cost"], int)


def assert_fantasy_team(obj: dict):
    """{ id: int, name: str, players: FantasyPlayers[] }"""
    assert isinstance(obj["id"], int)
    assert isinstance(obj["name"], str)
    assert isinstance(obj["players"], list)
    for p in obj["players"]:
        assert_fantasy_player(p)


def assert_fantasy_response(obj: dict):
    """{ id: int, name: str, salary_cap: int, currency: str,
         teams: FantasyTeams[] }"""
    assert isinstance(obj["id"], int)
    assert isinstance(obj["name"], str)
    assert isinstance(obj["salary_cap"], int)
    assert isinstance(obj["currency"], str)
    assert isinstance(obj["teams"], list)
    for t in obj["teams"]:
        assert_fantasy_team(t)


def assert_team_rank(obj: dict):
    """{ id: int, name: str, rank: int, points: int }"""
    assert isinstance(obj["id"], int)
    assert isinstance(obj["name"], str)
    assert isinstance(obj["rank"], int)
    assert isinstance(obj["points"], int)


def assert_ranking(obj: dict):
    """{ date: str, rankings: TeamRank[] }"""
    assert isinstance(obj["date"], str)
    assert isinstance(obj["rankings"], list)
    for entry in obj["rankings"]:
        assert_team_rank(entry)


def assert_team_stats_response(obj: dict):
    """{ id: int, name: str, n: int, n_wins: int }"""
    assert isinstance(obj["id"], int)
    assert isinstance(obj["name"], str)
    assert isinstance(obj["n"], int)
    assert isinstance(obj["n_wins"], int)