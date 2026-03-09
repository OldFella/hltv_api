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

# --- Counts ---

@dataclass
class CountResponse:
    players: int
    teams: int
    matches: int

# --- Players ---

@dataclass
class PlayerStatRow:
    id: int
    name: str
    team_id: int
    team_name: str
    k: float
    d: float
    swing: float
    adr: float
    kast: float
    rating: float
    N: int

@dataclass
class PlayerStats:
    k: float
    d: float
    swing: float
    adr: float
    kast: float
    rating: float
    N: int

@dataclass
class PlayerDetail:
    id: int
    name: str
    team: Item
    stats: PlayerStats

@dataclass
class PlayerGroupedStats:
    id: int | None
    name: str
    k: float
    d: float
    swing: float
    adr: float
    kast: float
    rating: float
    N: int

@dataclass
class PlayerAggregatedStats:
    id: int
    name: str
    rank: int
    k: int
    d: int
    swing: float
    adr: float
    kast: float
    rating: float
    N: int