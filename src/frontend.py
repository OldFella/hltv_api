from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from src.core.config import settings
from src.db.session import engine 
from src.db.base_class import Base
from src.config.routers_frontend import include_routers
from src.content.index.hero_card import hero_card
from pathlib import Path
from fastapi.staticfiles import StaticFiles
import markdown
import os

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

include_routers(app)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")
static_dir = os.getenv("STATIC_DIR", "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


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
        "hero_card": hero_card,
        "current_page": "home"},
    )

@app.get("/imprint")
def impressum(request: Request):
    return templates.TemplateResponse("imprint.html", {"request": request, "current_page": "imprint"})

@app.get("/about")
def impressum(request: Request):
    return templates.TemplateResponse("about.html", {"request": request, "current_page": "about"})


@app.get("/blog/rating-analysis")
async def rating_analysis(request: Request):
    with open("content/blog/rating-analysis.md") as f:
        content = markdown.markdown(f.read(), extensions=["fenced_code", "tables"])
    return templates.TemplateResponse("blog.html", {
        "request": request,
        "content": content,
        "title": "Modelling CS Player Performance",
        "current_page": "blog"
    })

@app.get("/predict")
def predict_page(request: Request):
    return templates.TemplateResponse(request, "predict.html", {"current_page": "predict"})