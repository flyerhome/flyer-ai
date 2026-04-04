import time

import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel

print("准备加载模型")
model = Qwen3TTSModel.from_pretrained(
    "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
    device_map="cuda:0",
    dtype=torch.bfloat16
)
print("成功加载模型")
ref_audio = "./myvoice01.wav"
ref_text  = "你好呀，我准备学英语，这是我2026年的学习计划"

print("准备 generate_voice_clone ")
wavs, sr = model.generate_voice_clone(
    text="I'd like speaking English and I will study everyday!",
    language="English",
    ref_audio=ref_audio,
    ref_text=ref_text,
)

print("成功 generate_voice_clone ")
sf.write("output_voice_clone3.wav", wavs[0], sr)
print("成功 sf.write ", "output_voice_clone3.wav")
