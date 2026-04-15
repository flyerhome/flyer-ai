import os
import re
import subprocess
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, FastAPI, UploadFile, File, HTTPException, Form
from starlette.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import hashlib
import time
from datetime import datetime
import shutil

video_router = APIRouter()
M3U8_PATH = os.getenv("M3U8_PATH")
VIDEO_PATH = os.getenv("VIDEO_PATH")
RECORD_PATH = os.getenv("RECORD_PATH")

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
    server = os.getenv("SERVER") if os.getenv("SERVER") != '0.0.0.0' else '127.0.0.1'
    item.video_path = "http://" + server + ":" + os.getenv("PORT") + item.video_path
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
        server = os.getenv("SERVER") if os.getenv("SERVER") != '0.0.0.0' else '127.0.0.1'
        item.video_path = "http://" + server + ":" + os.getenv("PORT") + item.video_path
    if not Path(VIDEO_PATH + '/player2').exists():
        Path(VIDEO_PATH + '/player2').mkdir(parents=True, exist_ok=True)
    if item.end_time:
        ffmpeg_ss_to(item.video_path, item.start_time, item.end_time, VIDEO_PATH + '/player2/' + item.save_name, item.cut_audio)
        return
    ffmpeg_ss_t(item.video_path, item.start_time, item.time_long, VIDEO_PATH + '/player2/' + item.save_name, item.cut_audio)
    pass

class MergeItem(BaseModel):
    video_path: str = None
    video_start: str = None
    video_end: str = None
    record: UploadFile = File(...)
    save_name: str = None

@video_router.post("/player/record/merge")
def player_merge(
        record: UploadFile = File(..., max_length= 100 * 1024 * 1024),
        video_path: Optional[str] = Form(None),
        video_start: Optional[str] = Form(None),
        video_end: Optional[str] = Form(None)
                 ):

    os.makedirs(RECORD_PATH, exist_ok=True)
    file_path = os.path.join(RECORD_PATH, record.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(record.file, buffer)
    video_save_tmp = os.path.join(RECORD_PATH, "video_cut_" + record.filename.replace(".webm", ".mp4"))
    server = os.getenv("SERVER") if os.getenv("SERVER") != '0.0.0.0' else '127.0.0.1'
    http_video_path = "http://" + server + ":" + os.getenv("PORT") + video_path
    ffmpeg_ss_to(http_video_path, video_start,video_end, video_save_tmp)
    save_path = os.path.join(RECORD_PATH, "merger_" + record.filename.replace(".webm", ".mp4"))
    ffmpeg_merge(video_save_tmp, file_path, save_path, stack="vstack")
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


def ffmpeg_merge(video_path, record_path, save_path, stack: str = 'hstack'):
    """
        ffmpeg -i left.mp4 -i right.mp4 -filter_complex hstack=inputs=2 output.mp4

        ffmpeg -i top.mp4 -i bottom.mp4 -filter_complex vstack=inputs=2 output.mp4


        ffmpeg -i D:/records/video_cut_record_1776262443251.mp4 ^
       -i D:/records/record_1776262443251.webm ^
       -filter_complex "[0:v]scale=854:-2[v0];[1:v]scale=854:-2[v1];[v0][v1]vstack=inputs=2[v];[0:a][1:a]amix=inputs=2[a]" ^
       -map "[v]" -map "[a]" -c:v libx264 -c:a aac ^
       D:/records/merger_record_1776262443251.mp4
        """
    if stack=='hstack':
        cmd = (
            f'ffmpeg -i {video_path} -i {record_path} '
            f'-filter_complex "[0:v]scale=trunc(iw*480/ih/2)*2:480[v0];[1:v]scale=trunc(iw*480/ih/2)*2:480[v1];[v0][v1]hstack=inputs=2" '
            f' -map "[v]" -map "[a]" -c:v libx264 -c:a aac '
            f'{save_path}'
        )
        print('执行合并命令', cmd)
        subprocess.run(cmd, shell=True, check=True, capture_output=True)
    if stack=='vstack':
        cmd = (
            f'ffmpeg -i {video_path} -i {record_path} '
            # f'-filter_complex "[0:v]scale=854:-2[v0];[1:v]scale=854:-2[v1];[v0][v1]vstack=inputs=2[v];[0:a][1:a]amix=inputs=2[a]"'
            f'-filter_complex "[0:v]scale=854:-2[v0];[1:v]scale=854:-2[v1];[v0][v1]vstack=inputs=2[v];[0:a]volume=0.5[a0];[1:a]volume=1.5[a1];[a0][a1]amix=inputs=2[a]"'
            f' -map "[v]" -map "[a]" -c:v libx264 -c:a aac '
            f'{save_path}'
        )
        print('执行合并命令', cmd)
        subprocess.run(cmd, shell=True, check=True, capture_output=True)
    # 执行
    print("合并完成完成！")


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