# HLTV API

A RESTful API for exposing Counter-Strike match and team data gathered with an HLTV scraper.  
Built in Python, this API provides structured endpoints for accessing HLTV.org–derived data for use in analytics tools, bots, dashboards, or other applications.

> **Live API:** http://csapi.de  
> **Status:** Active, read-only API

---

## 🚀 Features

### Teams
- Get a list of all teams
- Look up a team name by ID
- Look up a team ID by name
- Retrieve a team’s match history
- Filter match history by opponent

### Matches
- Retrieve all matches
- Retrieve a specific match by ID

### API Design
- Read-only (GET requests only)
- Simple RESTful endpoints
- JSON responses

---

## 🧰 Tech Stack

- **Language:** Python
- **Web Framework:** FastAPI
- **ASGI Server:** Uvicorn / Gunicorn
- **Reverse Proxy / Web Server:** Nginx
- **Data Source:** HLTV.org
- **API Style:** REST
- **Response Format:** JSON
- **Deployment:** Self-hosted (Linux server)
- **Version Control:** Git + GitHub

---

## 🌍 Base URL
http://csapi.de/

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

python app.py


By default, the local API will be available at:

http://localhost:8000

---

## 📌 API Endpoints

### Teams

| Endpoint                               | Description                       |
| -------------------------------------- | --------------------------------- |
| `/teams/all/`                          | Get all teams                     |
| `/teams/id/<teamid>`                   | Get team name by ID               |
| `/teams/name/<teamname>`               | Get team ID by name               |
| `/teams/matchhistory/<team>`           | Get match history for a team      |
| `/teams/matchhistory/<team>?vs=<team>` | Get match history vs another team |

### Matches

| Endpoint             | Description       |
| -------------------- | ----------------- |
| `/matches/all/`      | Get all matches   |
| `/matches/<matchid>` | Get a match by ID |

---

## 🧪 Examples
### Using curl (Live API)

#### Get all teams
curl http://csapi.de/teams/all/

#### Get a specific match
curl http://csapi.de/matches/12345

---

## ⚠️ Disclaimer

This project is **not affiliated with HLTV.org**.