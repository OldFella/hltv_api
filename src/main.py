from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from core.config import settings
from db.session import engine 
from db.base_class import Base
from routers import sides, matches, teams, spreadsheets, results, download


def create_tables():
    print('creating Base')   
    Base.metadata.create_all(bind=engine)
        

def start_application():
    app = FastAPI(title=settings.PROJECT_NAME,version=settings.PROJECT_VERSION)
    create_tables()
    return app


app = start_application()

app.include_router(sides.router)
app.include_router(matches.router)
app.include_router(teams.router)
app.include_router(spreadsheets.router)
app.include_router(results.router)
app.include_router(download.router)

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request},
    )
