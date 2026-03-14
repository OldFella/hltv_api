# HLTV API — Project Context

**What it is:** Read-only REST API + SSR frontend exposing CS match, team, and player data scraped from HLTV.org. Data refreshes daily.
**Live:** https://api.csapi.de | https://www.csapi.de
**Stack:** Python · FastAPI · SQLAlchemy · PostgreSQL (`pg_trgm`) · Jinja2 · Docker · Nginx · Pytest · GitHub Actions

---

## Architecture

- **Ports & adapters** — routers depend on ports (Protocols); SQLAlchemy adapters implement them; all queries live in `src/adapters/`
- **Read-only** — GET endpoints only, no mutations
- **Hybrid app** — JSON API (`routers_api.py`) + SSR frontend (`routers_fe.py` / `frontend.py`)
- **Fuzzy search** — powered by pg_trgm `similarity()` via `add_fuzzy_filter()`; used on `name` fields across teams, players
- **Stat rows** — the DB stores stats at multiple granularities controlled by `mapid` and `sideid`: `id=0` means "overall/both"; non-zero means a specific map or side. Query builders default `mapid=None` / `sideid=None` to **exclude** the `id=0` summary rows (filter `!= 0`)
- **Outcome join** — win/loss is not stored directly; it is derived at query time by self-joining `matches` on `matchid` where `teamid != teamid` and comparing scores (`query_outcomes`)
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

### Predict `src/routers/predict.py`
| Endpoint | Params | Notes |
|---|---|---|
| `GET /predict/{team_id_a}/{team_id_b}` | `start_date`, `end_date` (default: last 3 months) | returns `MatchupProbabilities` |

`MatchupProbabilities`:
- `map_win_probs: list[float]` — per-map Bradley-Terry win probabilities (server-side)
- `ranking_win_prob: float` — win probability from HLTV ranking points (server-side)
- Client blends: `alpha * ranking_win_prob + (1 - alpha) * map_win_probs[i]`
- Client runs Monte Carlo simulation via `simulation.js`

### Matches `src/routers/matches.py`
| Endpoint | Params | Notes |
|---|---|---|
| `GET /matches/` | `limit=100`, `offset=0` | |
| `GET /matches/latest` | `limit=10`, `offset=0` | shares `get_matches()` helper with above, differs only in default limit; response includes `team1.rank` and `team2.rank` (derived from latest rankings snapshot) |
| `GET /matches/{matchid}` | — | includes per-map scores + derived `best_of` and `winner` |
| `GET /matches/{matchid}/stats` | `by_map=false` | player stats for both teams; `by_map=true` splits by map |

### Players `src/routers/players.py` *(migrated)*
| Endpoint | Params | Notes |
|---|---|---|
| `GET /players/` | `name` (fuzzy), `limit=20`, `offset=0` | |
| `GET /players/stats` | `mapid=0`, `sideid=0`, `limit=20`, `offset=0`, `min_played=10` | aggregated stats ranked by composite score of rating and experience |
| `GET /players/stats/raw` | `mapid=0`, `sideid=0`, `limit=20`, `offset=0` | raw per-player-per-match rows |
| `GET /players/stats/raw/{outcome}` | `outcome`: `win`\|`lose`, `mapid`, `limit=100`, `offset=0` | filters via outcome subquery |
| `GET /players/{playerid}` | `start_date`, `end_date` (default: last 3 months) | aggregated stats + current team |
| `GET /players/{playerid}/stats/{group}` | `group`: `maps`\|`sides`\|`events`, `mapid`, `start_date`, `end_date` | `mapid` only applies for `sides`/`events` |

### Reference Data `src/routers/reference_data.py` *(migrated)*
| Endpoint | Params | Notes |
|---|---|---|
| `GET /sides/` | — | |
| `GET /sides/{sideid}` | — | |
| `GET /maps/` | — | |
| `GET /maps/{mapid}` | — | |
| `GET /fantasy/` | — | |
| `GET /fantasy/{fantasyid}` | — | includes teams, players, costs (salary cap $1,000) |
| `GET /rankings/` | `date` (optional) | defaults to most recent snapshot; returns `date` + ordered list of `{id, name, rank, points}` |
| `GET /counts/` | — | returns `{players, teams, matches}` as distinct counts from DB; used by homepage hero stats |

