endpoints = {
    "Maps": [
        {
            "path": "/maps",
            "description": "List all maps with their names and unique IDs."
        }
    ],
    "Sides": [
        {
            "path": "/sides",
            "description": "List all sides (T/CT) with names and IDs."
        }
    ],
    "Matches": [
        {
            "path": "/matches/latest",
            "description": "Get the most recent professional CS match results."
        },
        {
            "path": "/matches/2389666",
            "description": "Look up a specific match by its unique match ID."
        }
    ],
    "Teams": [
        {
            "path": "/teams",
            "description": "List all professional CS teams with names and IDs."
        },
        {
            "path": "/teams/?name=Vitality",
            "description": "Search for a team by name."
        },
        {
            "path": "/teams/9565",
            "description": "Get details for a specific team using its unique ID."
        },
        {
            "path": "/teams/9565/matchhistory",
            "description": "Retrieve the recent matches played by a team."
        }
    ],
    "Players": [
        {
            "path": "/players/?offset=0&limit=20",
            "description": "List players with names and IDs (paginated)."
        },
        {
            "path": "/players/21167",
            "description": "Get details for a specific player using their ID."
        },
        {
            "path": "/players/21167/stats",
            "description": "View a player's average stats per map."
        },
        {
            "path": "/players/21167/stats/maps",
            "description": "See a player's average stats broken down by each map."
        },
        {
            "path": "/players/21167/stats/sides",
            "description": "See a player's average stats for both sides (T/CT)."
        },
        {
            "path": "/players/21167/stats/events",
            "description": "View a player's average stats across different events."
        }
    ]
}
