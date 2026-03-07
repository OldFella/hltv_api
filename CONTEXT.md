# HLTV API — Project Context

**What it is:** Read-only REST API + SSR frontend exposing CS match, team, and player data scraped from HLTV.org. Data refreshes daily.
**Live:** https://api.csapi.de | https://www.csapi.de
**Stack:** Python · FastAPI · SQLAlchemy · PostgreSQL (`pg_trgm`) · Jinja2 · Docker · Nginx · Pytest · GitHub Actions

---

## Architecture

- **Repository pattern** — routers never touch the DB directly; all queries live in `src/repositories/`
- **Read-only** — GET endpoints only, no mutations
- **Hybrid app** — JSON API (`routers_api.py`) + SSR frontend (`routers_fe.py` / `frontend.py`)
- **Fuzzy search** — powered by pg_trgm `similarity()` via `add_fuzzy_filter()`; used on `name` fields across teams, players
- **Stat rows** — the DB stores stats at multiple granularities controlled by `mapid` and `sideid`: `id=0` means "overall/both"; non-zero means a specific map or side. Query builders default `mapid=None` / `sideid=None` to **exclude** the `id=0` summary rows (filter `!= 0`)
- **Outcome join** — win/loss is not stored directly; it is derived at query time by self-joining `matches` on `matchid` where `teamid != teamid` and comparing scores (`build_outcome_query`)
- **Active maps** — `ACTIVE_MAPS` (config) is materialised as a VALUES subquery in team stats so every active map always appears in results even with zero matches

---

## Endpoints

### Teams `src/routers/teams.py`
| Endpoint | Params | Notes |
|---|---|---|
| `GET /teams/` | `name` (fuzzy), `limit=20`, `offset=0` | |
| `GET /teams/{teamid}` | — | includes roster (from most recent match) + win/loss streak |
| `GET /teams/{teamid}/matchhistory` | `limit=5`, `offset=0` | |
| `GET /teams/{teamid}/stats` | `start_date`, `end_date` (default: last 3 months) | per-map win/loss counts across all active maps |

### Matches `src/routers/matches.py`
| Endpoint | Params | Notes |
|---|---|---|
| `GET /matches/` | `limit=100`, `offset=0` | |
| `GET /matches/latest` | `limit=10`, `offset=0` | shares `get_matches()` helper with above, differs only in default limit; response includes `team1.rank` and `team2.rank` (derived from latest rankings snapshot) |
| `GET /matches/{matchid}` | — | includes per-map scores + derived `best_of` and `winner` |
| `GET /matches/{matchid}/stats` | `by_map=false` | player stats for both teams; `by_map=true` splits by map |

### Players `src/routers/players.py`
| Endpoint | Params | Notes |
|---|---|---|
| `GET /players/` | `name` (fuzzy), `limit=20`, `offset=0` | |
| `GET /players/stats` | `mapid=0`, `sideid=0`, `limit=20`, `offset=0` | raw per-player-per-match rows |
| `GET /players/stats/{outcome}` | `outcome`: `win`\|`lose`, `mapid`, `limit=100`, `offset=0` | filters via outcome subquery |
| `GET /players/{playerid}` | `start_date`, `end_date` (default: last 3 months) | aggregated stats + current team |
| `GET /players/{playerid}/stats/{group}` | `group`: `maps`\|`sides`\|`events`, `mapid`, `start_date`, `end_date` | `mapid` only applies for `sides`/`events` |

### Rankings `src/routers/rankings.py`
| Endpoint | Params | Notes |
|---|---|---|
| `GET /rankings/` | — | most recent VRS snapshot; returns `date` + ordered list of `{id, name, rank, points}` |

### Counts `src/routers/counts.py` *(new)*
| Endpoint | Params | Notes |
|---|---|---|
| `GET /counts/` | — | returns `{players, teams, matches}` as distinct counts from DB; used by homepage hero stats |

### Other
- `GET /fantasy/`, `GET /fantasy/{fantasyid}` — fantasy details with teams, players, costs (salary cap $1,000)
- `GET /maps/`, `GET /maps/{id}`
- `GET /sides/`, `GET /sides/{id}`
- `GET /download/`, `GET /spreadsheets/`, `GET /goat/`

---

## Response Models `src/db/models.py`

| Model | Shape |
|---|---|
| `Item` | `{id, name}` |
| `TeamResponse` | `{id, name, streak: int, roster: Item[]}` |
| `MatchResponse` | `{id, team1, team2, date, event, maps[], best_of, winner}` — team objects include `rank` field |
| `MatchStats` | per-map `{id, name, team1: {players[]}, team2: {players[]}}` |
| `PlayerResponse` | `{id, name, team: Item, stats: {k,d,swing,adr,kast,rating,maps_played}}` |
| `PlayerStats` | raw stat row with optional team fields |
| `GroupedStats` | stat row reshaped by group dimension |
| `Ranking` | `{date, rankings: [{id, name, rank, points}]}` |

---

## Repositories

### `src/repositories/base.py`
- `execute_query(stmt, *, many=True)` — runs statement, raises **HTTP 404** if no rows; pass `many=False` to get single mapping
- `add_fuzzy_filter(col, value, filters, order_bys, threshold=0.3)` — no-op when `value` is None; otherwise appends `similarity() > threshold` filter and `similarity().desc()` ordering in-place

