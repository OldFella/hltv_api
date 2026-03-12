from src.routers import (
    reference_data,
    matches,
    teams,
    goat,
    players,
    predict
)

def include_routers(app):
    for router in reference_data.all_routers:
        app.include_router(router)
    app.include_router(matches.router)
    app.include_router(teams.router)
    app.include_router(goat.router)
    app.include_router(players.router)
    app.include_router(predict.router)




