from fastapi import APIRouter, Query, Depends
from datetime import date
from sqlalchemy.engine import Connection
from src.db.get_db import get_db
from src.domain import use_cases
from src.domain.models import MatchupProbabilities
from src.adapters.sqlalchemy_teams import SqlAlchemyTeamsAdapter
from src.adapters.sqlalchemy_reference_data import SqlAlchemyRankingsAdapter

from src.utils.helpers import default_date_range

router = APIRouter(prefix='/predict', tags=['predict'])

@router.get("/{team_id_a}/{team_id_b}", response_model=MatchupProbabilities)
def get_matchup_probabilities(
    team_id_a: int,
    team_id_b: int,
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    conn: Connection = Depends(get_db)
) -> MatchupProbabilities:
    start, end = start_date or default_date_range()[0], end_date or default_date_range()[1]
    teams_port = SqlAlchemyTeamsAdapter(conn)
    rankings_port = SqlAlchemyRankingsAdapter(conn)
    return use_cases.get_map_win_probs(teams_port, rankings_port, team_id_a, team_id_b, start, end)