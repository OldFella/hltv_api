from pydantic import BaseModel
from datetime import date


class Item(BaseModel):
    id: int
    name: str

class match(BaseModel):
    matchid: int
    teamid: int
    mapid: int
    sideid: int
    score: int
    date: date
    event: str

class MatchHistory(BaseModel):
    matchid: int
    map: str
    side: str
    team: str
    score: int
    opponent: str
    score_opponent: int
    date: date
    event: str

class TeamScore(Item):
    score: int

class MapScore(Item):
    team1_score: int
    team2_score: int

class MatchResponse(BaseModel):
    id: int
    team1: TeamScore
    team2: TeamScore
    maps: list[MapScore]
    best_of: int
    date: date
    event: str
    winner: Item

class MapResponse(BaseModel):
    id: int
    team1: TeamScore
    team2: TeamScore
    date: date
    event: str
    maps: list[MapScore]
    best_of: int
    winner: Item

class PlayerStats(Item):
    k: float
    d: float
    swing: float
    adr: float
    kast: float
    rating: float

class PlayerAverageStats(Item):
    k: float
    d: float
    swing: float
    adr: float
    kast: float
    rating: float
    maps_played: int
    