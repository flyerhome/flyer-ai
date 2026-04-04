import os
from pathlib import Path

from fastapi import APIRouter, FastAPI
from starlette.staticfiles import StaticFiles

video_router = APIRouter()
M3U8_PATH = os.getenv("M3U8_PATH")


@video_router.get("/player/list")
def player_list():
    dirs = [f for f in os.listdir(M3U8_PATH) if os.path.isdir(os.path.join(M3U8_PATH, f))]
    result = []
    for d in dirs:
        result.append({
            'name': d,
            'url': "/hls/" + d + "/index.m3u8"
        })
    return {"data": result, "code": 0, "success": True}

def player_static(app:FastAPI):
    if Path(M3U8_PATH).exists():
        app.mount(
            "/hls",
            StaticFiles(directory=M3U8_PATH, html=False),  # html=True 很关键！
            name="hls"
        )