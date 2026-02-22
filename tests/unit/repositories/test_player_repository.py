from datetime import date
from unittest.mock import MagicMock
from sqlalchemy import Select
import pytest

from src.repositories.player_repository import (
    default_date_range,
    format_stats,
    build_player_stats_query,
    DEFAULT_LOOKBACK_MONTHS,
    build_team_query,
)


# ---------------------------------------------------------------------------
# default_date_range
# ---------------------------------------------------------------------------

class TestDefaultDateRange:
    def test_returns_tuple_of_dates(self):
        start, end = default_date_range()
        assert isinstance(start, date)
        assert isinstance(end, date)

    def test_end_is_today(self):
        _, end = default_date_range()
        assert end == date.today()

    def test_start_is_correct_months_ago(self):
        from dateutil.relativedelta import relativedelta
        start, _ = default_date_range()
        assert start == date.today() - relativedelta(months=DEFAULT_LOOKBACK_MONTHS)

    def test_start_is_before_end(self):
        start, end = default_date_range()
        assert start < end


# ---------------------------------------------------------------------------
# format_stats
# ---------------------------------------------------------------------------

class TestFormatStats:
    def setup_method(self, method):
        self.mock_row = {
            "player_id": 1,
            "player_name": "s1mple",
            "k": 1.2345,
            "d": 0.8765,
            "roundswing": 0.1234,
            "adr": 85.6789,
            "kast": 0.7234,
            "rating": 1.3456,
            "n": 20,
        }

    def test_returns_list(self):
        result = format_stats([self.mock_row], "players")
        assert isinstance(result, list)

    def test_rounds_to_3_decimals(self):
        result = format_stats([self.mock_row], "players")[0]
        assert result["k"] == round(1.2345, 3)
        assert result["adr"] == round(85.6789, 3)

    def test_includes_maps_played(self):
        result = format_stats([self.mock_row], "players")[0]
        assert result["maps_played"] == 20

    def test_players_group_includes_id_and_name(self):
        result = format_stats([self.mock_row], "players")[0]
        assert "id" in result and "name" in result

    def test_maps_group_includes_id_and_name(self):
        row = {**self.mock_row, "map_id": 1, "map_name": "Mirage"}
        result = format_stats([row], "maps")[0]
        assert "id" in result and "name" in result

    def test_events_group_includes_only_name(self):
        row = {**self.mock_row, "events": "ESL Pro League"}
        result = format_stats([row], "events")[0]
        assert "name" in result
        assert "id" not in result

    def test_all_stat_fields_present(self):
        result = format_stats([self.mock_row], "players")[0]
        assert all(k in result for k in ["k", "d", "swing", "adr", "kast", "rating"])

    def test_empty_rows_returns_empty_list(self):
        assert format_stats([], "players") == []
    
    def test_events_group_has_no_id(self):
        row = {**self.mock_row, "events": "ESL Pro League"}
        result = format_stats([row], "events")[0]
        assert "name" in result
        assert result.get("id") is None
    
    def test_sides_group_includes_id_and_name(self):
        row = {**self.mock_row, "side_id": 1, "side_name": "CT"}
        result = format_stats([row], "sides")[0]
        assert "id" in result and "name" in result

# ---------------------------------------------------------------------------
# build_team_query
# ---------------------------------------------------------------------------
class TestBuildTeamQuery:
    def test_returns_select_statement(self):
        result = build_team_query(playerid=1)
        assert isinstance(result, Select)
    
    def test_playerid_filter(self):
        compiled = str(build_team_query(playerid=1).compile())
        assert "playerid" in compiled.lower()
    
    def test_uses_subquery(self):
        compiled = str(build_team_query(playerid=1).compile())
        assert compiled.lower().count("select") > 1


# ---------------------------------------------------------------------------
# build_player_stats_query
# ---------------------------------------------------------------------------

class TestBuildPlayerStatsQuery:
    def test_returns_select_statement(self):
        result = build_player_stats_query()
        assert isinstance(result, Select)

    def test_playerid_filter(self):
        result = build_player_stats_query(playerid=1)
        compiled = str(result.compile())
        assert "playerid" in compiled.lower()

    def test_date_filter(self):
        result = build_player_stats_query(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31)
        )
        compiled = str(result.compile())
        assert "date" in compiled.lower()

    def test_group_by_maps(self):
        result = build_player_stats_query(group_by=["maps"])
        compiled = str(result.compile())
        assert "map" in compiled.lower()

    def test_group_by_sides(self):
        result = build_player_stats_query(group_by=["sides"])
        compiled = str(result.compile())
        assert "side" in compiled.lower()

    def test_group_by_events(self):
        result = build_player_stats_query(group_by=["events"])
        compiled = str(result.compile())
        assert "event" in compiled.lower()

    def test_no_group_by_uses_literal_count(self):
        result = build_player_stats_query()
        compiled = str(result.compile())
        assert "count" not in compiled.lower()

    def test_with_playerid_uses_avg(self):
        result = build_player_stats_query(playerid=1)
        compiled = str(result.compile())
        assert "avg" in compiled.lower()
    
    def test_no_group_by_uses_literal_avg(self):
        result = build_player_stats_query()
        compiled = str(result.compile())
        assert "avg" not in compiled.lower()
    
    def test_event_filter(self):
        result = build_player_stats_query(event="ESL Pro League")
        compiled = str(result.compile())
        assert "event" in compiled.lower()

    def test_mapid_filter(self):
        result = build_player_stats_query(mapid=1)
        compiled = str(result.compile())
        assert "mapid" in compiled.lower()

    def test_sideid_filter(self):
        result = build_player_stats_query(sideid=1)
        compiled = str(result.compile())
        assert "sideid" in compiled.lower()

    def test_matchid_filter(self):
        result = build_player_stats_query(matchid=1)
        compiled = str(result.compile())
        assert "matchid" in compiled.lower()