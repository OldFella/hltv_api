from sqlalchemy import Select
import pytest

from src.repositories.match_repository import (
    _parse_maps,
    _calc_best_of,
    _get_winner,
    format_matches,
    format_match_stats,
    get_streak,
    build_match_query,
    build_roster_query,
    build_match_stats_query
)

# ---------------------------------------------------------------------------
# _parse_maps
# ---------------------------------------------------------------------------

class TestParseMaps:
    def setup_method(self, method):
        self.raw_maps = [
            {"id": 0, "team1_score": 1, "team2_score": 0},
            {"id": 1, "name": "Mirage", "team1_score": 16, "team2_score": 14},
            {"id": 2, "name": "Inferno", "team1_score": 16, "team2_score": 10},
        ]

    def test_returns_tuple_of_three(self):
        result = _parse_maps(self.raw_maps)
        assert len(result) == 3

    def test_extracts_overall_scores(self):
        _, team1_score, team2_score = _parse_maps(self.raw_maps)
        assert team1_score == 1
        assert team2_score == 0

    def test_excludes_map_with_id_zero(self):
        map_list, _, _ = _parse_maps(self.raw_maps)
        assert all(m["id"] != 0 for m in map_list)

    def test_returns_correct_map_count(self):
        map_list, _, _ = _parse_maps(self.raw_maps)
        assert len(map_list) == 2

    def test_empty_raw_maps_returns_none_scores(self):
        map_list, team1_score, team2_score = _parse_maps([])
        assert team1_score is None
        assert team2_score is None
        assert map_list == []


# ---------------------------------------------------------------------------
# _calc_best_of
# ---------------------------------------------------------------------------

class TestCalcBestOf:
    def test_single_map_returns_1(self):
        assert _calc_best_of(1, 0, 1) == 1

    def test_bo3(self):
        assert _calc_best_of(2, 1, 2) == 3

    def test_bo5(self):
        assert _calc_best_of(3, 2, 3) == 5

    def test_uses_max_score(self):
        assert _calc_best_of(1, 2, 2) == 3


# ---------------------------------------------------------------------------
# _get_winner
# ---------------------------------------------------------------------------

class TestGetWinner:
    def setup_method(self, method):
        self.row = {
            "team1_id": 1, "team1_name": "NaVi",
            "team2_id": 2, "team2_name": "Astralis",
        }

    def test_team1_wins(self):
        winner = _get_winner(self.row, 2, 0)
        assert winner == {"id": 1, "name": "NaVi"}

    def test_team2_wins(self):
        winner = _get_winner(self.row, 0, 2)
        assert winner == {"id": 2, "name": "Astralis"}

    def test_winner_has_id_and_name(self):
        winner = _get_winner(self.row, 2, 0)
        assert "id" in winner and "name" in winner


# ---------------------------------------------------------------------------
# format_matches
# ---------------------------------------------------------------------------

class TestFormatMatches:
    def setup_method(self, method):
        self.mock_row = {
            "match_id": 1,
            "team1_id": 1, "team1_name": "NaVi",
            "team2_id": 2, "team2_name": "Astralis",
            "date": "2024-01-01",
            "event": "ESL Pro League",
            "maps": [
                {"id": 0, "team1_score": 2, "team2_score": 1, "name": "overall"},
                {"id": 1, "name": "Mirage", "team1_score": 16, "team2_score": 14},
                {"id": 2, "name": "Inferno", "team1_score": 16, "team2_score": 10},
            ]
        }

    def test_returns_list(self):
        assert isinstance(format_matches([self.mock_row]), list)

    def test_returns_correct_shape(self):
        result = format_matches([self.mock_row])[0]
        assert all(k in result for k in ["id", "maps", "team1", "team2", "best_of", "winner", "date", "event"])

    def test_team1_shape(self):
        result = format_matches([self.mock_row])[0]
        assert all(k in result["team1"] for k in ["id", "name", "score"])

    def test_team2_shape(self):
        result = format_matches([self.mock_row])[0]
        assert all(k in result["team2"] for k in ["id", "name", "score"])

    def test_excludes_overall_map(self):
        result = format_matches([self.mock_row])[0]
        assert all(m["id"] != 0 for m in result["maps"])

    def test_correct_best_of(self):
        result = format_matches([self.mock_row])[0]
        assert result["best_of"] == 3

    def test_correct_winner(self):
        result = format_matches([self.mock_row])[0]
        assert result["winner"]["name"] == "NaVi"

    def test_empty_rows_returns_empty_list(self):
        assert format_matches([]) == []

