from sqlalchemy.engine import Connection
from sqlalchemy import select, Table, Column, func
from src.domain.models import Item

def add_fuzzy_filter(
    col: Column, 
    value: str | None, 
    filters: list, 
    order_bys: list, 
    threshold: float = 0.3,
) -> None:
    """Append a pg_trgm similarity filter + ordering when value is provided."""
    if value:
        similarity = func.similarity(col, value)
        filters.append(similarity > threshold)
        order_bys.append(similarity.desc())

def query_all_fuzzy(
    conn: Connection,
    table: Table,
    id_col: Column,
    name_col: Column,
    name: str | None,
    limit: int,
    offset: int,
) -> list[Item]:
    filters, order_bys = [], []
    add_fuzzy_filter(name_col, name, filters, order_bys)
    stmnt = (
        select(id_col.label('id'), name_col.label('name'))
        .where(*filters)
        .order_by(*order_bys)
        .limit(limit)
        .offset(offset)
    )
    rows = conn.execute(stmnt).mappings().all()
    return [Item(id=r['id'], name=r['name']) for r in rows]