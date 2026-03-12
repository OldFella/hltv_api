from dataclasses import dataclass
from typing import Literal
from datetime import date

from sqlalchemy.engine import Connection
from sqlalchemy import select, func, literal, and_, case
from sqlalchemy.orm import aliased

from src.domain.ports import TeamsPort
from src.domain.models import (
    Item, TeamDetail, MatchResult, TeamMapStats
)
from src.db.classes import (
    players, matches, sides, maps,
    match_overview, player_stats, teams,
)
from src.adapters.sqlalchemy_helpers import add_fuzzy_filter, query_all_fuzzy
from src.adapters.sqlalchemy_players import query_outcomes
from src.adapters.sqlalchemy_matches import query_matches, get_streak, query_roster, format_matches

from src.config.active_maps import ACTIVE_MAPS


@dataclass
class SqlAlchemyTeamsAdapter(TeamsPort):
    """SQLAlchemy implementation of TeamsPort."""

    conn: Connection

    def get_all_fuzzy(
        self,
        name: str | None,
        limit: int,
        offset: int,
    ) -> list[Item]:
        """Return a paginated list of players, optionally filtered by fuzzy name match."""
        return query_all_fuzzy(self.conn, teams, teams.teamid, teams.name, name, limit, offset)
    
    def get_one(
        self,
        teamid: int,
        start_date: date,
        end_date: date,
    ) -> TeamDetail | None:

        stmnt = select(teams.teamid.label('id'), teams.name.label('name')).where(teams.teamid == teamid)
        row = self.conn.execute(stmnt).mappings().first()
        if not row:
            return None
        
        stmnt_matches = query_matches(teamid=teamid, limit = 20)

        match_rows = self.conn.execute(stmnt_matches).mappings().all()
        matches_formatted = format_matches(match_rows)
        streak = get_streak(matches_formatted, teamid)

        stmnt_roster = query_roster(teamid)

        roster = self.conn.execute(stmnt_roster).mappings().all()

        return TeamDetail(
            id = row['id'],
            name = row['name'],
            streak = streak,
            roster = [Item(id = r['id'], name = r['name']) for r in roster]
            )
            
    def get_matchhistory(
        self,
        teamid: int,
        limit: int,
        offset: int,
    ) -> list[MatchResult]:
        stmnt = query_matches(teamid = teamid,limit = limit, offset = offset)
        rows = self.conn.execute(stmnt).mappings().all()
        if not rows:
            return []
        
        return format_matches(rows)
    
    def get_stats(
        self,
        teamid: int,
        start_date: date,
        end_date: date,
        ) -> list[TeamMapStats]:
            stmnt = query_team_stats(teamid = teamid, start_date = start_date, end_date = end_date)
            rows = self.conn.execute(stmnt).mappings().all()
            if not rows:
                return []
            return [TeamMapStats(
                id = r['id'], 
                name = r['name'],
                n = r['n'],
                n_wins = r['n_wins'] 
                ) for r in rows]

# ---------------------------------------------------------------------------
# Query Builders
# ---------------------------------------------------------------------------

def query_team_stats(
    teamid: int,
    start_date,
    end_date
    ):

    # Build a VALUES-based subquery from ACTIVE_MAPS so all maps are always present
    active_map_rows = [
        select(literal(map_id).label('id'), literal(map_name).label('name'))
        for map_id, map_name in ACTIVE_MAPS.items()
    ]
    active_maps_sq = active_map_rows[0].union_all(*active_map_rows[1:]).subquery()


    outcome_sq = query_outcomes().subquery()

    filters = [
        matches.sideid == 0,
        matches.teamid == teamid
    ]
    if start_date:
        filters.append(match_overview.date >= start_date)
    if end_date:
        filters.append(match_overview.date <= end_date)

    stats_sq = (
        select(
            matches.mapid.label('id'),
            maps.name.label('name'),
            func.count(outcome_sq.c.win).label('n'),
            func.sum(outcome_sq.c.win).label('n_wins')
        )
        .join(outcome_sq, and_(
            outcome_sq.c.match_id == matches.matchid,
            outcome_sq.c.map_id == matches.mapid,
            outcome_sq.c.team_id == matches.teamid,
            outcome_sq.c.side_id == matches.sideid

        ))
        .join(maps, maps.mapid == matches.mapid)
        .join(match_overview, match_overview.matchid == matches.matchid)
        .group_by(
            matches.mapid,
            maps.name
        )
        .where(*filters)
        .subquery()
    )
    # Left join stats onto the full active maps list
    stmnt = (
        select(
            active_maps_sq.c.id.label('id'),
            active_maps_sq.c.name.label('name'),
            func.coalesce(stats_sq.c.n, 0).label('n'),
            func.coalesce(stats_sq.c.n_wins, 0).label('n_wins')
        )
        .outerjoin(stats_sq, stats_sq.c.id == active_maps_sq.c.id)
        .order_by(active_maps_sq.c.id)
    )

    return stmnt