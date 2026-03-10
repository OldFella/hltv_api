from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from src.core.config import settings
from src.db.session import engine 
from src.db.base_class import Base
from src.config.routers_api import include_routers
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.domain.errors import NotFoundError


def create_tables():
    Base.metadata.create_all(bind=engine)
        

def start_application():
    app = FastAPI(title=settings.PROJECT_NAME,version=settings.PROJECT_VERSION)
    app.add_event_handler("startup", create_tables)  # run on startup, not import
    return app

app = start_application()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://csapi.de","https://www.csapi.de"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

include_routers(app)

@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.get("/")
async def homepage(request: Request):
    return {
        "name": "CSAPI",
        "description": "CS2 pro match, team and player data. No key required.",
        "docs": "https://api.csapi.de/docs",
        "base_url": "https://api.csapi.de",
        "endpoints": {
            "matches": "/matches/latest",
            "rankings": "/rankings/",
            "players": "/players/stats",
            "teams": "/teams/",
            "counts": "/counts/"
        }
    }

@app.get("/status")
def status():
    with open("last_updated.txt") as f:
        return {"updated_at": f.read().strip()}