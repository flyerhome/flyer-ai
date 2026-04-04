import os
from pathlib import Path

from fastapi import APIRouter, FastAPI
from starlette.staticfiles import StaticFiles

web_router = APIRouter()

HTML_PATH = os.getenv("HTML_PATH")

def web_static(app:FastAPI):
    if Path(HTML_PATH).exists():
        app.mount(
            "/",
            StaticFiles(directory=HTML_PATH, html=True),  # html=True 很关键！
            name="web"
        )