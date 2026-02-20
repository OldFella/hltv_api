from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from src.core.config import settings
from src.db.session import engine 
from src.db.base_class import Base
from src.routers import sides,results, teams, matches, maps, goat, players
from fastapi.middleware.cors import CORSMiddleware


def create_tables():
    Base.metadata.create_all(bind=engine)
        

def start_application():
    app = FastAPI(title=settings.PROJECT_NAME,version=settings.PROJECT_VERSION)
    app.add_event_handler("startup", create_tables)  # run on startup, not import
    return app


app = start_application()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://csapi.de"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sides.router)
app.include_router(maps.router)
app.include_router(matches.router)
app.include_router(teams.router)
app.include_router(results.router)
app.include_router(goat.router)
app.include_router(players.router)




@app.get("/")
async def homepage(request: Request):
    return {'Hello':'Welcome to my api service!',
            'docs': "https://api.csapi.de/docs"}
