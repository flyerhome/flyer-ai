import os
import time
from datetime import datetime

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel
import edge_tts
from pathlib import Path

from starlette.staticfiles import StaticFiles

edge_router = APIRouter()
VOLUME_PATH = os.getenv("VOLUME_PATH")

def filter_gender(gender: str):
    if gender == 'Male':
        return '男'
    if gender == 'Female':
        return '女'
    return gender


def read_edge_tts_volume():
    result = []
    with open("./server/volume/edge_tts_volume.txt", "r", encoding="utf-8") as f:
        # 一行一行读
        for line in f:
            # strip() 去掉换行符和空格
            items = line.strip().split()
            if items[0] == 'Name':
                continue
            result.append({
                "name": items[0],
                "gender": filter_gender(items[1]),
                "contentCategories": items[2],
                "voicePersonalities": items[3]
            })
    return result

@edge_router.get("/volume/tone/list")
def tone_list():
    return read_edge_tts_volume()


class VolumeSubmitItem(BaseModel):
    content: str = ''
    tone: str = ''
    output: str = ''
    rate: int = 0
    pitch: int = 0
    volume: int = 0

def trans_rate_pitch(val: int):
    if val >= 0:
        return '+' + str(val)
    return str(val)

@edge_router.post("/volume/submit")
async def submit(item: VolumeSubmitItem):
    print('submit', item)
    if not item.output:
        timestamp = str(time.time())
        item.output = item.tone + timestamp
    communicate = edge_tts.Communicate(text=item.content, voice=item.tone, volume=trans_rate_pitch(item.volume) + '%', rate=trans_rate_pitch(item.rate) + "%",pitch=trans_rate_pitch(item.pitch) + "Hz")
    p = os.path.join(VOLUME_PATH + "/edge", item.output + '.wav')
    print(f"语音将生成：{p}")
    await communicate.save(p)
    print(f"语音已生成：{p}")
    return item


@edge_router.get("/volume/list")
def volume_list():
    result = []
    folder = Path(VOLUME_PATH + "/edge")
    files = [f for f in folder.iterdir() if f.is_file()]
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    for f in files:
        result.append({
            'name': f.name,
            "time": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            'url': '/volume/edge/' + f.name
        })
    return {"data": result, "code": 0, "success": True}

def edge_static(app:FastAPI):
    if not Path(VOLUME_PATH + "/edge").exists():
        print("不存在" + VOLUME_PATH + "/edge", "要准备自动创建")
        Path(VOLUME_PATH + "/edge").mkdir(parents=True, exist_ok=True)
    app.mount(
        "/volume/edge",
        StaticFiles(directory=VOLUME_PATH + "/edge", html=False),  # html=True 很关键！
        name="volume"
    )