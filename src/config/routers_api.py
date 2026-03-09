from src.routers import (
    reference_data,
    matches,
    teams,
    goat,
    players
)

def include_routers(app):
    app.include_router(reference_data.sides_router)
    app.include_router(reference_data.maps_router)
    app.include_router(matches.router)
    app.include_router(teams.router)
    app.include_router(goat.router)
    app.include_router(players.router)
    app.include_router(reference_data.fantasy_router)
    app.include_router(reference_data.rankings_router)
    app.include_router(reference_data.counts_router)



