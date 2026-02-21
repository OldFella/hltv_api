from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from src.core.config import settings
from src.db.session import engine 
from src.db.base_class import Base
from src.config.routers_api import include_routers
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
    allow_origins=["https://csapi.de","https://www.csapi.de"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

include_routers(app)

@app.get("/")
async def homepage(request: Request):
    return {'Hello':'Welcome to my api service!',
            'docs': "https://api.csapi.de/docs"}

@app.get("/status")
def status():
    with open("last_updated.txt") as f:
        return {"updated_at": f.read().strip()}