from dotenv import load_dotenv

load_dotenv()
import os
from fastapi import FastAPI
from server.player.video import video_router,player_static, player_edit_static,player_record_static
from server.volume.edge import edge_router,edge_static
from server.volume.qwen import qwen_router,qwen_static
from server.draw.draw_ollama_cloud_ai import draw_ollama_cloud_ai_router
from server.web.web import web_static,tmp_static
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

uvicorn_server = None
SERVER = os.getenv("SERVER")
PORT = int(os.getenv("PORT"))
MAX_REQUESTS = int(os.getenv("MAX_REQUESTS"))


class LimitUploadSize(BaseHTTPMiddleware):
    def __init__(self, apps: ASGIApp, max_upload_size: int) -> None:
        super().__init__(apps)
        self.max_upload_size = max_upload_size

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method == 'POST':
            if 'content-length' not in request.headers:
                return Response(status_code=status.HTTP_411_LENGTH_REQUIRED)
            content_length = int(request.headers['content-length'])
            if content_length > self.max_upload_size:
                return Response(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
        return await call_next(request)

app = FastAPI(title="Flyer-API")
app.add_middleware(LimitUploadSize, max_upload_size=MAX_REQUESTS)

def load_app():
    app.include_router(video_router)
    app.include_router(draw_ollama_cloud_ai_router)
    app.include_router(edge_router)
    app.include_router(qwen_router)
    player_static(app)
    player_edit_static(app)
    player_record_static(app)
    edge_static(app)
    qwen_static(app)
    tmp_static(app)
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