---

## Ports & Adapters `src/domain/`

### Domain Models `src/domain/models.py`
| Model | Shape |
|---|---|
| `Item` | `{id, name}` |
| `Side(Item)` | `{id, name}` |
| `Map(Item)` | `{id, name}` |
| `TeamRank(Item)` | `{id, name, rank, points}` |
| `Ranking` | `{date, rankings: list[TeamRank]}` |
| `FantasyPlayer(Item)` | `{id, name, cost}` |
| `FantasyTeam(Item)` | `{id, name, players: list[FantasyPlayer]}` |
| `Fantasy(Item)` | `{id, name, salary_cap, currency, teams: list[FantasyTeam]}` |
| `CountResponse` | `{players, teams, matches}` |
| `PlayerStatRow(Item)` | `{id, name, team_id, team_name, k, d, swing, adr, kast, rating, N}` |
| `PlayerStats` | `{k, d, swing, adr, kast, rating, N}` |
| `PlayerDetail(Item)` | `{id, name, team: Item, stats: PlayerStats}` |
| `PlayerGroupedStats` | `{id, name, k, d, swing, adr, kast, rating, N}` |
| `PlayerAggregatedStats(Item)` | `{id, name, rank, k, d, swing, adr, kast, rating, N}` |
| `TeamMapStats` | `{id, name, n, n_wins}` |
| `MatchupProbabilities` | `{map_win_probs: list[float], ranking_win_prob: float}` |

### Ports `src/domain/ports.py`
| Port | Methods |
|---|---|
| `ReadPort[T]` | `get_all() -> list[T]`, `get_one(id) -> T \| None` |
| `RankingsPort` | `get_rankings(date) -> Ranking \| None` |
| `CountsPort` | `get_counts() -> CountResponse` |
| `TeamsPort` | `get_all_fuzzy(name, limit, offset)`, `get_one(teamid, start_date, end_date)`, `get_matchhistory(teamid, limit, offset)`, `get_stats(teamid, start_date, end_date)` |
| `PlayersPort` | `get_all_fuzzy(name, limit, offset)`, `get_one(playerid, start_date, end_date)`, `get_stats(mapid, sideid, limit, offset)`, `get_stats_by_outcome(outcome, mapid, limit, offset)`, `get_grouped_stats(playerid, group, mapid, start_date, end_date)`, `get_aggregated_stats(mapid, sideid, limit, offset, min_played)` |

### Errors `src/domain/errors.py`
- `DomainError` — base exception
- `NotFoundError(DomainError)` — raised by use cases when adapter returns `None`; mapped to HTTP 404 in `main.py`

### Use Cases `src/domain/use_cases.py`
| Function | Signature |
|---|---|
| `get_all` | `(port: ReadPort[T]) -> list[T]` |
| `get_one` | `(port: ReadPort[T], id: int, label: str) -> T` |
| `get_rankings` | `(port: RankingsPort, date: date \| None = None) -> Ranking` |
| `get_counts` | `(port: CountsPort) -> CountResponse` |
| `get_all_fuzzy` | `(port: TeamsPort \| PlayersPort, name, limit, offset) -> list[Item]` |
| `get_team` | `(port: TeamsPort, teamid, start_date, end_date) -> TeamDetail` |
| `get_team_matchhistory` | `(port: TeamsPort, teamid, limit, offset) -> list[MatchResult]` |
| `get_team_stats` | `(port: TeamsPort, teamid, start_date, end_date) -> list[TeamMapStats]` |
| `get_map_win_probs` | `(teams_port: TeamsPort, rankings_port: RankingsPort, team_id_a, team_id_b, start_date, end_date) -> MatchupProbabilities` |
| `get_player` | `(port: PlayersPort, playerid, start_date, end_date) -> PlayerDetail` |
| `get_player_stats` | `(port: PlayersPort, mapid, sideid, limit, offset) -> list[PlayerStatRow]` |
| `get_player_stats_by_outcome` | `(port: PlayersPort, outcome, mapid, limit, offset) -> list[PlayerStatRow]` |
| `get_player_grouped_stats` | `(port: PlayersPort, playerid, group, mapid, start_date, end_date) -> list[PlayerGroupedStats]` |
| `get_aggregated_stats` | `(port: PlayersPort, mapid, sideid, limit, offset, min_played) -> list[PlayerAggregatedStats]` |

