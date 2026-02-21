from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from core.config import settings
from db.session import engine 
from db.base_class import Base
from routers import spreadsheets, results, download
from src.config.endpoints import endpoints
from src.config.hero_card import hero_card
from src.config.example_requests import example_requests
from pathlib import Path


def create_tables():
    Base.metadata.create_all(bind=engine)
        

def start_application():
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        docs_url=None,       
        redoc_url=None,      
        openapi_url=None)
    app.add_event_handler("startup", create_tables) 
    return app


app = start_application()

app.include_router(spreadsheets.router)
app.include_router(results.router)
app.include_router(download.router)



BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse(
    request,
    "404.html",
    status_code=404
)


@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request,
        "api_base": "https://api.csapi.de",
        "endpoints": endpoints,
        "hero_card": hero_card,
        "example_requests": example_requests},
    )
