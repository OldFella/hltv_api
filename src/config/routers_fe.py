from src.routers import spreadsheets, download

def include_routers(app):
    app.include_router(spreadsheets.router)
    app.include_router(download.router)