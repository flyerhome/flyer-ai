from TTS.api import TTS

# 自动下载模型，无需编译
tts = TTS(model_name="tts_models/zh-CN/best/tacotron2-DDC_ph", progress_bar=True)

# ======================
# 语音克隆核心代码
# ======================
tts.tts_to_file(
    text="你好，这是AI克隆出来的声音，非常自然。",
    speaker_wav="myvoice.wav",  # 你的声音 5~10秒
    language="zh-cn",
    file_path="output.wav"
)

print("✅ 生成完成！output.wav 就是克隆后的声音")
