from fastapi import APIRouter
import numpy as np

router = APIRouter(prefix = '/goat',
                   tags = ['goat'])


@router.get("/", include_in_schema=False)
async def get_goat():
    goats = ['ZywOo', 'donk', 's0mple', 'dev1ce', 'f0rest']
    goat = np.random.choice(goats, p=[0.5, 0.3, 0.15, 0.04, 0.01])
    return {'goat': goat}