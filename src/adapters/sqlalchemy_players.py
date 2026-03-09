from dataclasses import dataclass
from typing import Literal
from datetime import date

from sqlalchemy.engine import Connection
from sqlalchemy import select, func, literal, and_, case
from sqlalchemy.orm import aliased

from src.domain.ports import PlayersPort
from src.domain.models import (
    Item, PlayerDetail, PlayerStats,
    PlayerStatRow, PlayerGroupedStats,
)
from src.db.classes import (
    players, matches, sides, maps,
    match_overview, player_stats, teams,
)
from src.adapters.sqlalchemy_helpers import add_fuzzy_filter, query_all_fuzzy

FIELDS: dict[str, str] = {
    "k": "k",
    "d": "d",
    "swing": "roundswing",
    "adr": "adr",
    "kast": "kast",
    "rating": "rating",
}


@dataclass
class SqlAlchemyPlayersAdapter(PlayersPort):
    """SQLAlchemy implementation of PlayersPort."""

    conn: Connection

    def get_all_fuzzy(
        self,
        name: str | None,
        limit: int,
        offset: int,
    ) -> list[Item]:
        """Return a paginated list of players, optionally filtered by fuzzy name match."""
        return query_all_fuzzy(self.conn, players, players.playerid, players.name, name, limit, offset)

    def get_one(
        self,
        playerid: int,
        start_date: date,
        end_date: date,
    ) -> PlayerDetail | None:
        """
        Return aggregated stats and current team for a single player.
        Returns None if the player has no stats in the given date range.
        """
        stmnt_stats = query_player_stats(
            playerid=playerid,
            sideid=0,
            start_date=start_date,
            end_date=end_date,
        )
        row = self.conn.execute(stmnt_stats).mappings().one_or_none()
        if row is None:
            return None
        stmnt_team = query_current_team(playerid)
        team = self.conn.execute(stmnt_team).mappings().one_or_none()
        return PlayerDetail(
            id=row['player_id'],
            name=row['player_name'],
            team=Item(id=team['id'], name=team['name']),
            stats=PlayerStats(
                k=float(round(row['k'], 3)),
                d=float(round(row['d'], 3)),
                swing=float(round(row['roundswing'], 3)),
                adr=float(round(row['adr'], 3)),
                kast=float(round(row['kast'], 3)),
                rating=float(round(row['rating'], 3)),
                N=row['n'],
            )
        )

    def get_raw_stats(
        self,
        mapid: int | None,
        sideid: int | None,
        limit: int,
        offset: int,
    ) -> list[PlayerStatRow]:
        """Return a paginated log of raw per-player per-match stat rows."""
        stmnt = query_player_stats(
            mapid=mapid,
            sideid=sideid,
            include_teams=True,
        ).limit(limit).offset(offset)

        rows = self.conn.execute(stmnt).mappings().all()

        return [
            PlayerStatRow(
                id=r['player_id'],
                name=r['player_name'],
                team_id=r['team_id'],
                team_name=r['team_name'],
                k=float(round(r['k'], 3)),
                d=float(round(r['d'], 3)),
                swing=float(round(r['roundswing'], 3)),
                adr=float(round(r['adr'], 3)),
                kast=float(round(r['kast'], 3)),
                rating=float(round(r['rating'], 3)),
                N=r['n'],
            )
            for r in rows
        ]

    def get_raw_stats_by_outcome(
        self,
        outcome: Literal["win", "lose"],
        mapid: int | None,
        limit: int,
        offset: int,
    ) -> list[PlayerStatRow]:
        """Return a paginated log of raw stat rows filtered by match outcome (win or lose)."""
        stmnt = query_player_stats_by_outcome(
            mode=outcome,
            mapid=mapid,
        ).limit(limit).offset(offset)
        rows = self.conn.execute(stmnt).mappings().all()
        return [
            PlayerStatRow(
                id=r['player_id'],
                name=r['player_name'],
                team_id=r['team_id'],
                team_name=r['team_name'],
                k=float(round(r['k'], 3)),
                d=float(round(r['d'], 3)),
                swing=float(round(r['roundswing'], 3)),
                adr=float(round(r['adr'], 3)),
                kast=float(round(r['kast'], 3)),
                rating=float(round(r['rating'], 3)),
                N=r['n'],
            )
            for r in rows
        ]

    def get_grouped_stats(
        self,
        playerid: int,
        group: Literal["maps", "sides", "events"],
        mapid: int | None,
        start_date: date,
        end_date: date,
    ) -> list[PlayerGroupedStats] | None:
        """
        Return a player's stats aggregated by the given dimension.
        Returns None if no rows are found.
        """
        stmnt = query_player_stats(
            playerid=playerid,
            mapid=mapid,
            sideid=None if group == 'sides' else 0,
            start_date=start_date,
            end_date=end_date,
            group_by=[group],
        )

        rows = self.conn.execute(stmnt).mappings().all()

        if not rows:
            return None

        return [
            PlayerGroupedStats(
                id=r.get('map_id') or r.get('side_id'),
                name=r.get('map_name') or r.get('side_name') or r.get('events'),
                k=float(round(r['k'], 3)),
                d=float(round(r['d'], 3)),
                swing=float(round(r['roundswing'], 3)),
                adr=float(round(r['adr'], 3)),
                kast=float(round(r['kast'], 3)),
                rating=float(round(r['rating'], 3)),
                N=r['n'],
            )
            for r in rows
        ]


