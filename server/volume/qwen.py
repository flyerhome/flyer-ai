import os
from datetime import datetime

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel
from pathlib import Path

from pydantic import BaseModel
import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel
import time

from starlette.staticfiles import StaticFiles

MODEL_NAME = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"
MODEL = None
VOLUME_PATH = os.getenv("VOLUME_PATH")

qwen_router = APIRouter()
QWEN_CLONE_SRC_PATH = os.getenv("QWEN_CLONE_SRC_PATH")

class QwenCloneVoiceItem(BaseModel):
    text: str
    language: str = 'Chinese'
    clone_source: str = 'wenge'
    save_name: str | None

def clone_src():
    return [
        {"name": "文哥", "en_name":"wenge", "file": QWEN_CLONE_SRC_PATH + "/wenge.wav", "text":"你好，我是文哥，这是我的声音"},
        {"name": "吕布", "en_name":"lv_bu", "file": QWEN_CLONE_SRC_PATH + "/lvbu.aac", "text":"我堂堂大丈夫，安肯为汝之义子"},
        {"name": "曹操", "en_name":"caocao", "file": QWEN_CLONE_SRC_PATH + "/caocao.aac", "text":"司徒大人所虑不能说不对，然而也未必全对"},
    ]

def clone_voice(item:QwenCloneVoiceItem):
    clone_name = item.clone_source
    if not item.text:
        return
    if not item.save_name:
        timestamp = str(time.time())
        item.save_name = clone_name + timestamp
    global MODEL

    clone_src_list = clone_src()
    src = next((r for r in clone_src_list if r["en_name"] == clone_name), None)
    if not src:
        return

    if not MODEL:
        print("准备加载模型", MODEL_NAME)
        MODEL = Qwen3TTSModel.from_pretrained(
            MODEL_NAME,
            device_map="cuda:0",
            dtype=torch.bfloat16
        )
        print("成功加载模型", MODEL_NAME)

    ref_audio = src['file']
    ref_text = src['text']
    wav_list, sr = MODEL.generate_voice_clone(
        text=item.text,
        language=item.language,
        ref_audio=ref_audio,
        ref_text=ref_text,
    )
    if not Path(VOLUME_PATH + "/qwen/").exists():
        Path(VOLUME_PATH + "/qwen/").mkdir(parents=True, exist_ok=True)
    sf.write(VOLUME_PATH + "/qwen/" + item.save_name + ".wav", wav_list[0], sr)


@qwen_router.get("/volume/qwen/tone/list")
def qwen_tone_list():
    return clone_src()

@qwen_router.post("/volume/qwen/submit")
async def submit(item: QwenCloneVoiceItem):
    print('submit', item)
    clone_voice(item)
    return item

@qwen_router.get("/volume/qwen/list")
def volume_list():
    result = []
    folder = Path(VOLUME_PATH + "/qwen")
    files = [f for f in folder.iterdir() if f.is_file()]
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    for f in files:
        result.append({
            'name': f.name,
            "time": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            'url': '/volume/qwen/' + f.name
        })
    return {"data": result, "code": 0, "success": True}

def qwen_static(app:FastAPI):
    if not Path(VOLUME_PATH + "/qwen").exists():
        print("不存在" + VOLUME_PATH + "/qwen", "要准备自动创建")
        Path(VOLUME_PATH + "/qwen").mkdir(parents=True, exist_ok=True)
    app.mount(
        "/volume/qwen",
        StaticFiles(directory=VOLUME_PATH + "/qwen", html=False),  # html=True 很关键！
        name="volume"
    )