### `src/repositories/match_repository.py`
- `build_match_query(matchid, teamid, vsid, sideid, mapid, limit, offset)` — self-joins `matches` aliased as `m1`/`m2` to pair team1/team2; aggregates maps as JSON via `array_agg`; orders by `date desc, matchid desc`; joins `rankings` subquery twice (aliased `r1`/`r2`) to add `team1_rank`/`team2_rank` — rank is computed via `RANK() OVER (ORDER BY points DESC)` on the latest rankings date, LEFT JOIN so unranked teams return `null`
- `build_match_stats_query(matchid, by_map)` — aggregates player stats per map as JSON array; filters `sideid=0`; adds `mapid=0` filter when `by_map=False`
- `build_roster_query(teamid)` — resolves players from team's single most recent match
- `format_matches(rows)` — parses `maps` array, splits out `id=0` overall score row, computes `best_of = (2 * max_score) - 1`, derives `winner`
- `format_match_stats(rows, by_map)` — reshapes flat player rows into `{team1: {players[]}, team2: {players[]}}` structure per map
- `get_streak(match_history, teamid)` — returns positive int for win streak, negative for loss streak

### `src/repositories/player_repository.py`
- `FIELDS` — API key → DB column: `k→k`, `d→d`, `swing→roundswing`, `adr→adr`, `kast→kast`, `rating→rating`
- `GROUP_CONFIG` — maps format mode to id/name field names: `players`, `players_w_teams`, `maps`, `sides`, `events`
- `default_date_range()` — returns `(today - 3 months, today)`
- `format_stats(rows, group)` — rounds stats to 3dp, reshapes via `GROUP_CONFIG`, appends `maps_played` from `n`
- `build_team_query(playerid)` — resolves current team from player's most recent match
- `build_player_stats_query(playerid, mapid, sideid, matchid, event, start_date, end_date, group_by, include_teams, ps)`:
  - when `group_by` is set → aggregates with `avg()`; otherwise returns raw per-row stats
  - `mapid=None` → excludes `mapid=0` rows; `sideid=None` → excludes `sideid=0` rows
  - `group_by` accepts list of `maps`, `sides`, `events`
  - `include_teams=True` adds `team_id`/`team_name` to selects
- `build_outcome_query()` — self-joins `matches` to label each `(matchid, mapid, teamid)` row as `win=1` or `win=0`; filters to `sideid=0`
- `build_player_stats_query_outcome(mode, mapid, sideid)` — wraps `build_player_stats_query` and joins outcome subquery, filtering to `win=1` (win) or `win=0` (lose)

### `src/repositories/team_repository.py`
- `build_team_stats_query(teamid, start_date, end_date)`:
  - builds `ACTIVE_MAPS` as a VALUES subquery so all active maps always appear
  - joins `build_outcome_query()` subquery to count wins
  - left-joins stats onto active maps → maps with no data return `n=0, n_wins=0`

---

## DB Tables `src/db/classes.py`
`teams` · `players` · `matches` · `match_overview` · `player_stats` · `maps` · `sides` · `rankings`

Note: `rankings` table schema is `{teamid, points, date}` — rank is **not stored**, it is derived at query time via `RANK() OVER (ORDER BY points DESC)` filtered to `max(date)`.

---

## Frontend `src/frontend.py`

SSR pages use Jinja2 templates. All `TemplateResponse` calls use the new signature: `TemplateResponse(request, "template.html", {...})`.

Every route passes `current_page` string to templates for active nav highlighting.

### Homepage (`/`)
- Hero section with live stat counters fetched from `GET /counts/`
- Two-panel layout: World Rankings (fixed 300px) + Latest Results (flex)
- Rankings: top 10 from `GET /rankings/`, staggered fade-in from right
- Matches: 3 most recent from `GET /matches/latest`, staggered fade-in from left; each card shows team names, ranks (`#N`), series score, map chips with per-map scores
- API banner below cards linking to `api.csapi.de/docs`
- Endpoints card removed from homepage

---

## Frontend Asset Files

| File | Purpose |
|---|---|
| `variables.css` | CSS custom properties / design tokens |
| `styles.css` | Global layout, header, hero, cards, buttons, footer |
| `matches.css` | Match cards, score rows, map chips, rankings panel |
| `animation.css` | All keyframe animations; matches fade left, rankings fade right |
| `theme-toggle.css` | Theme toggle button styles (merge into styles.css) |
| `base.js` | Theme toggle logic, last-updated fetch |
| `main.js` | Homepage: fetches counts, rankings, matches; renders cards |
| `header.html` | Header template with crosshair logo + nav |
| `footer.html` | Footer template |
| `base.html` | Base template; inlines CSS/JS via `{% include %}`; applies saved theme before render to prevent flash |

---

## Key Files
| Path | Purpose |
|---|---|
| `src/main.py` | FastAPI app entry point |
| `src/frontend.py` | Jinja2 SSR routes |
| `src/core/config.py` | App settings from `.env` |
| `src/db/session.py` | SQLAlchemy engine setup |
| `src/config/active_maps.py` | `ACTIVE_MAPS: dict[int, str]` — map_id → name |
| `src/config/routers_api.py` | API router registration |
| `src/config/routers_fe.py` | Frontend router registration |

---

## Dev Commands
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000   # local dev
pip install -r requirements-dev.txt
pytest / pytest -v
```
Config: `.env` + `src/core/.env`