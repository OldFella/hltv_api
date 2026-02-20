
from pathlib import Path
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
import pandas as pd
import numpy as np

from src.db.classes import fantasy_overview
from src.db.session import engine


templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix = '/spreadsheet',
                   tags = ['spreadsheet'])

BASE_DIR = Path("db/spreadsheets/").resolve()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _get_fantasy_map() -> dict:
    """Return {fantasyid: name} for all fantasies."""
    query = select(fantasy_overview.fantasyid, fantasy_overview.name)
    with engine.connect() as con:
        rows = con.execute(query).mappings().all()
    return {r['fantasyid']: r['name'] for r in rows}

def _get_sorted_fantasy_ids() -> list[int]:
    return sorted([int(p.name.removesuffix('.ods')) for p in BASE_DIR.iterdir()], reverse=True)



def _parse_ods(path: Path) -> tuple[dict, list]:
    ods = pd.read_excel(path, sheet_name=None, engine='odf')
    sheets = {}
    teams_list = []
    for sheet_name, df in ods.items():
        if {'fantasyid', 'teamid', 'playerid'}.issubset(df.columns):
            df = df.drop(columns=['fantasyid', 'teamid', 'playerid'])
            if not teams_list:
                teams_list = df['team'].drop_duplicates().tolist()
        sheets[sheet_name] = {
            "columns": df.columns.tolist(),
            "rows": df.fillna(np.nan).values.tolist(),
        }
    return sheets, teams_list

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------



@router.get("/", response_class=HTMLResponse)
def show_folders(request: Request):
    folder_ids = _get_sorted_fantasy_ids()
    fantasy_map = _get_fantasy_map()

    fantasies = {f: fantasy_map[f] for f in folder_ids}
   
    return templates.TemplateResponse(
        "fantasies.html",
        {
            "request": request,
            "folders": fantasies,
        }
    )


@router.get("/{fantasyid}", response_class=HTMLResponse)
def display_spreadsheet(fantasyid: int, request: Request):
    ods_path = BASE_DIR / f"{fantasyid}.ods"
    if not ods_path.exists():
        raise HTTPException(status_code=404, detail="ODS file not found")

    fantasy_map = _get_fantasy_map()
    folder_ids = _get_sorted_fantasy_ids()
    fantasies = {f: fantasy_map[f] for f in folder_ids}
    sheets, _ = _parse_ods(ods_path)

    return templates.TemplateResponse("table.html", {
        "request": request,
        "fantasyid": fantasyid,
        "fantasy_name": fantasy_map[fantasyid],
        "fantasies": fantasies,
        "sheets": sheets,
        "fantasy_map": fantasies,
    })

