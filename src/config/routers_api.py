from src.routers import (
    sides,
    maps,
    matches,
    teams,
    goat,
    players,
    fantasy
)

def include_routers(app):
    app.include_router(sides.router)
    app.include_router(maps.router)
    app.include_router(matches.router)
    app.include_router(teams.router)
    app.include_router(goat.router)
    app.include_router(players.router)
    app.include_router(fantasy.router)

