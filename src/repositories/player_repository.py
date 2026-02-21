from src.db.classes import players, matches, sides, maps, match_overview, player_stats, teams
from sqlalchemy import select, func, text, literal
from sqlalchemy.orm import aliased
from datetime import date
from dateutil.relativedelta import relativedelta

from src.repositories.base import add_fuzzy_filter


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FIELDS: dict[str, str] = {
    "k": "k",
    "d": "d",
    "swing": "roundswing",
    "adr": "adr",
    "kast": "kast",
    "rating": "rating",
}

GROUP_CONFIG: dict[str, dict] = {
    "players": {"id": "player_id", "name": "player_name"},
    "maps":    {"id": "map_id",    "name": "map_name"},
    "sides":   {"id": "side_id",   "name": "side_name"},
    "events":  {"name": "events"},
}

DEFAULT_LOOKBACK_MONTHS = 3


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def default_date_range() -> tuple[date, date]:
    return date.today() - relativedelta(months=DEFAULT_LOOKBACK_MONTHS), date.today()

def format_stats(rows, group: str) -> list[dict]:
    """Round raw stat columns and reshape rows for API output."""
    output = []
    group_fields = GROUP_CONFIG[group]
    for row in rows:
        row = dict(row)
        stats = {key: round(row[col], 3) for key, col in FIELDS.items()}
        group_info = {key: row[col] for key, col in group_fields.items()}
        output.append({**group_info, **stats, "maps_played": row["n"]})
    return output


# ---------------------------------------------------------------------------
# Query builder
# ---------------------------------------------------------------------------
def build_team_query(playerid: int):
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


def build_player_stats_query(
    playerid = None,
    mapid = None,
    sideid = None,
    matchid = None,
    event = None,
    start_date=None,
    end_date=None,
    group_by = None
    ):

    # --- Aliases ---

    ps = aliased(player_stats)


    # --- Filters ---

    filters = []
    
    # (value, column, fallback_filter_when_value_is_none)
    optional_filters = [
        (playerid, ps.playerid, None),
        (mapid, ps.mapid, lambda col: col !=0),
        (sideid, ps.sideid, lambda col: col !=0),
        (matchid, ps.matchid, None)
        ]
    
    for value, column, default in optional_filters:
        if value is not None:
            filters.append(column == value)
        elif default:
            filters.append(default(column))

    add_fuzzy_filter(match_overview.event, event, filters,order_bys := [])
    
    if start_date and end_date:
        filters += [match_overview.date >= start_date, match_overview.date <= end_date]
    


    # --- Group-by columns ---

    group_bys = []

    if playerid:
        group_bys +=[ps.playerid, players.name]

    group_mapping = {
        'maps': ([ps.mapid.label('map_id'), maps.name.label('map_name')], [ps.mapid, maps.name]),
        'sides': ([ps.sideid.label('side_id'), sides.name.label('side_name')], [ps.sideid, sides.name]),
        'events': ([match_overview.event.label('events')], [match_overview.event])
    }

    extra_selects: list = []
    if group_by:
        for key in group_by:
            select_cols, gb_cols = group_mapping[key]
            extra_selects.extend(select_cols)
            group_bys.extend(gb_cols)

    

    # --- SELECT columns ---
    is_aggregating = len(group_bys) > 0

    stat_cols = [
        func.coalesce(func.avg(getattr(ps, col)), 0).label(col) if is_aggregating
        else getattr(ps, col).label(col)
        for col in FIELDS.values()
    ]

    count_col = func.count().label('n') if is_aggregating else literal(1).label('n')

    selects =[
        ps.playerid.label('player_id'),
        players.name.label('player_name'),
        *stat_cols,
        count_col,
        *extra_selects
    ]
    
    stmnt = (
        select(*selects)
            .join(players, players.playerid == ps.playerid)
            .join(maps, maps.mapid == ps.mapid)
            .join(sides, sides.sideid == ps.sideid)
            .join(match_overview, match_overview.matchid == ps.matchid)
            .where(*filters)
            .group_by(*group_bys)
    )

    return stmnt