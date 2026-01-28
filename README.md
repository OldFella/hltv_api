# hltv_api

Development of a RESTful API for the Data gathered by the htlv_scraper. The API will provide access to all tables and some quality of life request. Currently not available publically.


## API Calls:
The API will be read-only, therefore most request will be GET requests.

 - teams: 
    - GET all teams:
        """bash
        curl '<url>/teams/all/'
        """
    - GET `teamid` by `name`:
        """bash
        curl '<url>/teams/name/<teamname>'
        """
    - GET `name` by `teamid`:
        """bash
        curl '<url>/teams/id/<teamid>'
        """
    
    - GET matchhistory of a `team` (optional against a specific opponent):
        """bash
        curl '<url>/teams/matchhistory/<teamname1>?vs=<teamname2>'
        """

-  matches:
    - GET all matches:
         """bash
        curl '<url>/matches/all/'
        """
    - GET match:
         """bash
        curl '<url>/matches/<matchid>'
        """