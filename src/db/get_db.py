from sqlalchemy.engine import Connection
from fastapi import Depends
from src.db.session import engine

def get_db() -> Connection:
    with engine.connect() as conn:
        yield conn