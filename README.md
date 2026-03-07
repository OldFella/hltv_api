# HLTV API ![Tests](https://github.com/OldFella/hltv_api/actions/workflows/tests.yml/badge.svg)

A RESTful API for exposing Counter-Strike match, team, and player data gathered with an HLTV scraper.  
Built in Python, this API provides structured endpoints for accessing HLTV.org–derived data for use in analytics tools, bots, dashboards, or other applications.

> **Website:** https://www.csapi.de
> **Live API:** https://api.csapi.de
> **Status:** Active, read-only API

---

## 🚀 Features

### Teams
- Get a list of all teams with fuzzy name search
- Look up a team by ID including current roster and win/loss streak
- Get match history for a team
- Get per-map win/loss stats for a team over a date range

### Matches
- Retrieve all matches with pagination
- Retrieve latest matches including current world ranking for each team
- Retrieve a specific match by ID including maps and scores
- Get player stats for a match, optionally broken down per map

### Players
- Get a list of all players with fuzzy name search
- Look up a player by ID including current team and overall stats
- Get raw per-match player stats, filterable by map and side
- Get player stats filtered by match outcome (win/loss)
- Get player stats grouped by map, side, or event

### Rankings
- Get the most recent Valve Regional Standings (VRS) ranking with team points

### Fantasy
- Get all available fantasies
- Get fantasy details including teams, players and costs
- Salary cap: $1,000 (costs expressed in units of $1,000)

### Maps & Sides
- Get all maps
- Get all sides

### Counts
- Get distinct counts of players, teams, and matches in the database

### API Design
- Read-only (GET requests only)
- Simple RESTful endpoints
- JSON responses
- Fuzzy search on team and player names
- Pagination support on all list endpoints

### Update Frequency
> All data provided by this API is refreshed once per day, so recent matches or roster changes may take up to 24 hours to appear.

---

## 🧰 Tech Stack

- **Language:** Python
- **Web Framework:** FastAPI
- **ASGI Server:** Uvicorn / Gunicorn
- **Reverse Proxy:** Nginx
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Data Source:** HLTV.org
- **API Style:** REST
- **Response Format:** JSON
- **Deployment:** Self-hosted (Linux server + Docker)
- **Version Control:** Git + GitHub

---

## 🌍 Base URL

https://api.csapi.de/

---

## 📦 Installation (Local Development)

Clone the repository and install dependencies:
```sh
git clone https://github.com/OldFella/hltv_api.git
cd hltv_api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Run the API locally:
```sh
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

By default, the local API will be available at http://localhost:8000

---

## 📌 API Endpoints

### Teams
| Endpoint | Params | Description |
|---|---|---|
| `GET /teams/` | `name` (fuzzy), `limit=20`, `offset=0` | Get all teams |
| `GET /teams/{teamid}` | — | Get team by ID with roster and streak |
| `GET /teams/{teamid}/matchhistory` | `limit=5`, `offset=0` | Get match history for a team |
| `GET /teams/{teamid}/stats` | `start_date`, `end_date` | Get per-map win/loss stats (default: last 3 months) |

### Matches
| Endpoint | Params | Description |
|---|---|---|
| `GET /matches/` | `limit=100`, `offset=0` | Get all matches |
| `GET /matches/latest` | `limit=10`, `offset=0` | Get latest matches with team rankings |
| `GET /matches/{matchid}` | — | Get a match by ID |
| `GET /matches/{matchid}/stats` | `by_map=false` | Get player stats for a match (`by_map=true` for per-map breakdown) |

### Players
| Endpoint | Params | Description |
|---|---|---|
| `GET /players/` | `name` (fuzzy), `limit=20`, `offset=0` | Get all players |
| `GET /players/stats` | `mapid=0`, `sideid=0`, `limit=20`, `offset=0` | Get raw per-match player stats |
| `GET /players/stats/{outcome}` | `outcome`: `win`\|`lose`, `mapid`, `limit=100`, `offset=0` | Get player stats filtered by match outcome |
| `GET /players/{playerid}` | `start_date`, `end_date` | Get player by ID with current team and aggregated stats (default: last 3 months) |
| `GET /players/{playerid}/stats/{group}` | `group`: `maps`\|`sides`\|`events`, `mapid`, `start_date`, `end_date` | Get stats grouped by map, side, or event |

