from dotenv import load_dotenv

load_dotenv()
import os
from fastapi import FastAPI
from server.player.video import video_router,player_static, player_edit_static
from server.volume.edge import edge_router,edge_static
from server.volume.qwen import qwen_router,qwen_static
from server.draw.draw_ollama_cloud_ai import draw_ollama_cloud_ai_router
from server.web.web import web_static


uvicorn_server = None
SERVER = os.getenv("SERVER")
PORT = int(os.getenv("PORT"))

app = FastAPI(title="Flyer-API")


def load_app():
    app.include_router(video_router)
    app.include_router(draw_ollama_cloud_ai_router)
    app.include_router(edge_router)
    app.include_router(qwen_router)
    player_static(app)
    player_edit_static(app)
    edge_static(app)
    qwen_static(app)
    web_static(app)


def start_web():
    load_app()
    global uvicorn_server
    import uvicorn
    uvicorn_server = uvicorn.Server(uvicorn.Config(app, host=SERVER, port=PORT))
    uvicorn_server.run()
    pass

def stop_web():
    global uvicorn_server
    if uvicorn_server:
        uvicorn_server.should_exit = True  # 优雅停止
    print('执行了stop_fastapi')
    pass

if __name__ == "__main__":
    # 先启动网页服务
    start_web()
