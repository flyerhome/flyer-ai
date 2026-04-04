import os
from pathlib import Path

from pydantic import BaseModel
import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel
import time
from datetime import datetime

class CloneVoiceItem(BaseModel):
    text: str
    language: str = 'English'
    clone_source: str = 'wenge'
    save_name: str | None

MODEL_NAME = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"
MODEL = None
VOLUME_PATH = os.getenv("VOLUME_PATH")

def clone_src():
    return [
        {"name": "文哥", "en_name":"wenge", "file": "./clone_src/wenge.wav", "text":"你好，我是文哥，这是我的声音"}
    ]

def clone_voice(item:CloneVoiceItem):
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

    ref_audio = src.file
    ref_text = src.text
    wav_list, sr = MODEL.generate_voice_clone(
        text=item.text,
        language=item.language,
        ref_audio=ref_audio,
        ref_text=ref_text,
    )
    sf.write(VOLUME_PATH + "/qwen3/" + item.save_name + ".wav", wav_list[0], sr)

def qwen3_volume_list():
    result = []
    folder = Path(VOLUME_PATH + "/qwen3")
    files = [f for f in folder.iterdir() if f.is_file()]
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    for f in files:
        result.append({
            'name': f.name,
            "time": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            'url': '/volume/qwen3/' + f.name
        })
    return result


# print("准备加载模型")
# model = Qwen3TTSModel.from_pretrained(
#     "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
#     device_map="cuda:0",
#     dtype=torch.bfloat16
# )
# print("成功加载模型")
# ref_audio = "./wenge.wav"
# ref_text  = "你好呀，我准备学英语，这是我2026年的学习计划"

# print("准备 generate_voice_clone ")
# wavs, sr = model.generate_voice_clone(
#     text="I'd like speaking English and I will study everyday!",
#     language="English",
#     ref_audio=ref_audio,
#     ref_text=ref_text,
# )

# print("成功 generate_voice_clone ")
# sf.write("output_voice_clone3.wav", wavs[0], sr)
# print("成功 sf.write ", "output_voice_clone3.wav")