# ---------------------------------------------------------------------------
# get_streak
# ---------------------------------------------------------------------------

class TestGetStreak:
    def setup_method(self, method):
        self.win = {'winner': {'id': 1}}
        self.loss = {'winner': {'id': 2}}

    def test_empty_history_returns_zero(self):
        assert get_streak([], 1) == 0

    def test_win_streak(self):
        assert get_streak([self.win, self.win, self.win], 1) == 3

    def test_loss_streak(self):
        assert get_streak([self.loss, self.loss], 1) == -2

    def test_streak_stops_at_first_different_result(self):
        assert get_streak([self.win, self.win, self.loss], 1) == 2

    def test_single_win(self):
        assert get_streak([self.win], 1) == 1


# ---------------------------------------------------------------------------
# format_match_stats
# ---------------------------------------------------------------------------

class TestFormatMatchStats:
    def setup_method(self, method):
        self.mock_rows = [{
            'map_id': 0,
            'map_name': 'All',
            'player_stats': [
                {'player_id': 1, 'player_name': 's1mple', 'team_id': 1,
                 'team_name': 'NaVi', 'k': 25, 'd': 15, 'roundswing': 3.5,
                 'adr': 90.0, 'kast': 75.0, 'rating': 1.4},
                {'player_id': 2, 'player_name': 'device', 'team_id': 2,
                 'team_name': 'Astralis', 'k': 20, 'd': 18, 'roundswing': 1.2,
                 'adr': 80.0, 'kast': 70.0, 'rating': 1.1}
            ]
        }]

    def test_returns_list(self):
        assert isinstance(format_match_stats(self.mock_rows, by_map=False), list)

    def test_returns_correct_shape(self):
        result = format_match_stats(self.mock_rows, by_map=False)[0]
        assert all(k in result for k in ['id', 'name', 'team1', 'team2'])

    def test_team1_is_lower_id(self):
        result = format_match_stats(self.mock_rows, by_map=False)[0]
        assert result['team1']['id'] == 1
        assert result['team2']['id'] == 2

    def test_players_in_teams(self):
        result = format_match_stats(self.mock_rows, by_map=False)[0]
        assert len(result['team1']['players']) == 1
        assert len(result['team2']['players']) == 1


# ---------------------------------------------------------------------------
# build_roster_query
# ---------------------------------------------------------------------------
class TestBuildRosterQuery:
    def test_returns_select_statement(self):
        assert isinstance(build_roster_query(teamid=1), Select)

    def test_matchid_filter(self):
        compiled = str(build_roster_query(teamid=1).compile())
        assert "teamid" in compiled.lower()

# ---------------------------------------------------------------------------
# build_match_stats_query
# ---------------------------------------------------------------------------
class TestBuildMatchStatsQuery:
    def test_returns_select_statement(self):
        assert isinstance(build_match_stats_query(matchid=1,by_map=False), Select)

    def test_matchid_filter(self):
        compiled = str(build_match_stats_query(matchid=1, by_map=False).compile())
        assert "matchid" in compiled.lower()
    
# ---------------------------------------------------------------------------
# build_match_query
# ---------------------------------------------------------------------------

class TestBuildMatchQuery:
    def test_returns_select_statement(self):
        assert isinstance(build_match_query(), Select)

    def test_matchid_filter(self):
        compiled = str(build_match_query(matchid=1).compile())
        assert "matchid" in compiled.lower()

    def test_teamid_filter(self):
        compiled = str(build_match_query(teamid=1).compile())
        assert "teamid" in compiled.lower()

    def test_vsid_only_applied_with_teamid(self):
        without_teamid = str(build_match_query(vsid=2).compile())
        with_teamid = str(build_match_query(teamid=1, vsid=2).compile())
        assert with_teamid != without_teamid

    def test_limit_applied(self):
        compiled = str(build_match_query(limit=5).compile())
        assert "limit" in compiled.lower()

    def test_offset_applied(self):
        compiled = str(build_match_query(offset=10).compile())
        assert "offset" in compiled.lower()

    def test_nonzero_sideid_adds_side_filter(self):
        compiled = str(build_match_query(sideid=1).compile())
        assert "sideid" in compiled.lower()