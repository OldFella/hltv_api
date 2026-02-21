from sqlalchemy import select, and_, func
from sqlalchemy.orm import aliased

from src.db.session import engine
from src.db.classes import (
    teams, sides, maps, 
    matches, match_overview, 
    player_stats, players
)

from src.repositories.player_repository import FIELDS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_maps(raw_maps: list) -> tuple[list, int, int]:
    """Split raw maps into map list and overall scores."""
    map_list = []
    team1_score = team2_score = None

    for m in raw_maps:
        if m['id'] == 0:
            team1_score = m['team1_score']
            team2_score = m['team2_score']
        else:
            map_list.append(m)

    return map_list, team1_score, team2_score

def _calc_best_of(team1_score: int, team2_score: int, map_count: int) -> int:
    if map_count == 1:
        return 1
    return (2 * max(team1_score, team2_score)) - 1

def _get_winner(row, team1_score, team2_score):
    if team2_score > team1_score:
        return {'id': row['team2_id'], 'name': row['team2_name']}

    return {'id': row['team1_id'],'name': row['team1_name']}

def format_matches(rows)->list[dict]:
    result = []
    for row in rows:
        
        map_list, team1_score, team2_score = _parse_maps(row['maps'])

        best_of = _calc_best_of(team1_score,team2_score, len(map_list))
        
        winner = _get_winner(row, team1_score, team2_score)

        result.append({
            'id':row['match_id'],
            'maps': map_list,
            'team1': {
                'id': row['team1_id'],
                'name': row['team1_name'],
                'score': team1_score
                },
            'team2': {
                'id': row['team2_id'],
                'name': row['team2_name'],
                'score': team2_score
                },
            'best_of': best_of,
            'date': row['date'],
            'event': row['event'],
            'winner': winner
            })

    return result

def format_match_stats(rows, by_map: bool):
    result = []
    for row in rows:
        teams = {}
        for p in row['player_stats']:
            tid = p['team_id']
            if tid not in teams:
                teams[tid] = {'id': tid, 'name': p['team_name'], 'players': []}
            
            teams[tid]['players'] += [{
                'id': p['player_id'],
                'name': p['player_name'],
                **{key:p[col] for key, col in FIELDS.items()}
            }]
        
        team_items = sorted(list(teams.values()), key=lambda t: t['id'])
        result.append({
            'id': row['map_id'],
            'name': row['map_name'],
            'team1': team_items[0],
            'team2': team_items[1]
        })
    return result


def get_streak(match_history, teamid):
    if not match_history:
        return 0
    
    first_result = match_history[0]['winner']['id'] == teamid
    streak = 0
    
    for match in match_history:
        result = match['winner']['id'] == teamid
        if result == first_result:
            streak += 1
        else:
            break
    
    return streak if first_result else -streak  # positive = win streak, negative = loss streak

# ---------------------------------------------------------------------------
# Query builder
# ---------------------------------------------------------------------------

def build_roster_query(
    teamid: int):
    last_match_stmnt = (
        select(match_overview.matchid)
        .join(player_stats, player_stats.matchid == match_overview.matchid)
        .where(player_stats.teamid == teamid)
        .order_by(match_overview.date.desc(), match_overview.matchid.desc())
        .limit(1)
        .subquery()
    )

    stmnt = (
        select(
            players.playerid.label('id'),
            players.name.label('name')
        )
        .distinct()
        .join(player_stats, player_stats.playerid == players.playerid)
        .where(
            player_stats.matchid == last_match_stmnt,
            player_stats.teamid == teamid
        )
    )

    return stmnt

def build_match_stats_query(matchid: int, by_map: bool):

    ps = aliased(player_stats)

    selects_array = [ 
                'player_id',ps.playerid,
                'player_name',players.name,
                'team_id', ps.teamid,
                'team_name', teams.name
    ]
    selects_array_fields = [[col, getattr(ps, col)] for col in FIELDS.values()]
    for f in selects_array_fields:
        selects_array += f

    selects = [
        ps.mapid.label('map_id'),
        maps.name.label('map_name'),
        func.array_agg(
            func.json_build_object(*selects_array)
        ).label("player_stats")
    ]

    filters = [ps.matchid == matchid, ps.sideid == 0]
    if not by_map:
        filters += [ps.mapid == 0]

    stmnt = (
        select(*selects)
        .join(players, players.playerid == ps.playerid)
        .join(teams, teams.teamid == ps.teamid)
        .join(maps, ps.mapid == maps.mapid)
        .group_by(maps.name, ps.mapid)
        .where(*filters)
    )
    return stmnt


def build_match_query(
    matchid = None,
    teamid = None, 
    vsid=None, 
    sideid = 0, 
    mapid = None, 
    limit = 100, 
    offset = 0):


    # --- Aliases ---

    m1 = aliased(matches)
    m2 = aliased(matches)

    t1 = aliased(teams)
    t2 = aliased(teams)


    # --- Filters ---

    filters = [
        m1.sideid == sideid,
        m1.mapid == m2.mapid
    ]

    optional_filters = [
        (matchid, m1.matchid, None),
        (mapid, m1.mapid, None),
        (teamid, m1.teamid, lambda col: col < m2.teamid)
        ]
    
    for value, column, default in optional_filters:
        if value is not None:
            filters.append(column == value)
        elif default:
            filters.append(default(column))
            
    
    if sideid != 0:
        filters.append(and_(m2.sideid != sideid, m2.sideid != 0))

    else:
        filters.append(m1.sideid == m2.sideid)
    
    if teamid is not None and vsid is not None:
        filters.append(m2.teamid == vsid)

    
    # --- Selects ---

    selects = [
        m1.matchid.label('match_id'),
            m1.teamid.label('team1_id'),
            t1.name.label('team1_name'),
            m2.teamid.label('team2_id'),
            t2.name.label('team2_name'),
            match_overview.date.label('date'),
            match_overview.event.label('event'),
            func.array_agg(
                func.json_build_object(
                'id', maps.mapid,
                'name', maps.name,
                'team1_score', m1.score,
                'team2_score', m2.score
                )
            ).label('maps')
    ]

    # --- Group-by columns ---

    group_bys = [
        m1.matchid, m1.teamid, t1.name,
        m2.teamid, t2.name,
        match_overview.date, match_overview.event
    ]


    stmnt = (
        select(*selects)
            .join(
                m2,
                and_(
                    m1.matchid == m2.matchid,
                    m1.teamid != m2.teamid
                    )
            )
            .join(t1, m1.teamid == t1.teamid)
            .join(t2, m2.teamid == t2.teamid)
            .join(match_overview, m1.matchid == match_overview.matchid)
            .join(maps, maps.mapid == m1.mapid)
            .group_by(*group_bys)
            .where(*filters)
            .order_by(match_overview.date.desc(),m1.matchid.desc())
            .offset(offset)
            .limit(limit)
    )
    return stmnt