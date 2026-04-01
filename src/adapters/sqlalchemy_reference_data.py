from dataclasses import dataclass

from sqlalchemy.engine import Connection
from sqlalchemy import select, Table, Column, func, distinct
from sqlalchemy.orm import aliased

from typing import TypeVar, Callable

from src.domain.ports import ReadPort, RankingsPort, CountsPort
from src.domain.models import (
    Item, Ranking, TeamRank,
    Fantasy, FantasyPlayer, FantasyTeam,
    CountResponse
)

from src.config.fantasy import SALARY_CAP, CURRENCY

from src.db.classes import (
    sides, maps, rankings,
    teams, fantasy_overview,
    fantasies, players,
    match_overview
)

from datetime import date

# === Helpers ===

T = TypeVar('T')

def query_all(conn: Connection, id_col: Column, name_col:Column, model:Callable) -> list:
    stmnt = select(id_col.label('id'), name_col.label('name')).order_by(id_col)
    rows = conn.execute(stmnt).mappings().all()
    return [model(id = r['id'], name = r['name']) for r in rows]

# === Adapters ====

@dataclass
class SqlAlchemyReadAdapter(ReadPort):
    conn: Connection
    table: Table
    id_col: Column
    name_col: Column
    model: Callable[..., T]

    def get_all(self) -> list[T]:
       return query_all(self.conn, self.id_col, self.name_col, self.model)

    
    def get_one(self, id:int) -> T | None:
        stmnt = select(self.name_col.label('name')).where(self.id_col == id)
        row = self.conn.execute(stmnt).mappings().all()
        if not row:
            return None
        return self.model(id = id, name = row[0]['name'])

class SqlAlchemySideAdapter(SqlAlchemyReadAdapter):
    pass

class SqlAlchemyMapAdapter(SqlAlchemyReadAdapter):
    pass

def get_side_adapter(conn: Connection):
    return SqlAlchemySideAdapter(conn, sides, sides.sideid, sides.name, Item)

def get_map_adapter(conn: Connection):
    return SqlAlchemyMapAdapter(conn, maps, maps.mapid, maps.name, Item)


@dataclass
class SqlAlchemyRankingsAdapter(RankingsPort):
    conn: Connection

    def get_rankings(self, date: date|None = None) -> Ranking | None:

        date_filter = [rankings.date <= date] if date is not None else []
        # if date is not None:
        #     date_filter.append(rankings.date <= date)

        date_sq = (
            select(distinct(rankings.date))
            .where(*date_filter)
            .order_by(rankings.date.desc()).limit(2).subquery()
        )

        stmnt = (
            select(
                rankings.teamid.label('id'),
                teams.name.label('name'),
                func.rank().over(partition_by=rankings.date, order_by=rankings.points.desc()).label('rank'),
                rankings.points.label('points'),
                rankings.date.label('date')
            )
            .join(teams, teams.teamid == rankings.teamid)
            .where(rankings.date.in_(date_sq))
            .order_by(rankings.date.desc(), rankings.points.desc())
        )
   

        rows = self.conn.execute(stmnt).mappings().all()

        if not rows:
            return None
        
        print(rows)

        from itertools import groupby
        grouped_data = [list(group) for _, group in groupby(rows, key=lambda x: x['date'])]
        print(grouped_data)
        if len(grouped_data) < 2:
            current_rows, previous_rows = grouped_data[0], grouped_data[0]
        else:
            current_rows, previous_rows = grouped_data[0], grouped_data[1]


        return Ranking(
            date=current_rows[0]['date'],
            rankings = [TeamRank(
                id = r1['id'], 
                name = r1['name'], 
                rank = r1['rank'],
                rank_diff = r1['rank'] - r2['rank'],
                points = r1['points'],
                points_diff = r1['points'] - r2['points']) for r1,r2 in zip(current_rows, previous_rows)])

@dataclass
class SqlAlchemyFantasyAdapter(ReadPort):
    conn: Connection

    def get_all(self) -> list[Item]:
        return query_all(
            self.conn, 
            fantasy_overview.fantasyid, 
            fantasy_overview.name,
            Item
            )
    def get_one(self, fantasyid) -> Fantasy | None:
        fo = aliased(fantasy_overview)
        f = aliased(fantasies)
        stmnt = (
            select(
                fo.fantasyid.label('id'),
                fo.name.label('name')
            )
            .where(fo.fantasyid == fantasyid)
        )
        row = self.conn.execute(stmnt).mappings().first()

        if not row:
            return None

        stmnt_player = (
            select(
                f.playerid.label('player_id'),
                players.name.label('player_name'),
                f.teamid.label('team_id'),
                teams.name.label('team_name'),
                f.cost.label('cost')
            )
            .join(players, players.playerid == f.playerid)
            .join(teams, teams.teamid == f.teamid)
            .where(f.fantasyid == fantasyid)
            .order_by(f.teamid)
        )

        rows_player = self.conn.execute(stmnt_player).mappings().all()

        team = {}
        for p in rows_player:
            tid = p['team_id']
            if tid not in team:
                team[tid] = {'id': tid, 'name': p['team_name'], 'players': []}
            team[tid]['players'].append(
                FantasyPlayer(
                    id=p['player_id'], 
                    name=p['player_name'], 
                    cost=p['cost']
                    )
            )
        return Fantasy(
            id = row['id'],
            name = row['name'],
            salary_cap = SALARY_CAP,
            currency = CURRENCY,
            teams = [FantasyTeam(
                id = t['id'], 
                name = t['name'], 
                players = t['players']) for t in team.values()]
        )

@dataclass
class SqlAlchemyCountsAdapter(CountsPort):
    conn: Connection

    def get_counts(self) -> CountResponse:
        queries = [
            ('players', select(func.count(distinct(players.playerid)).label('count'))),
            ('teams', select(func.count(teams.teamid).label('count'))),
            ('matches', select(func.count(match_overview.matchid).label('count')))
        ]
        result = {}
        for key, q in queries:
            result[key] = self.conn.execute(q).mappings().first()['count']

        return CountResponse(**result)