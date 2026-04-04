import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from dotenv import load_dotenv
from .ai import Item, request_cloud_ai, gen_volume, VolumeSubmitItem, cloud_ai_models, read_edge_tts_volume, \
    gen_volume_list, base_volume_path

load_dotenv()

fastApi = FastAPI(title="Flyer-API")

storage_path = os.getenv("M3U8_PATH")

# ==============================================
# 你可以继续写接口，前端能直接调用
# ==============================================
@fastApi.get("/api/hello")
def hello():
    return {"message": "Hello world"}


@fastApi.get("/player/list")
def player_list():
    dirs = [f for f in os.listdir(storage_path) if os.path.isdir(os.path.join(storage_path, f))]
    result = []
    for d in dirs:
        result.append({
            'name': d,
            'url': "/hls/" + d + "/index.m3u8"
        })
    return {"data": result, "code": 0, "success": True}


@fastApi.get("/draw/contents")
def content_models():
    return {
        "contents": [
            {'name': '淡蓝风格',
             'content': '请用文本“{text}”绘制页面，文本整体居中，文本字体颜色统一用#0066EE，'
                        '独占一行，'
                        '下边一行小字中文翻译，'
                        '背景简单好看，'
                        '色调偏浅蓝，背景和文本不要太突兀，'
                        '在不影响文本的情况下适当丰富些，与文本应景，类似PPT标题页'
             }
        ]
    }


@fastApi.get("/draw/ai_models")
def ai_models():
    return cloud_ai_models()


@fastApi.post("/draw/cloud-ai")
def cloud_ai(item: Item):
    item.role_desc = '首先你是一个画家，极具美感，其次你还是一个svg绘图专家，你只根据HTML标准返回绘画结果，格式如<rect x=100 y=200 width=30 height=320 />'
    return {
        "item": item,
        "result": request_cloud_ai(item)
    }


@fastApi.get("/volume/tone/list")
def tone_list():
    return read_edge_tts_volume()


volume_path = base_volume_path()

@fastApi.post("/volume/submit")
async def submit(item: VolumeSubmitItem):
    return gen_volume(item)


@fastApi.get("/volume/list")
def volume_list():
    result = gen_volume_list()
    return {"data": result, "code": 0, "success": True}

m3u8 = os.getenv("M3U8_PATH")
if Path(m3u8).exists():
    fastApi.mount(
        "/hls",
        StaticFiles(directory=m3u8, html=False),  # html=True 很关键！
        name="hls"
    )


if not Path(volume_path).exists():
    print("不存在" + volume_path, "要准备自动创建")
    Path(volume_path).mkdir(parents=True, exist_ok=True)
fastApi.mount(
    "/volume",
    StaticFiles(directory=volume_path, html=False),  # html=True 很关键！
    name="volume"
)

web_deploy = os.getenv("WEB_DEPLOY")
if Path(web_deploy).exists():
    fastApi.mount(
        "/",
        StaticFiles(directory=web_deploy, html=True),  # html=True 很关键！
        name="web"
    )

def app():
    return fastApi