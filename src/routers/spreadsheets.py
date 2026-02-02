import sys
sys.path.append('../')
from db.classes import fantasy_overview
from db.session import engine 
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
import pandas as pd
from fastapi.templating import Jinja2Templates
import os
from sqlalchemy import select, and_
from pathlib import Path
import numpy as np


templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix = '/spreadsheet',
                   tags = ['spreadsheet'])




BASE_DIR = Path("db/spreadsheets/").resolve()

@router.get("/", response_class=HTMLResponse)
def show_folders(request: Request):
    # List all folders in BASE_DIR
    folders = [p.name.removesuffix('.ods') for p in BASE_DIR.iterdir()]
    folders = sorted(folders, reverse=True)

    
    query = select(fantasy_overview.fantasyid, fantasy_overview.name)
    with engine.connect() as con:
        fantasy = np.array(con.execute(query).fetchall()).squeeze().T
        fantasy_map = dict(zip(list(fantasy[0]), list(fantasy[1].astype(str))))

    fantasies = {f: fantasy_map[f] for f in folders}
   
    return templates.TemplateResponse(
        "fantasies.html",
        {
            "request": request,
            "folders": fantasies,
        }
    )



@router.get("/{fantasyid}", response_class=HTMLResponse)
def display_spreadsheet(fantasyid, request:Request):
    ods_path = Path(f'db/spreadsheets/{fantasyid}.ods')
    if not ods_path.exists():
        raise HTTPException(status_code=404, detail="ODS file not found")
    
    fantasies = [p.name.removesuffix('.ods') for p in BASE_DIR.iterdir()]
    fantasies = sorted(fantasies, reverse=True)
    
    ods = pd.read_excel(ods_path,sheet_name=None, engine='odf')
    sheets = {}
    teams_list = []
    for sheet_name, df in ods.items():
        if {'fantasyid', 'teamid', 'playerid'}.issubset(df.columns):
            df = df.drop(columns=['fantasyid', 'teamid', 'playerid'])
            if len(teams_list) == 0:
                teams_list = df['team'].drop_duplicates()
        sheets[sheet_name] = {
            "columns": df.columns.tolist(),
            "rows": df.fillna(np.nan).values.tolist()  # keep NaN for sorting
        }
 

    query = select(fantasy_overview.fantasyid, fantasy_overview.name)
    with engine.connect() as con:
        fantasy = np.array(con.execute(query).fetchall()).squeeze().T
        fantasy_map = dict(zip(list(fantasy[0]), list(fantasy[1].astype(str))))
    
    fantasy_name = fantasy_map[fantasyid]
    fantasies = {f: fantasy_map[f] for f in fantasies}

    return templates.TemplateResponse(
        "table.html",  # Updated template for multi-sheet
        {
            "request": request,
            "fantasyid": fantasyid,
            "fantasy_name": fantasy_name,
            "fantasies": fantasies,
            "sheets": sheets,
            "fantasy_map": fantasies
            #"teams_list":teams_list
        }
    )

