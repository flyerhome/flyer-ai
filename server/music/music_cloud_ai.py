import re
import time
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from starlette.staticfiles import StaticFiles

from .musics import MusicObj
from .scale import low1, high1, low2, high2, C,D,E, F, G,A, B
from ollama import Client
import os
import json

class MusicItem(BaseModel):
    content: str
    model: str = 'deepseek-v3.1:671b-cloud'

musics_router = APIRouter()
MUSIC_PATH=os.getenv('MUSIC_PATH')

json_str = {
    "speed":88,
    "program":1,
    "musics":[
        {"key":"F","time": 1.0, "scale":"1", "pitch":"high1"}
    ]
}
format_info = "speed表示音速，program 表示乐器0-127 musics 代表音乐的音符列表，key是音调，time是弹唱时长，scale代表音名如1234567，pitch代表音高取值有空值、low1、low2、high1、high2"


def extract_json_from_markdown(text):
    """从包含 Markdown 代码块的文本中提取 JSON"""

    # 匹配 ```json ... ``` 之间的内容（非贪婪模式）
    pattern = r'```json\n(.*?)\n```'
    match = re.search(pattern, text, re.DOTALL)

    if match:
        json_str = match.group(1).strip()
        return json.loads(json_str)
    else:
        # 如果没有找到 ```json 标记，尝试直接解析
        return json.loads(text)

def cloud_ai(content, model="deepseek-v3.1:671b-cloud"):
    client = Client(
        host="https://ollama.com",
        headers={'Authorization': 'Bearer ' + os.getenv("OLLAMA_KEY")}
    )

    messages = [
        {
            'role': 'user',
            'content': f'你是一名优秀的音乐编曲师，擅长用midi工具编曲，输出格式为{json.dumps(json_str)}，格式说明{format_info}。'
        },
        {
            'role': 'user',
            'content': content
        },
    ]
    result = ''
    for part in client.chat(model, messages=messages, stream=True):
        result = result + part['message']['content']
    return {
        "item": {content,model},
        "result": result
    }

@musics_router.post("/musics/cloud-ai")
def music_cloud_ai(item: MusicItem):
    body = cloud_ai(item.content, model=item.model)
    print("cloud return",body)
    result = body["result"]
    print("result=",result)
    result = extract_json_from_markdown(result)
    musicObj = MusicObj(speed=(result["speed"]), program=(result["program"]))
    print("musics",result["musics"])
    for music in result["musics"]:
        scale_name = str(music["scale"])
        key = C
        if music["key"] == "C":
            key = C
        if music["key"] == "D":
            key = D
        if music["key"] == "E":
            key = E
        if music["key"] == "F":
            key = F
        if music["key"] == "G":
            key = G
        if music["key"] == "A":
            key = A
        if music["key"] == "B":
            key = B
        final_scale = key[scale_name]
        if music['pitch'] == "high1":
            final_scale = high1(final_scale)
        if music['pitch'] == "high2":
            final_scale = high2(final_scale)
        if music['pitch'] == "low1":
            final_scale = low1(final_scale)
        if music['pitch'] == "low2":
            final_scale = low2(final_scale)
        musicObj.press(final_scale, time_long=float(music["time"]))
    file_name = time.strftime("%Y%m%d%H%M%S", time.localtime())
    musicObj.save(f"{MUSIC_PATH}/{file_name}.mid")

    return {
        "file_name": f"{file_name}.mid",
        "url": f"/music/{file_name}.mid",
    }

def music_static(app:FastAPI):
    if not Path(MUSIC_PATH).exists():
        print("不存在" + MUSIC_PATH, "要准备自动创建")
        Path(MUSIC_PATH).mkdir(parents=True, exist_ok=True)
    app.mount(
        "/music",
        StaticFiles(directory=MUSIC_PATH, html=False),  # html=True 很关键！
        name="music"
    )

@musics_router.get("/music/list")
def musics_list():
    result = []
    folder = Path(MUSIC_PATH)
    files = [f for f in folder.iterdir() if f.is_file()]
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    for f in files:
        result.append({
            'name': f.name,
            "time": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            'url': '/music/' + f.name
        })
    return {"data": result, "code": 0, "success": True}