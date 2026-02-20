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
      "name": "ovp",
      "team1_score": 10,
      "team2_score": 13
    },
    {
      "id": 5,
      "name": "nuke",
      "team1_score": 2,
      "team2_score": 13
    },
    {
      "id": 7,
      "name": "inf",
      "team1_score": 8,
      "team2_score": 13
    },
    {
      "id": 6,
      "name": "mrg",
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
    "url":  '"https://api.csapi.de/players/21167/stats"',
    "response": """
{
  "id": 21167,
  "name": "donk",
  "k": 20.711,
  "d": 15.6,
  "swing": 2.645,
  "adr": 94.331,
  "kast": 76.056,
  "rating": 1.405,
  "maps_played": 45
}
    """
}
]