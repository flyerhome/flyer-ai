import os
import sys
import threading
import webview
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from ollama import Client
import edge_tts
from pathlib import Path

from webview import Menu
from webview.menu import MenuAction

uvicorn_server = None
PORT = 9999
SERVER = 'localhost'

if len(sys.argv) > 1:
    PORT = sys.argv[1]

if len(sys.argv) > 2:
    SERVER = sys.argv[2]

# ==============================================
# FastAPI  app（全局一个就行）
# ==============================================
app = FastAPI(title="Flyer UI 本地网页服务")

# ==============================================
# 核心：托管 web 目录下的所有前端静态文件
# 访问 http://127.0.0.1:9000/ → 自动找 web/index.html
# ==============================================
storage_path = "F:\\study\\m3u8"


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


# ==============================================
# 你可以继续写接口，前端能直接调用
# ==============================================
@app.get("/api/hello")
def hello():
    return {"message": "Hello from FastAPI 接口"}


@app.get("/player/list")
def player_list():
    dirs = [f for f in os.listdir(storage_path) if os.path.isdir(os.path.join(storage_path, f))]
    result = []
    for d in dirs:
        result.append({
            'name': d,
            'url': "/hls/" + d + "/index.m3u8"
        })
    return {"data": result, "code": 0, "success": True}


@app.get("/draw/contents")
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


@app.get("/draw/ai_models")
def ai_models():
    return {
        "models": [
            {"value": "deepseek-v3.1:671b-cloud", "label": "deepseek-v3.1:671b-cloud"},
            {"value": "qwen3-coder:480b-cloud", "label": "qwen3-coder:480b-cloud"},
            {"value": "gpt-oss:120b-cloud", "label": "gpt-oss:120b-cloud"},
            {"value": "gpt-oss:20b-cloud", "label": "gpt-oss:20b-cloud"}
        ]
    }


class Item(BaseModel):
    content: str
    model: str


@app.post("/draw/cloud-ai")
def cloud_ai(item: Item):
    client = Client(
        host="https://ollama.com",
        headers={'Authorization': 'Bearer 95315917af9c4197a81b189f77b3b2cc.Ph0sTihPCcZjMQRgr0tdsHPP'}
    )

    messages = [
        {'role': 'user',
         'content': '首先你是一个画家，极具美感，其次你还是一个svg绘图专家，你只根据HTML标准返回绘画结果，格式如<rect x=100 y=200 width=30 height=320 />'},
        {'role': 'user', 'content': item.content},
    ]
    result = ''
    for part in client.chat(item.model, messages=messages, stream=True):
        result = result + part['message']['content']
    return {
        "item": item,
        "result": result
    }


@app.get("/volume/tone/list")
def tone_list():
    return read_edge_tts_volume()


class VolumeSubmitItem(BaseModel):
    content: str
    tone: str
    output: str


OUTPUT_DIR = 'D:\\volumes'


@app.post("/volume/submit")
async def submit(item: VolumeSubmitItem):
    print('submit', item)
    communicate = edge_tts.Communicate(item.content, item.tone)
    p = os.path.join(OUTPUT_DIR, item.output + '.wav')
    print(f"语音将生成：{p}")
    await communicate.save(p)
    print(f"语音已生成：{p}")
    return item


@app.get("/volume/list")
def volume_list():
    result = []
    folder = Path(OUTPUT_DIR)
    files = [f for f in folder.iterdir() if f.is_file()]
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    for f in files:
        result.append({
            'name': f.name,
            "time": f.stat().st_mtime,
            'url': '/volume/' + f.name
        })
    return {"data": result, "code": 0, "success": True}


app.mount(
    "/hls",
    StaticFiles(directory="F:/study/m3u8", html=False),  # html=True 很关键！
    name="hls"
)

app.mount(
    "/volume",
    StaticFiles(directory="D:/volumes", html=False),  # html=True 很关键！
    name="volume"
)
app.mount(
    "/",
    StaticFiles(directory="web", html=True),  # html=True 很关键！
    name="web"
)


# ===================== 启动 UVICORN =====================
def start_fastapi():
    global uvicorn_server
    import uvicorn
    uvicorn_server = uvicorn.Server(uvicorn.Config(app, host=SERVER, port=PORT))
    uvicorn_server.run()


# ===================== 停止 UVICORN =====================
def stop_fastapi():
    global uvicorn_server
    if uvicorn_server:
        uvicorn_server.should_exit = True  # 优雅停止
    print('执行了stop_fastapi')


# 启动线程（后台运行）
def start_web_server():
    thread = threading.Thread(target=start_fastapi, daemon=True)
    thread.start()


def on_closed():
    stop_fastapi()


def go_draw():
    window = webview.windows[0]  # 获取当前窗口
    url = "http://" + SERVER + ":" + str(PORT) + "/#/draw/ai"
    window.load_url(url)  # 改 URL


def go_draw2():
    window = webview.windows[0]  # 获取当前窗口
    url = "http://" + SERVER + ":" + str(PORT) + "/#/draw/cloud-ai"
    window.load_url(url)  # 改 URL


def go_player():
    window = webview.windows[0]  # 获取当前窗口
    url = "http://" + SERVER + ":" + str(PORT) + "/#/player"
    window.load_url(url)  # 改 URL


def go_volume():
    window = webview.windows[0]  # 获取当前窗口
    url = "http://" + SERVER + ":" + str(PORT) + "/#/volume/ai"
    window.load_url(url)  # 改 URL


MENU_LIST = [
    Menu('工具', items=[
        MenuAction("AI绘图-阿里云百炼", go_draw),
        MenuAction("AI绘图-ollama云模型", go_draw2),
        MenuAction("视频播放器", go_player),
        MenuAction("AI语音生成", go_volume),
    ])
]
win = None


def main():
    global win
    url = "http://" + SERVER + ":" + str(PORT) + "/#/volume/ai"
    print('url', url)
    # 1. 初始化 CEF（完整版Chrome内核）
    win = webview.create_window(title="AI工具", url=url)
    webview.start(menu=MENU_LIST)
    stop_fastapi()


# ==============================================
# 你原来的 UI 入口
# ==============================================
if __name__ == "__main__":
    # 先启动网页服务
    start_web_server()
    main()
