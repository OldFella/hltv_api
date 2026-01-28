from ..db.classes import fantasies
from ..db.session import engine 
from fastapi import APIRouter
from sqlalchemy import select


router = APIRouter(prefix = '/fantasy',
                   tags = ['fantasy'])



