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
class PlayerStatRow(Item):
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
class PlayerDetail(Item):
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
class PlayerAggregatedStats(Item):
    rank: int
    k: int
    d: int
    swing: float
    adr: float
    kast: float
    rating: float
    N: int