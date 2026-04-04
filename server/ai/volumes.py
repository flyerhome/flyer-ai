from pydantic import BaseModel
import edge_tts
import os
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path

load_dotenv()
volume_path = os.getenv("VOLUME_PATH")
class VolumeSubmitItem(BaseModel):
    content: str
    tone: str
    output: str

async def gen_volume(item: VolumeSubmitItem):
    print('gen_volume', item)
    communicate = edge_tts.Communicate(item.content, item.tone)
    p = os.path.join(volume_path, item.output + '.wav')
    print(f"语音将生成：{p}")
    await communicate.save(p)
    print(f"语音已生成：{p}")
    return item


def filter_gender(gender: str):
    if gender == 'Male':
        return '男'
    if gender == 'Female':
        return '女'
    return gender


def read_edge_tts_volume():
    result = []
    with open("edge_tts_volume.txt", "r", encoding="utf-8") as f:
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

def gen_volume_list():
    result = []
    folder = Path(volume_path)
    files = [f for f in folder.iterdir() if f.is_file()]
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    for f in files:
        result.append({
            'name': f.name,
            "time": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            'url': '/volume/' + f.name
        })
    return result

def base_volume_path():
    return volume_path