# ---------------------------------------------------------------------------
# Query Builders
# ---------------------------------------------------------------------------

def query_current_team(playerid: int):
    """
    Return the team a player most recently appeared for.
    Resolves via their latest match in match_overview.
    """
    last_match_stmnt = (
        select(match_overview.matchid)
        .join(player_stats, player_stats.matchid == match_overview.matchid)
        .where(player_stats.playerid == playerid)
        .order_by(match_overview.date.desc(), match_overview.matchid.desc())
        .limit(1)
        .scalar_subquery()
    )

    stmnt = (
        select(
            teams.teamid.label('id'),
            teams.name.label('name')
        )
        .distinct()
        .join(player_stats, player_stats.teamid == teams.teamid)
        .where(
            player_stats.matchid == last_match_stmnt,
            player_stats.playerid == playerid
        )
    )
    return stmnt


def query_player_stats(
    playerid=None,
    mapid=None,
    sideid=None,
    matchid=None,
    event=None,
    start_date=None,
    end_date=None,
    group_by=None,
    include_teams=False,
    ps=None,
):
    """
    Flexible player stats query builder.

    Aggregates with avg() when group_by is provided, otherwise returns raw rows.
    - mapid=None excludes the id=0 overall rows (filters mapid != 0)
    - sideid=None excludes the id=0 overall rows (filters sideid != 0)
    - group_by accepts a list of: 'maps', 'sides', 'events'
    - include_teams=True adds team_id and team_name to the select
    """
    if ps is None:
        ps = aliased(player_stats)

    filters = []

    optional_filters = [
        (playerid, ps.playerid, None),
        (mapid, ps.mapid, lambda col: col != 0),
        (sideid, ps.sideid, lambda col: col != 0),
        (matchid, ps.matchid, None),
    ]

    for value, column, default in optional_filters:
        if value is not None:
            filters.append(column == value)
        elif default:
            filters.append(default(column))

    add_fuzzy_filter(match_overview.event, event, filters, order_bys := [])

    if start_date and end_date:
        filters += [match_overview.date >= start_date, match_overview.date <= end_date]

    group_bys = []

    if playerid:
        group_bys += [ps.playerid, players.name]

    group_mapping = {
        'maps': ([ps.mapid.label('map_id'), maps.name.label('map_name')], [ps.mapid, maps.name]),
        'sides': ([ps.sideid.label('side_id'), sides.name.label('side_name')], [ps.sideid, sides.name]),
        'events': ([match_overview.event.label('events')], [match_overview.event]),
    }

    extra_selects: list = []
    if group_by:
        for key in group_by:
            select_cols, gb_cols = group_mapping[key]
            extra_selects.extend(select_cols)
            group_bys.extend(gb_cols)

    is_aggregating = len(group_bys) > 0

    stat_cols = [
        func.coalesce(func.avg(getattr(ps, col)), 0).label(col) if is_aggregating
        else getattr(ps, col).label(col)
        for col in FIELDS.values()
    ]

    count_col = func.count().label('n') if is_aggregating else literal(1).label('n')

    selects = [
        ps.playerid.label('player_id'),
        players.name.label('player_name'),
        *stat_cols,
        count_col,
        *extra_selects,
    ]

    if include_teams:
        selects += [ps.teamid.label('team_id'), teams.name.label('team_name')]

    stmnt = (
        select(*selects)
        .join(players, players.playerid == ps.playerid)
        .join(maps, maps.mapid == ps.mapid)
        .join(sides, sides.sideid == ps.sideid)
        .join(match_overview, match_overview.matchid == ps.matchid)
        .join(teams, teams.teamid == ps.teamid)
        .where(*filters)
        .group_by(*group_bys)
    )

    return stmnt


def query_outcomes():
    """
    Build a subquery labelling each (matchid, mapid, teamid) row as win=1 or lose=0.
    Self-joins matches aliased as m1/m2 and compares scores. Filters to sideid=0 (overall).
    """
    m1 = aliased(matches)
    m2 = aliased(matches)

    stmnt = (
        select(
            m1.matchid.label('match_id'),
            m1.mapid.label('map_id'),
            m1.teamid.label('team_id'),
            m1.sideid.label('side_id'),
            case(
                (m1.score > m2.score, 1),
                (m1.score < m2.score, 0),
                else_=None
            ).label('win')
        )
        .join(m2, and_(
            m2.matchid == m1.matchid,
            m2.teamid != m1.teamid,
            m1.mapid == m2.mapid,
            m1.sideid == m2.sideid,
        ))
        .where(m1.sideid == 0)
    )
    return stmnt


def query_player_stats_by_outcome(
    mode='win',
    mapid=None,
    sideid=0,
):
    """
    Extend query_player_stats with an outcome join, filtering to wins or losses.
    Uses query_outcomes() as a subquery joined on (matchid, mapid, teamid).
    """
    ps = aliased(player_stats)

    outcome_sq = query_outcomes().subquery()
    outcome_filter = 1 if mode == 'win' else 0

    stmnt = query_player_stats(
        mapid=mapid,
        sideid=sideid,
        include_teams=True,
        ps=ps,
    )

    stmnt = (
        stmnt
        .join(outcome_sq, and_(
            outcome_sq.c.match_id == ps.matchid,
            outcome_sq.c.map_id == ps.mapid,
            outcome_sq.c.team_id == ps.teamid,
        ))
        .where(outcome_sq.c.win == outcome_filter)
    )

    return stmnt