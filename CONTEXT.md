# Project Context: HLTV API

## Overview
A read-only RESTful API that exposes Counter-Strike match, team, and player data scraped from HLTV.org. Data is refreshed once per day. The project also serves a frontend via Jinja2 templates (hybrid API + SSR app).

- **Live API:** https://api.csapi.de
- **Website:** https://www.csapi.de
- **Status:** Active, in development

---

## Tech Stack
- **Language:** Python
- **Framework:** FastAPI
- **ASGI Server:** Uvicorn / Gunicorn
- **Reverse Proxy:** Nginx
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Deployment:** Self-hosted Linux server via Docker (`Dockerfile.api`, `Dockerfile.frontend`, `compose.api.yaml`)
- **Tests:** Pytest (`pytest.ini`, `tests/`)
- **CI:** GitHub Actions (`.github/workflows/tests.yml`)

---

## Project Structure
```
src/
├── main.py                  # FastAPI app entry point
├── frontend.py              # Jinja2 SSR frontend routes
├── config/
│   ├── endpoints.py         # Endpoint definitions/constants
│   ├── example_requests.py  # Example request data
│   ├── hero_card.py         # Hero card config (likely for frontend)
│   ├── routers_api.py       # API router registration
│   └── routers_fe.py        # Frontend router registration
├── core/
│   ├── config.py            # App settings (reads from .env)
│   └── __init__.py
├── db/
│   ├── base_class.py        # SQLAlchemy declarative base
│   ├── classes.py           # DB class helpers
│   ├── models.py            # SQLAlchemy ORM models
│   ├── session.py           # DB session / engine setup
│   └── spreadsheets/        # ODS spreadsheet data files (591–598)
├── repositories/
│   ├── base.py              # Base repository with shared query logic
│   ├── match_repository.py  # Match-specific DB queries
│   └── player_repository.py # Player-specific DB queries
├── routers/
│   ├── matches.py           # /matches endpoints
│   ├── players.py           # /players endpoints
│   ├── teams.py             # /teams endpoints
│   ├── fantasy.py           # /fantasy endpoints
│   ├── maps.py              # /maps endpoints
│   ├── sides.py             # /sides endpoints
│   ├── download.py          # /download endpoints
│   ├── goat.py              # /goat endpoints
│   └── spreadsheets.py      # /spreadsheets endpoints
├── templates/               # Jinja2 HTML templates (SSR frontend)
└── static/                  # Static files and downloadable ODS files

tests/
├── unit/
|   ├── conftest.py
|   ├── repositories/        # Tests for base, match, player repositories
|   └── routers/             # Tests for all routers
└── endpoints/               # Tests for all endpoints against the database
```

---

## Architecture Patterns
- **Repository pattern:** DB access is abstracted into repository classes (`src/repositories/`). Routers call repositories, not the DB directly.
- **Router-based structure:** Each domain (matches, players, teams, etc.) has its own FastAPI router file.
- **Hybrid app:** The app serves both a JSON API (`routers_api.py`) and an SSR frontend with Jinja2 templates (`routers_fe.py`, `frontend.py`).
- **Read-only API:** All endpoints are GET only. No mutations.

---

## API Domains & Key Endpoints

### Teams
- `GET /teams/` — all teams, supports `?name=` fuzzy search
- `GET /teams/{teamid}` — team by ID with roster and win/loss streak
- `GET /teams/{teamid}/matchhistory` — match history for a team

### Matches
- `GET /matches/` — all matches (paginated)
- `GET /matches/latest` — latest matches (default limit 10)
- `GET /matches/{matchid}` — match by ID with maps and scores
- `GET /matches/{matchid}/stats` — player stats for a match (`?by_map=true` for per-map breakdown)

### Players
- `GET /players/` — all players, supports `?name=` fuzzy search
- `GET /players/stats` — stats for all players
- `GET /players/{playerid}` — player by ID with team and overall stats
- `GET /players/{playerid}/stats/{group}` — stats grouped by `maps`, `sides`, or `events`

### Fantasy
- `GET /fantasy/` — all available fantasies
- `GET /fantasy/{fantasyid}` — fantasy details with teams, players, costs (salary cap: $1,000)

### Maps & Sides
- `GET /maps/`, `GET /maps/{id}`
- `GET /sides/`, `GET /sides/{id}`

---

## Key Data Models (from JSON examples)
- **Team:** `id`, `name`, `streak`, `roster[]`
- **Match:** `id`, `team1`, `team2`, `date`, `event`, `maps[]`, `best_of`, `winner`
- **Player:** `id`, `name`, `team`, `stats` (k, d, swing, adr, kast, rating, maps_played)
- **Fantasy:** `id`, `name`, `salary_cap`, `currency`, `teams[]` with players and costs

---

## Development Notes
- Local dev: `uvicorn src.main:app --reload --host 0.0.0.0 --port 8000`
- Install deps: `pip install -r requirements-dev.txt`
- Run tests: `pytest` or `pytest -v`
- Environment config lives in `.env` and `src/core/.env`
- Data source is HLTV.org (not affiliated); scraped data, refreshed daily
- ODS spreadsheet files are stored in `src/db/spreadsheets/` and served via `src/static/downloads/`