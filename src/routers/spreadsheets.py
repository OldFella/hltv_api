from pathlib import Path
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
import pandas as pd
import numpy as np

from src.db.classes import fantasy_overview
from src.db.session import engine
from src.content.loader import content_for, shared

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/spreadsheet", tags=["spreadsheet"])

BASE_DIR = Path("db/spreadsheets/").resolve()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_fantasy_map() -> dict:
    """Return {fantasyid: name} for all fantasies, sorted newest first."""
    query = select(fantasy_overview.fantasyid, fantasy_overview.name)
    with engine.connect() as con:
        rows = con.execute(query).mappings().all()
    fantasy_map = {r["fantasyid"]: r["name"] for r in rows}

    sorted_ids = sorted(
        [int(p.name.removesuffix(".ods")) for p in BASE_DIR.iterdir()],
        reverse=True,
    )
    # Return ordered dict: newest fantasy first
    return {fid: fantasy_map[fid] for fid in sorted_ids if fid in fantasy_map}


def _parse_ods(path: Path) -> tuple[dict, list]:
    ods = pd.read_excel(path, sheet_name=None, engine="odf")
    sheets = {}
    teams_list = []

    for sheet_name, df in ods.items():
        if {"fantasyid", "teamid", "playerid"}.issubset(df.columns):
            df = df.drop(columns=["fantasyid", "teamid", "playerid"])
        if not teams_list:
            teams_list = df["team"].drop_duplicates().tolist()
        sheets[sheet_name] = {
            "columns": df.columns.tolist(),
            "rows": df.fillna(np.nan).values.tolist(),
        }
    return sheets, teams_list


def _base_ctx(request: Request, current_page: str, **extra) -> dict:
    """Base context for spreadsheet routes — mirrors frontend.py ctx()."""
    return {
        "request": request,
        "current_page": current_page,
        **shared("nav"),
        **extra,
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/", response_class=HTMLResponse)
def show_folders(request: Request):
    fantasies = _get_fantasy_map()
    return templates.TemplateResponse(
        request,
        "fantasies.html",
        _base_ctx(
            request,
            "Fantasy",
            fantasies=fantasies,
            **content_for("fantasies"),
        ),
    )


@router.get("/{fantasyid}", response_class=HTMLResponse)
def display_spreadsheet(fantasyid: int, request: Request):
    ods_path = BASE_DIR / f"{fantasyid}.ods"
    if not ods_path.exists():
        raise HTTPException(status_code=404, detail="ODS file not found")

    fantasies = _get_fantasy_map()
    if fantasyid not in fantasies:
        raise HTTPException(status_code=404, detail="Fantasy not found")

    sheets, _ = _parse_ods(ods_path)
    return templates.TemplateResponse(
        request,
        "table.html",
        _base_ctx(
            request,
            "Fantasy",
            fantasyid=fantasyid,
            fantasy_name=fantasies[fantasyid],
            fantasies=fantasies,
            sheets=sheets,
        ),
    )