---

## Adapters

### `src/adapters/sqlalchemy_reference_data.py`
| Adapter | Implements | Notes |
|---|---|---|
| `SqlAlchemyReadAdapter` | `ReadPort[T]` | generic; configured with `table`, `id_col`, `name_col`, `model` at instantiation |
| `SqlAlchemyRankingsAdapter` | `RankingsPort` | derives rank via `RANK() OVER (ORDER BY points DESC)`; defaults to `max(date)` when no date passed |
| `SqlAlchemyFantasyAdapter` | `ReadPort[Fantasy]` | `get_all` uses `query_all` helper; `get_one` runs two queries + groups players by team |
| `SqlAlchemyCountsAdapter` | `CountsPort` | three count queries; returns `CountResponse` |

### `src/adapters/sqlalchemy_teams.py`
| Adapter | Implements | Notes |
|---|---|---|
| `SqlAlchemyTeamsAdapter` | `TeamsPort` | `get_all_fuzzy`, `get_one`, `get_matchhistory`, `get_stats` |

### `src/adapters/sqlalchemy_players.py`
| Adapter | Implements | Notes |
|---|---|---|
| `SqlAlchemyPlayersAdapter` | `PlayersPort` | all query builders live in this file; no imports from `repositories/` |

#### Query Builders `src/adapters/sqlalchemy_players.py`
| Function | Notes |
|---|---|
| `query_current_team(playerid)` | resolves team from player's most recent match |
| `query_player_stats(...)` | flexible builder; aggregates with `avg()`/`sum()` when `group_by` set; `sum_fields` overrides specific cols to use `SUM`; `mapid=None`/`sideid=None` excludes id=0 rows |
| `query_outcomes()` | self-joins `matches` aliased `m1`/`m2`; labels each `(matchid, mapid, teamid)` as `win=1` or `win=0`; filters to `sideid=0` |
| `query_player_stats_by_outcome(mode, mapid, sideid)` | wraps `query_player_stats` and joins `query_outcomes()` subquery |

### `src/adapters/sqlalchemy_helpers.py`
| Function | Notes |
|---|---|
| `add_fuzzy_filter(col, value, filters, order_bys, threshold=0.3)` | appends pg_trgm similarity filter + ordering when value is provided |
| `query_all_fuzzy(conn, table, id_col, name_col, name, limit, offset)` | shared fuzzy name search helper used by players and teams adapters |

---

## Math / Model `src/utils/stats.py`
Pure math helpers used by `get_map_win_probs` use case:
- `strength_maps(n_wins, n, c=5, K=400)` — Bradley-Terry strength from map stats with Laplace smoothing
- `ranking_strength(points, K=400)` — `(points / 1000) * K`
- `bradley_terry(R_i, R_j, base=10, K=400)` — win probability from strengths
- `softmax_t(x, tau)` — temperature softmax for map draft simulation

---

## Response Models `src/db/models.py` *(legacy — used by unmigrated endpoints)*

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

## Repositories *(legacy — used by unmigrated endpoints)*

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

### `src/repositories/player_repository.py` *(legacy — kept for reference until fully removed)*
- `FIELDS` — API key → DB column: `k→k`, `d→d`, `swing→roundswing`, `adr→adr`, `kast→kast`, `rating→rating`
- `GROUP_CONFIG` — maps format mode to id/name field names: `players`, `players_w_teams`, `maps`, `sides`, `events`
- `default_date_range()` — returns `(today - 3 months, today)`
- `format_stats(rows, group)` — rounds stats to 3dp, reshapes via `GROUP_CONFIG`, appends `maps_played` from `n`

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

