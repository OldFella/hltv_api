example_requests = [
    {"url":  '"https://api.csapi.de/matches/2389666"',
    "response":"""
{
  "id": 2389666,
  "team1": {
    "id": 8297,
    "name": "FURIA",
    "score": 1
  },
  "team2": {
    "id": 9565,
    "name": "Vitality",
    "score": 3
  },
  "maps": [
    {
      "id": 2,
      "name": "Overpass",
      "team1_score": 10,
      "team2_score": 13
    },
    {
      "id": 5,
      "name": "Nuke",
      "team1_score": 2,
      "team2_score": 13
    },
    {
      "id": 7,
      "name": "Inferno",
      "team1_score": 8,
      "team2_score": 13
    },
    {
      "id": 6,
      "name": "Mirage",
      "team1_score": 13,
      "team2_score": 11
    }
  ],
  "best_of": 5,
  "date": "2026-02-08",
  "event": "IEM Kraków 2026",
  "winner": {
    "id": 9565,
    "name": "Vitality"
  }
}
"""
    },
{
    "url":  '"https://api.csapi.de/players/21167"',
    "response": """
{
  "id": 21167,
  "name": "donk",
  "team": {
    "id": 7020,
    "name": "Spirit"
  },
  "stats": {
    "k": 21.0,
    "d": 14.643,
    "swing": 3.608,
    "adr": 99.525,
    "kast": 77.993,
    "rating": 1.49,
    "maps_played": 28
  }
}
    """
},
{
    "url":  '"https://api.csapi.de/teams/9565"',
      "response": """
{
  "id": 9565,
  "name": "Vitality",
  "streak": 10,
  "roster": [
    {
      "id": 7322,
      "name": "apex"
    },
    {
      "id": 11816,
      "name": "ropz"
    },
    {
      "id": 11893,
      "name": "zywoo"
    },
    {
      "id": 16693,
      "name": "flamez"
    },
    {
      "id": 18462,
      "name": "mezii"
    }
  ]
}
"""
  }]