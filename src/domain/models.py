from dataclasses import dataclass
from datetime import date

@dataclass
class Item:
    id: int
    name: str

@dataclass()
class TeamRank(Item):
    rank: int
    points: int

# --- Rankings ---
@dataclass
class Ranking:
    date: date    
    rankings: list[TeamRank]

# --- Fantasy ---

@dataclass
class FantasyPlayer(Item):
    cost: int

@dataclass
class FantasyTeam(Item):
    players: list[FantasyPlayer]

@dataclass
class Fantasy(Item):
    salary_cap: int
    currency: str
    teams: list[FantasyTeam]

@dataclass
class CountResponse:
    players: int
    teams: int
    matches: int

