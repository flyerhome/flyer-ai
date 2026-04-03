import asyncio
import sys

import edge_tts

# 配置参数
TEXT = 'Hello, My name is Gao'
# VOICE = sys.argv[2]  # 晓晓（女声）
# VOICE = "ja-JP-NanamiNeural"  # 晓晓（女声）
# VOICE = "am-ET-AmehaNeural"  # 晓晓（女声）
VOICE = "zh-TW-YunJheNeural"  # 晓晓（女声）
OUTPUT_FILE = 'test.wav'


# 异步生成语音
async def text_to_speech():
    communicate = edge_tts.Communicate(TEXT, VOICE)
    await communicate.save(OUTPUT_FILE)
    print(f"语音已生成：{OUTPUT_FILE}")


# 运行
if __name__ == "__main__":
    asyncio.run(text_to_speech())
