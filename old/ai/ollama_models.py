from pydantic import BaseModel
from ollama import Client
import os

class Item(BaseModel):
    content: str
    model: str
    role_desc: str = None

def request_cloud_ai(item: Item):
    client = Client(
            host="https://ollama.com",
            headers={'Authorization': 'Bearer ' + os.getenv("OLLAMA_KEY")}
        )

    messages = [
        {'role': 'user',
         'content': item.role_desc},
        {'role': 'user', 'content': item.content},
    ]
    result = ''
    for part in client.chat(item.model, messages=messages, stream=True):
        result = result + part['message']['content']
    return result

def cloud_ai_models():
    return {
        "models": [
            {"value": "deepseek-v3.1:671b-cloud", "label": "deepseek-v3.1:671b-cloud"},
            {"value": "qwen3-coder:480b-cloud", "label": "qwen3-coder:480b-cloud"},
            {"value": "gpt-oss:120b-cloud", "label": "gpt-oss:120b-cloud"},
            {"value": "gpt-oss:20b-cloud", "label": "gpt-oss:20b-cloud"}
        ]
    }