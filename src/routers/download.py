from fastapi import APIRouter
from fastapi.responses import FileResponse
from fastapi import HTTPException
from pathlib import Path

router = APIRouter(prefix = '/download',
                   tags = ['download'])

DOWNLOAD_DIR = Path("static/downloads")




@router.get("/{filename}")
async def download_file(filename: str):
    file_path = DOWNLOAD_DIR / filename

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    # FileResponse sets correct headers so browser downloads file
    return FileResponse(path=file_path, filename=filename)