### Predict Page (`/matchup-predictor`)
- **Template:** `templates/predict.html` extends `base.html`
- **Layout:** Two-card `home-grid` — Match Setup + Result
- **Features:** Team autocomplete search, BO1/3/5 format selector, rankings toggle, advanced settings (alpha slider + tooltip, tau slider + tooltip, n_simulations number input)
- **Flow:** `GET /predict/{a}/{b}` → client blends with alpha → `mc_sim()` → `outcomeToResult()` → animated bars
- **Outcome order:** `2-0, 2-1, 1-2, 0-2` — sorted in `outcomeToResult` by score descending
- **Bar width:** Scaled relative to max probability outcome (not raw %)
- **Tooltips:** `.tooltip` with `data-tip` attribute; appears to the right, width 160px, stays within card

---

## Frontend Design System
- **Theme:** CS2 tactical dark theme with gold accent (`--accent`), cyan secondary
- **Fonts:** `--font-display` (Bebas Neue), `--font-mono` (DM Mono), `--font-body`
- **Components:** `.hero`, `.card`, `.card-title`, `.section-label`, `.badge`, `.panel`, `.button`, `.nav-link`, `.home-grid`
- **Mobile:** Burger button (staggered 3-line design) → right-side sliding sidebar (280px) with overlay backdrop; sidebar links have left accent border on active
- **CSS variables:** `--bg`, `--surface`, `--surface-2`, `--chrome`, `--border`, `--border-bright`, `--accent`, `--accent-rgb`, `--muted`, `--text`, `--text-bright`, `--win`, `--danger`, `--cyan`

---

## Frontend Asset Files

| File | Purpose |
|---|---|
| `variables.css` | CSS custom properties / design tokens |
| `styles.css` | Global layout, header, hero, cards, buttons, footer, sidebar |
| `matches.css` | Match cards, score rows, map chips, rankings panel |
| `animation.css` | All keyframe animations; matches fade left, rankings fade right |
| `base.js` | Theme toggle logic, last-updated fetch, mobile sidebar open/close |
| `main.js` | Homepage: fetches counts, rankings, matches; renders cards |
| `simulation.js` | Client-side MC simulation ES module: `mc_sim`, `outcomeToResult`, `scoreToLabel` |
| `header.html` | Header template with crosshair logo + nav + burger button |
| `footer.html` | Footer template |
| `base.html` | Base template; inlines CSS/JS via `{% include %}`; sidebar markup included |

---

## Key Files
| Path | Purpose |
|---|---|
| `src/main.py` | FastAPI app entry point; registers `NotFoundError` → 404 exception handler |
| `src/frontend.py` | Jinja2 SSR routes |
| `src/core/config.py` | App settings from `.env` |
| `src/db/session.py` | SQLAlchemy engine setup |
| `src/db/get_db.py` | `get_db` — yields `Connection` per request via `Depends` |
| `src/config/active_maps.py` | `ACTIVE_MAPS: dict[int, str]` — map_id → name |
| `src/config/fantasy.py` | `SALARY_CAP`, `CURRENCY` constants |
| `src/config/routers_api.py` | API router registration |
| `src/config/routers_fe.py` | Frontend router registration |

---

## Tests
- `TestClient(app, raise_server_exceptions=False)` — required to test 500 responses without re-raising
- Teams router tests mock `src.routers.teams.use_cases.*` functions
- Test fixtures use domain model objects (`TeamDetail`, `MatchResult`, etc.) as mock return values

---

## Dev Commands
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000   # local dev
pip install -r requirements-dev.txt
pytest / pytest -v
```
Config: `.env` + `src/core/.env`

---

## Pending / Future Work
- Single-elimination bracket simulator (exact probability propagation)
- HLTV fantasy player performance prediction
- Wire remaining nav links (Teams, Matches, Players, Rankings pages)