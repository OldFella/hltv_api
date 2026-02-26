from src.db.classes import matches, maps, match_overview
from sqlalchemy import select, func, text, literal, and_, case
from sqlalchemy.orm import aliased
from datetime import date

from src.repositories.player_repository import build_outcome_query
from src.config.active_maps import ACTIVE_MAPS


# ---------------------------------------------------------------------------
# Query builder
# ---------------------------------------------------------------------------

def build_team_stats_query(
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


    outcome_sq = build_outcome_query().subquery()

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