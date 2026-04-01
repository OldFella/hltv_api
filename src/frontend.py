from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import markdown
import os

from src.core.config import settings
from src.db.session import engine
from src.db.base_class import Base
from src.config.routers_frontend import include_routers
from src.content.loader import content_for, shared


def create_tables():
    Base.metadata.create_all(bind=engine)


def start_application():
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.add_event_handler("startup", create_tables)
    return app


app = start_application()
include_routers(app)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

static_dir = os.getenv("STATIC_DIR", "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


def ctx(request: Request, current_page: str, **extra) -> dict:
    """
    Base context injected into every route.
    Includes the request, current_page, and shared nav —
    so templates always have {{ nav.links }} available.
    """
    return {
        "request": request,
        "current_page": current_page,
        **shared("nav"),
        **extra,
    }


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse(
        request, "404.html", ctx(request, ""), status_code=404
    )


@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse(
        request, "index.html",
        ctx(request, "home", api_base="https://api.csapi.de", **content_for("index")),
    )


@app.get("/matchup-predictor")
async def predict_page(request: Request):
    return templates.TemplateResponse(
        request, "predict.html",
        ctx(request, "predict", **content_for("predict")),
    )


@app.get("/blog/rating-analysis")
async def rating_analysis(request: Request):
    with open("content/blog/rating-analysis.md") as f:
        html_content = markdown.markdown(f.read(), extensions=["fenced_code", "tables"])
    return templates.TemplateResponse(
        request, "blog.html",
        ctx(request, "blog", content=html_content, title="Modelling CS Player Performance"),
    )


@app.get("/imprint")
async def impressum(request: Request):
    return templates.TemplateResponse(
        request, "imprint.html", ctx(request, "imprint")
    )


@app.get("/about")
async def about(request: Request):
    return templates.TemplateResponse(
        request, "about.html", ctx(request, "about")
    )

@app.get("/robots.txt")
async def robots():
    return FileResponse("robots.txt")

@app.get("/apple-touch-icon.png")
@app.get("/apple-touch-icon-precomposed.png")
async def apple_touch_icon():
    return FileResponse("static/icon/apple-touch-icon.png")