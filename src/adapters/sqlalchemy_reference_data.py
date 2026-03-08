from dataclasses import dataclass

from sqlalchemy.engine import Connection
from sqlalchemy import select, Table, Column
from typing import TypeVar, Callable

from src.domain.ports import ReadPort
from src.domain.models import Side, Map

from src.db.classes import sides, maps

T = TypeVar('T')

@dataclass
class SqlAlchemyReadAdapter(ReadPort):
    conn: Connection
    table: Table
    id_col: Column
    name_col: Column
    model: Callable[..., T]

    def get_all(self) -> list[T]:
        stmnt = select(self.id_col.label('id'), self.name_col.label('name'))
        rows = self.conn.execute(stmnt).mappings().all()
        return [self.model(id = r['id'], name = r['name']) for r in rows]

    
    def get_one(self, id:int) -> T | None:
        stmnt = select(self.name_col.label('name')).where(self.id_col == id)
        row = self.conn.execute(stmnt).mappings().all()
        if not row:
            return None
        return self.model(id = id, name = row[0]['name'])

def get_side_adapter(conn: Connection):
    return SqlAlchemyReadAdapter(conn, sides, sides.sideid, sides.name, Side)

def get_map_adapter(conn: Connection):
    return SqlAlchemyReadAdapter(conn, maps, maps.mapid, maps.name, Map)
