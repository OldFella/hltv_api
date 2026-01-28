from fastapi import FastAPI
from .core.config import settings
from .db.session import engine 
from .db.base_class import Base
from .routers import sides, matches, teams, spreadsheets


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



@app.get("/")
def home():
    return {"msg":"Welcome to my HTLV API"}










        