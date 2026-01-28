from pydantic import BaseModel
from datetime import date


class item(BaseModel):
    id: int
    name: str

class match(BaseModel):
    matchid: int
    teamid: int
    mapid: int
    sideid: int
    score: int
    date: date

class matchhistory(BaseModel):
    matchid: int
    map: str
    side: str
    team: str
    score: int
    opponent: str
    score_opponent: int
    date: date