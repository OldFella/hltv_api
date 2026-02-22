# HLTV API
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

### Matches
- Retrieve all matches with pagination
- Retrieve latest matches
- Retrieve a specific match by ID including maps and scores
- Get player stats for a match, optionally broken down per map

### Players
- Get a list of all players with fuzzy name search
- Look up a player by ID including current team and overall stats
- Get average player stats over a date range
- Get player stats grouped by map, side, or event

### Fantasy
- Get all available fantasies
- Get fantasy details including teams, players and costs
- Salary cap: $1,000 (costs expressed in units of $1,000)

### Maps & Sides
- Get all maps
- Get all sides

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
| Endpoint                           | Description                              |
| ---------------------------------- | ---------------------------------------- |
| `GET /teams/`                      | Get all teams (supports `?name=`)        |
| `GET /teams/{teamid}`              | Get team by ID with roster and streak    |
| `GET /teams/{teamid}/matchhistory` | Get match history for a team             |

### Matches
| Endpoint                      | Description                           |
| ----------------------------- | ------------------------------------- |
| `GET /matches/`               | Get all matches                       |
| `GET /matches/latest`         | Get latest matches (default limit 10) |
| `GET /matches/{matchid}`      | Get a match by ID                     |
| `GET /matches/{matchid}/stats`| Get player stats for a match (`?by_map=true` for per-map breakdown) |

### Players
| Endpoint                                | Description                                         |
| --------------------------------------- | --------------------------------------------------- |
| `GET /players/`                         | Get all players (supports `?name=`)                 |
| `GET /players/stats`                    | Get stats for all players                           |
| `GET /players/{playerid}`               | Get player by ID with current team and overall stats|
| `GET /players/{playerid}/stats/{group}` | Get stats grouped by `maps`, `sides`, or `events`   |

### Fantasy
| Endpoint                  | Description                        |
| ------------------------- | ---------------------------------- |
| `GET /fantasy/`           | Get all available fantasies        |
| `GET /fantasy/{fantasyid}`| Get fantasy details with teams and player costs |

### Maps & Sides
| Endpoint           | Description      |
| ------------------ | ---------------- |
| `GET /maps/`       | Get all maps     |
| `GET /maps/{id}`   | Get map by ID    |
| `GET /sides/`      | Get all sides    |
| `GET /sides/{id}`  | Get side by ID   |

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
    {"id": 7322, "name": "apex"},
    {"id": 18462, "name": "mezii"},
    {"id": 16693, "name": "flamez"},
    {"id": 11816, "name": "ropz"}
  ]
}
```

### Match with maps and winner
```json
{
  "id": 2389666,
  "team1": {"id": 8297, "name": "FURIA", "score": 1},
  "team2": {"id": 9565, "name": "Vitality", "score": 3},
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

#### Get paginated matches
```sh
curl "https://api.csapi.de/matches/?limit=20&offset=0"
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