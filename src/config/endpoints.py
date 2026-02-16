endpoints = {
    "Maps": [
        {
            "path": "/maps",
            "description": "Returns all Map names and IDs"
        }
    ],
    "Sides": [
        {
            "path": "/sides",
            "description": "Returns all Side names and IDs"
        }
    ],
    "Matches": [
        {
            "path": "/matches/latest",
            "description": "Returns latest pro CS results"
        },
        {
            "path": "/matches/2389666",
            "description": "Search Match with ID"
        }
    ],
    "Teams": [
        {
            "path": "/teams",
            "description": "Returns all pro CS team names and IDs"
        },
        {
            "path": "/teams/?name=Vitality",
            "description": "Search Team with name"
        },
        {
            "path": "/teams/9565",
            "description": "Search Team with ID"
        },
        {
            "path": "/teams/9565/matchhistory",
            "description": "Returns the last recent matches"
        }
    ],
    "Players": [
        {
            "path": "/players/?offset=0&limit=20",
            "description": "Returns all Player names and IDs"
        },
        {
            "path": "/players/21167",
            "description": "Returns a Player's name and ID"
        },
        {
            "path": "/players/21167/stats",
            "description": "Returns a Player's average stats per map"
        },
        {
            "path": "/players/21167/stats/maps",
            "description": "Returns a list of a Player's average stats for all maps"
        },
        {
            "path": "/players/21167/stats/sides",
            "description": "Returns a list of a Player's average stats for both sides"
        }
    ]
}
