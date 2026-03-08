from dataclasses import dataclass
from datetime import date

@dataclass
class Item:
    id: int
    name: str

# --- Sides ---
@dataclass
class Side(Item):
    ...

# --- Maps ---
@dataclass
class Map(Item):
    ...

@dataclass()
class TeamRank(Item):
    rank: int
    points: int

@dataclass
class Ranking:
    date: date    
    rankings: list[TeamRank]
