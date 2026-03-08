from src.routers import (
    reference_data,
    matches,
    teams,
    goat,
    players,
    fantasy,
    rankings,
    counts
)

def include_routers(app):
    app.include_router(reference_data.sides_router)
    app.include_router(reference_data.maps_router)
    app.include_router(matches.router)
    app.include_router(teams.router)
    app.include_router(goat.router)
    app.include_router(players.router)
    app.include_router(fantasy.router)
    app.include_router(rankings.router)
    app.include_router(counts.router)



