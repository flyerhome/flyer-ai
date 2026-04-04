import os
from fastapi import APIRouter
from pydantic import BaseModel
from ollama import Client

draw_ollama_cloud_ai_router = APIRouter()

class Item(BaseModel):
    content: str
    model: str

@draw_ollama_cloud_ai_router.get("/draw/ai_models")
def ai_models():
    return {
        "models": [
            {"value": "deepseek-v3.1:671b-cloud", "label": "deepseek-v3.1:671b-cloud"},
            {"value": "qwen3-coder:480b-cloud", "label": "qwen3-coder:480b-cloud"},
            {"value": "gpt-oss:120b-cloud", "label": "gpt-oss:120b-cloud"},
            {"value": "gpt-oss:20b-cloud", "label": "gpt-oss:20b-cloud"}
        ]
    }

@draw_ollama_cloud_ai_router.post("/draw/cloud-ai")
def cloud_ai(item: Item):
    client = Client(
        host="https://ollama.com",
        headers={'Authorization': 'Bearer ' + os.getenv("OLLAMA_KEY")}
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