import os
import sys
import threading
import webview
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

uvicorn_server = None
PORT = 9000
SERVER = '127.0.0.1'

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


app.mount(
    "/hls",
    StaticFiles(directory="F:/study/m3u8", html=True),  # html=True 很关键！
    name="hls"
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


def main():
    url = "http://" + SERVER + ":" + str(PORT)
    print('url', url)
    # 1. 初始化 CEF（完整版Chrome内核）
    webview.create_window(title="Vue 正常运行", url=url)
    webview.start()
    stop_fastapi()


# ==============================================
# 你原来的 UI 入口
# ==============================================
if __name__ == "__main__":
    # 先启动网页服务
    start_web_server()
    main()
