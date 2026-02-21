endpoints = {
    "Maps": [
        {
            "path": "/maps",
            "description": "All maps with names and IDs."
        }
    ],
    "Matches": [
        {
            "path": "/matches/latest",
            "description": "Most recent professional match results."
        },
        {
            "path": "/matches/2389666",
            "description": "Look up a match by ID."
        }
    ],
    "Teams": [
        {
            "path": "/teams",
            "description": "All professional teams."
        },
        {
            "path": "/teams/?name=Vitality",
            "description": "Search teams by name."
        },
        {
            "path": "/teams/9565/matchhistory",
            "description": "Recent matches for a team."
        }
    ],
    "Players": [
        {
            "path": "/players",
            "description": "All players, paginated."
        },
        {
            "path": "/players/21167",
            "description": "Player details by ID."
        },
        {
            "path": "/players/21167/stats",
            "description": "Player stats per map."
        }
    ]
}