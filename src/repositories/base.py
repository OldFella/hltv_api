from src.db.session import engine
from fastapi import HTTPException
from sqlalchemy import func
from typing import Optional


def execute_query(statement, *, many: bool = True):
    """Run a statement and return row mappings, raising 404 if empty."""
    with engine.connect() as con:
        rows = con.execute(statement).mappings().all()
    if not rows:
        raise HTTPException(status_code=404, detail="Item not found")
    return rows if many else rows[0]


def add_fuzzy_filter(col, value: Optional[str], filters: list, order_bys: list, threshold: float = 0.3):
    """Append a pg_trgm similarity filter + ordering when value is provided."""
    if value:
        similarity = func.similarity(col, value)
        filters.append(similarity > threshold)
        order_bys.append(similarity.desc())
