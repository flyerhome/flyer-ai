import torch
import os
import soundfile as sf
from qwen_tts import Qwen3TTSModel

# 强制禁用 CUDA，强制使用 CPU
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["USE_FLASH_ATTENTION"] = "0"
torch.cuda.is_available = lambda : False  # 欺骗模型：没有GPU
model = Qwen3TTSModel.from_pretrained(
    "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
    dtype=torch.bfloat16,
)

ref_audio = "./myvoice01.wav"
ref_text  = "你好呀，我准备学英语，这是我2026年的学习计划"

wavs, sr = model.generate_voice_clone(
    text="I'd like speaking English and I will study everyday!",
    language="English",
    ref_audio=ref_audio,
    ref_text=ref_text,
)
sf.write("output_voice_clone2.wav", wavs[0], sr)
