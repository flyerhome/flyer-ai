import os
import subprocess
from pathlib import Path

from fastapi import APIRouter, FastAPI
from starlette.staticfiles import StaticFiles
from pydantic import BaseModel
import hashlib
import time
from datetime import datetime

video_router = APIRouter()
M3U8_PATH = os.getenv("M3U8_PATH")
VIDEO_PATH = os.getenv("VIDEO_PATH")

def md5_encode(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()

@video_router.get("/player/list")
def player_list():
    dirs = [f for f in os.listdir(M3U8_PATH) if os.path.isdir(os.path.join(M3U8_PATH, f))]
    result = []
    for d in dirs:
        url = "/hls/" + d + "/index.m3u8"
        result.append({
            'vid': md5_encode(url),
            'name': d,
            'url': url
        })
    return {"data": result, "code": 0, "success": True}

def player_static(app:FastAPI):
    if Path(M3U8_PATH).exists():
        app.mount(
            "/hls",
            StaticFiles(directory=M3U8_PATH, html=False),  # html=True 很关键！
            name="hls"
        )

class PlayerEditItem(BaseModel):
    video_path: str = None
    start_time: str = None
    time_long: int = 10
    end_time: str = None
    volume: float = 0.6
    save_name: str = None

@video_router.post("/player/video-edit")
def player_edit(item:PlayerEditItem):
    if not item.save_name:
        item.save_name = str(time.time()) + ".mp4"
    hash_str = md5_encode(item.video_path)
    item.video_path = "http://" + os.getenv("SERVER") + ":" + os.getenv("PORT") + item.video_path
    if not Path(VIDEO_PATH + '/' + hash_str).exists():
        Path(VIDEO_PATH + '/' + hash_str).mkdir(parents=True, exist_ok=True)
    if item.end_time:
        ffmpeg_ss_to(item.video_path, item.start_time, item.end_time, VIDEO_PATH + '/' + hash_str + '/' + item.save_name)
        return
    ffmpeg_ss_t(item.video_path, item.start_time, item.time_long, VIDEO_PATH + '/' + hash_str + '/' + item.save_name)
    pass

def player_edit_static(app:FastAPI):
    if not Path(VIDEO_PATH).exists():
        Path(VIDEO_PATH).mkdir(parents=True, exist_ok=True)
    app.mount(
        "/video",
        StaticFiles(directory=VIDEO_PATH, html=False),  # html=True 很关键！
        name="video"
    )

@video_router.get("/player/edit/list")
def player_edit_list(vid:str):
    result = []
    folder = Path(VIDEO_PATH + "/" + vid)
    files = [f for f in folder.iterdir() if f.is_file()]
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    for f in files:
        result.append({
            'name': f.name,
            "time": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            'url': '/video/' + vid + '/' + f.name
        })
    return {"data": result, "code": 0, "success": True}

def ffmpeg_ss_to(video_path, start, end, save_path):
    """
    ffmpeg -i input.mp4 -ss 00:01:20 -to 00:01:45 -c:v libx264 -c:a aac output.mp4
    """
    cmd = (
        f'ffmpeg -i "{video_path}" '
        f'-ss {start} -to {end} '
        f'-c:v libx264 '
        f'-c:a aac '
        f'"{save_path}"'
    )
    # 执行
    subprocess.run(cmd, shell=True, check=True, capture_output=True)
    print("音频提取完成！")

def ffmpeg_ss_t(video_path, start, time_long, save_path):
    """
    ffmpeg -i input.mp4 -ss 00:01:20 -t 25 -c:v libx264 -c:a aac output.mp4
    """
    cmd = (
        f'ffmpeg -i "{video_path}" '
        f'-ss {start} -to {time_long} '
        f'-c:v libx264 '
        f'-c:a aac '
        f'"{save_path}"'
    )
    # 执行
    subprocess.run(cmd, shell=True, check=True, capture_output=True)
    print("音频提取完成！")