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

def tmp_static(app:FastAPI):
    app.mount(
        "/tmp",
        StaticFiles(directory=r"H:\wenge\有价值的学习\2026学习计划\英语", html=False),  # html=True 很关键！
        name="web"
    )
    app.mount(
        "/static",
        StaticFiles(directory="static", html=True),  # html=True 很关键！
        name="static"
    )
