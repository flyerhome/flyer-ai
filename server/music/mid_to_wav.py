from midi2audio import FluidSynth

# 1. 初始化 FluidSynth，指定 SoundFont 音源路径
# 替换为你的 .sf2 文件实际路径（注意斜杠方向：Windows 用 \ 或 /，Mac/Linux 用 /）
sf2_path = "D:\\run\\fluidsynth\\FluidR3_GM\\FluidR3_GM.sf2"  # Windows 示例
fs = FluidSynth(sf2_path)

# 2. 转换 MID 到 MP3
input_mid = "mine.mid"    # 输入的 MID 文件路径（如当前目录下的 input.mid）
output_mp3 = "mine.mp3"  # 输出的 MP3 文件路径
fs.midi_to_audio(input_mid, output_mp3)

print(f"转换完成：{output_mp3}")
