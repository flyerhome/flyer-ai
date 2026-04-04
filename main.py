import os
from server import app
from dotenv import load_dotenv

load_dotenv()
uvicorn_server = None
SERVER = os.getenv("SERVER")
PORT = int(os.getenv("PORT"))
def start_web():
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
