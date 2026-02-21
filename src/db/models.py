from pydantic import BaseModel
from datetime import date
from typing import Optional


class Item(BaseModel):
    id: int
    name: str

class TeamResponse(Item):
    streak: int
    roster: list[Item]

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

class MatchPlayerStats(Item):
    k: int
    d: int
    swing: float
    adr: float
    kast: float
    rating: float

class MatchTeamStats(Item):
    players: list[MatchPlayerStats]

class MatchStats(Item):
    team1: MatchTeamStats
    team2: MatchTeamStats

class PlayerStatsValues(BaseModel):
    k: float
    d: float
    swing: float
    adr: float
    kast: float
    rating: float
    maps_played: int

class PlayerResponse(Item):
    team: Item
    stats: PlayerStatsValues

class GroupedStats(BaseModel):
    id: Optional[int] = None
    name: str
    k: float
    d: float
    swing: float
    adr: float
    kast: float
    rating: float
    maps_played: int

class FantasyPlayers(Item):
    cost: int

class FantasyTeams(Item):
    players: list[FantasyPlayers]

class FantasyResponse(Item):
    salary_cap: int
    currency: str
    teams: list[FantasyTeams]

    