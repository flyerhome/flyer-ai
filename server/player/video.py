import os
import re
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
            'vid': d,
            'name': d,
            'url': url
        })
    return {"data": result, "code": 0, "success": True}

def player_static(app:FastAPI):
    if Path(M3U8_PATH).exists():
        print('mount /hls M3U8_PATH=', M3U8_PATH)
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
    cut_audio: int = 0

def get_filename_safe(filepath):
    """安全获取文件名（无论是否有路径）"""
    return Path(filepath).parent.name

@video_router.post("/player/video-edit")
def player_edit(item:PlayerEditItem):
    file_name = get_filename_safe(item.video_path)
    if not item.save_name:
        default_name = file_name + '_' + datetime.fromtimestamp(time.time()).strftime("%Y_%m_%d_%H_%M_%S")
        if 0 == item.cut_audio:
            item.save_name = default_name + ".mp4"
        if 1 == item.cut_audio:
            item.save_name = default_name + ".wav"
    item.video_path = "http://" + os.getenv("SERVER") + ":" + os.getenv("PORT") + item.video_path
    if not Path(VIDEO_PATH + '/' + file_name).exists():
        Path(VIDEO_PATH + '/' + file_name).mkdir(parents=True, exist_ok=True)
    if item.end_time:
        ffmpeg_ss_to(item.video_path, item.start_time, item.end_time, VIDEO_PATH + '/' + file_name + '/' + item.save_name, item.cut_audio)
        return
    ffmpeg_ss_t(item.video_path, item.start_time, item.time_long, VIDEO_PATH + '/' + file_name + '/' + item.save_name, item.cut_audio)
    pass


@video_router.post("/player2/video-edit")
def player_edit(item:PlayerEditItem):
    file_name = get_filename_safe(item.video_path)
    if not item.save_name:
        default_name = file_name + '_' + datetime.fromtimestamp(time.time()).strftime("%Y_%m_%d_%H_%M_%S")
        if 0 == item.cut_audio:
            item.save_name = default_name + ".mp4"
        if 1 == item.cut_audio:
            item.save_name = default_name + ".wav"
    if not item.video_path.startswith('http'):
        item.video_path = "http://" + os.getenv("SERVER") + ":" + os.getenv("PORT") + item.video_path
    if not Path(VIDEO_PATH + '/player2').exists():
        Path(VIDEO_PATH + '/player2').mkdir(parents=True, exist_ok=True)
    if item.end_time:
        ffmpeg_ss_to(item.video_path, item.start_time, item.end_time, VIDEO_PATH + '/player2/' + item.save_name, item.cut_audio)
        return
    ffmpeg_ss_t(item.video_path, item.start_time, item.time_long, VIDEO_PATH + '/player2/' + item.save_name, item.cut_audio)
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

@video_router.get("/player2/edit/list")
def player_edit_list():
    result = []
    folder = Path(VIDEO_PATH + "/player2")
    files = [f for f in folder.iterdir() if f.is_file()]
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    for f in files:
        result.append({
            'name': f.name,
            "time": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            'url': '/video/player2/' + f.name
        })
    return {"data": result, "code": 0, "success": True}

def ffmpeg_ss_to(video_path, start, end, save_path, cut_audio=0):
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
    if 1 == cut_audio:
        cmd = (
            f'ffmpeg -i "{video_path}" '
            f'-ss {start} -to {end} '
            f'-vn -acodec pcm_s16le '
            f'"{save_path}"'
        )
    # 执行
    subprocess.run(cmd, shell=True, check=True, capture_output=True)
    print("音频提取完成！")

def ffmpeg_ss_t(video_path, start, time_long, save_path, cut_audio=0):
    """
    ffmpeg -i input.mp4 -ss 00:01:20 -t 25 -c:v libx264 -c:a aac output.mp4
    """
    cmd = (
        f'ffmpeg -i "{video_path}" '
        f'-ss {start} -t {time_long} '
        f'-c:v libx264 '
        f'-c:a aac '
        f'"{save_path}"'
    )
    if cut_audio:
        cmd = (
            f'ffmpeg -i "{video_path}" '
            f'-ss {start} -t {time_long} '
            f'-c copy '
            f'"{save_path}"'
        )
    # 执行
    subprocess.run(cmd, shell=True, check=True, capture_output=True)
    print("音频提取完成！")

def ffmpeg_get_audio():
    """
    ffmpeg -list_devices true -f dshow -i dummy
    """
    cmd = (
        f'ffmpeg -list_devices true '
        f'-f dshow '
        f'-i dummy '
    )
    # 执行
    subprocess.run(cmd, shell=True, check=True, capture_output=True)
    print("音频提取完成！")
    pass

def ffmpeg_make_record():
    """
        ffmpeg -f dshow -i audio="麦克风名称" output.wav
        """
    cmd = (
        f'ffmpeg -i "{video_path}" '
        f'-ss {start} -t {time_long} '
        f'-c:v libx264 '
        f'-c:a aac '
        f'"{save_path}"'
    )
    # 执行
    subprocess.run(cmd, shell=True, check=True, capture_output=True)
    print("音频提取完成！")
    pass


def get_device_details():
    """获取更详细的麦克风设备信息（包含替代名称）"""
    cmd = ['ffmpeg', '-list_devices', 'true', '-f', 'dshow', '-i', 'dummy']

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='gbk',
            shell=True
        )

        devices = []
        lines = result.stderr.split('\n')

        for i, line in enumerate(lines):
            # 匹配音频设备行
            if '(audio)' in line:
                # 提取设备名
                match = re.search(r'"([^"]+)"', line)
                if match:
                    device_name = match.group(1)

                    # 尝试获取下一行的替代名称
                    alt_name = ""
                    if i + 1 < len(lines) and 'Alternative name' in lines[i + 1]:
                        alt_match = re.search(r'"([^"]+)"', lines[i + 1])
                        if alt_match:
                            alt_name = alt_match.group(1)

                    devices.append({
                        'name': device_name,
                        'alternative_name': alt_name
                    })

        return devices

    except Exception as e:
        print(f"获取设备详情时出错: {e}")
        return []