### Rankings
| Endpoint | Params | Description |
|---|---|---|
| `GET /rankings/` | — | Get most recent VRS ranking with team points |

### Counts
| Endpoint | Params | Description |
|---|---|---|
| `GET /counts/` | — | Get distinct counts of players, teams, and matches |

### Fantasy
| Endpoint | Params | Description |
|---|---|---|
| `GET /fantasy/` | — | Get all available fantasies |
| `GET /fantasy/{fantasyid}` | — | Get fantasy details with teams and player costs |

### Maps & Sides
| Endpoint | Description |
|---|---|
| `GET /maps/` | Get all maps |
| `GET /maps/{id}` | Get map by ID |
| `GET /sides/` | Get all sides |
| `GET /sides/{id}` | Get side by ID |

---

## 📄 Example Responses

### Team with roster and streak
```json
{
  "id": 9565,
  "name": "Vitality",
  "streak": 9,
  "roster": [
    {"id": 11893, "name": "zywoo"},
    {"id": 7322,  "name": "apex"},
    {"id": 18462, "name": "mezii"},
    {"id": 16693, "name": "flamez"},
    {"id": 11816, "name": "ropz"}
  ]
}
```

### Match with maps, winner and team rankings
```json
{
  "id": 2389666,
  "team1": {"id": 8297, "name": "FURIA",    "score": 1, "rank": 3},
  "team2": {"id": 9565, "name": "Vitality", "score": 3, "rank": 1},
  "date": "2026-02-08",
  "event": "IEM Kraków 2026",
  "maps": [
    {"id": 2, "name": "Overpass", "team1_score": 10, "team2_score": 13},
    {"id": 5, "name": "Nuke",     "team1_score": 2,  "team2_score": 13},
    {"id": 6, "name": "Mirage",   "team1_score": 13, "team2_score": 11},
    {"id": 7, "name": "Inferno",  "team1_score": 8,  "team2_score": 13}
  ],
  "best_of": 5,
  "winner": {"id": 9565, "name": "Vitality"}
}
```

### Player details
```json
{
  "id": 11893,
  "name": "zywoo",
  "team": {"id": 9565, "name": "Vitality"},
  "stats": {
    "k": 19.119,
    "d": 11.548,
    "swing": 5.058,
    "adr": 90.107,
    "kast": 78.579,
    "rating": 1.482,
    "maps_played": 42
  }
}
```

### Rankings
```json
{
  "date": "2026-03-01",
  "rankings": [
    {"id": 9565, "name": "Vitality", "rank": 1, "points": 1000},
    {"id": 8297, "name": "FURIA",    "rank": 2, "points": 845}
  ]
}
```

### Counts
```json
{
  "players": 1547,
  "teams": 334,
  "matches": 2163
}
```

### Fantasy details
```json
{
  "id": 598,
  "name": "PGL Cluj-Napoca 2026 - Playoffs",
  "salary_cap": 1000,
  "currency": "$",
  "teams": [
    {
      "id": 9565,
      "name": "Vitality",
      "players": [
        {"id": 11893, "name": "zywoo", "cost": 240},
        {"id": 11816, "name": "ropz",  "cost": 215}
      ]
    }
  ]
}
```

---

## 🧪 Examples

### Using curl (Live API)

#### Get all teams
```sh
curl https://api.csapi.de/teams/
```

#### Search for a team by name
```sh
curl "https://api.csapi.de/teams/?name=vitality"
```

#### Get a specific match
```sh
curl https://api.csapi.de/matches/2389666
```

#### Get match player stats broken down per map
```sh
curl "https://api.csapi.de/matches/2389666/stats?by_map=true"
```

#### Get player stats grouped by map
```sh
curl https://api.csapi.de/players/11893/stats/maps
```

#### Get player win stats on a specific map
```sh
curl "https://api.csapi.de/players/stats/win?mapid=2"
```

#### Get team map stats for the last 3 months
```sh
curl https://api.csapi.de/teams/9565/stats
```

#### Get current VRS rankings
```sh
curl https://api.csapi.de/rankings/
```

#### Get paginated matches
```sh
curl "https://api.csapi.de/matches/?limit=20&offset=0"
```

#### Get database counts
```sh
curl https://api.csapi.de/counts/
```

---

## 🧪 Running Tests
```sh
pytest        # run all tests
pytest -v     # verbose output
```

---

## ⚠️ Disclaimer

This project is **not affiliated with HLTV.org**.