from dataclasses import dataclass
from datetime import date

@dataclass
class Item:
    id: int
    name: str

@dataclass()
class TeamRank(Item):
    rank: int
    rank_diff: int
    points: int
    points_diff: int

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

# --- Teams ---
@dataclass
class TeamDetail:
    id: int
    name: str
    streak: int
    roster: list[Item]

@dataclass
class TeamMapStats:
    id: int
    name: str
    n: int
    n_wins: int


# --- Matches ---

@dataclass
class TeamScore:
    id: int
    name: str
    score: int
    rank: int

@dataclass
class MapScore:
    id: int
    name: str
    team1_score: int
    team2_score: int

@dataclass
class MatchResult:
    id: int
    team1: TeamScore
    team2: TeamScore
    maps: list[MapScore]
    best_of: int
    date: date
    event: str
    winner: Item

@dataclass
class PlayerMatchStats:
    id: int
    name: str
    k: int
    d: int
    swing: float
    adr: float
    kast: float
    rating: float

@dataclass 
class MatchTeamStats:
    id: int
    name: str
    players: list[PlayerMatchStats]

@dataclass
class MatchPlayerStats:
    id: int
    name: str
    team1: MatchTeamStats
    team2: MatchTeamStats




@dataclass
class MatchupProbabilities:
    map_win_probs: list[float]
    ranking_win_prob: float