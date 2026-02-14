# HLTV API

A RESTful API for exposing Counter-Strike match and team data gathered with an HLTV scraper.  
Built in Python, this API provides structured endpoints for accessing HLTV.org–derived data for use in analytics tools, bots, dashboards, or other applications.

> **Website:** https://www.csapi.de  
> **Live API:** https://api.csapi.de  
> **Status:** Active, read-only API

---

## 🚀 Features

### Teams
- Get a list of all teams
- Look up a team name by ID
- Look up a team ID by name

### Matches
- Retrieve all matches
- Retrieve a specific match by ID
- Retrieve match maps with scores
- Get match winner information

### API Design
- Read-only (GET requests only)
- Simple RESTful endpoints
- JSON responses

### Update Frequency

>All data provided by this API is refreshed once per day, so recent matches or roster changes may take up to 24 hours to appear.

---

## 🧰 Tech Stack

- **Language:** Python
- **Web Framework:** FastAPI
- **ASGI Server:** Uvicorn / Gunicorn
- **Reverse Proxy / Web Server:** Nginx
- **Data Source:** HLTV.org
- **API Style:** REST
- **Response Format:** JSON
- **Deployment:** Self-hosted (Linux server + Docker)
- **Version Control:** Git + GitHub

---

## 🌍 Base URL
https://www.csapi.de/

---

## 📦 Installation (Local Development)

Clone the repository and install dependencies:

```sh
git clone https://github.com/OldFella/hltv_api.git
cd hltv_api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🛠 Usage

Run the API locally:
```sh
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```
By default, the local API will be available at:

http://localhost:8000

---

## 📌 API Endpoints

### Teams

| Endpoint                               | Description                       |
| -------------------------------------- | --------------------------------- |
| `/teams/<?teamname>`                   | Get all teams                     |
| `/teams/id/<teamid>`                   | Get team name by ID               |

### Matches

| Endpoint                                         | Description                 |
| ------------------------------------------------ | --------------------------- |
| `/matches/`                                      | Get all matches             |
| `/matches/matches/?limit=<limit>&offset=<offset>`| Get all matches with paging |
| `/matches/<matchid>`                             | Get a match result by ID    |
| `/matches/<matchid>/maps`                        | Get a map results by ID     |

---

## 📄 Example Responses
### Match with maps and winner

```json
{
  "id": 2389666,
  "team1": {"id": 8297, "name": "FURIA", "score": 1},
  "team2": {"id": 9565, "name": "Vitality", "score": 3},
  "date": "2026-02-08",
  "event": "IEM Kraków 2026",
  "maps": [
    {"id": 2, "name": "ovp", "team1_score": 10, "team2_score": 13},
    {"id": 5, "name": "nuke", "team1_score": 2, "team2_score": 13},
    {"id": 6, "name": "mrg", "team1_score": 13, "team2_score": 11},
    {"id": 7, "name": "inf", "team1_score": 8, "team2_score": 13}
  ],
  "best_of": 5,
  "winner": {"id": 9565, "name": "Vitality"}
}
```

---

## 🧪 Examples
### Using curl (Live API)

#### Get all teams
```sh 
curl https://api.csapi.de/teams/
```

#### Get a specific match
```sh
curl https://api.csapi.de/matches/2389666
```

#### Get match maps
```sh
curl https://api.csapi.de/matches/2389666/maps
```

#### Get paginated matches
```sh
curl "https://api.csapi.de/matches/all/?limit=20&offset=0"
```
---

## ⚠️ TODO

- Add **player stats for the matches** (per match/map performance)
- Add **player stats** (overall player info, rankings, etc.)
- Add pagination and filtering for `/matches/`
- Build Fantasy Spreadsheets on the fly

---

## ⚠️ Disclaimer

This project is **not affiliated with HLTV.org**.