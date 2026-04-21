from midiutil import MIDIFile
import subprocess
import os
from midi2audio import FluidSynth

class MusicObj:
    midi = None
    track = None
    time = None
    channel = None
    program = None
    speed = None
    file_name = None

    def __init__(self, speed=120, program=1, tracks=0, channel=0):
        self.midi = MIDIFile(1)
        self.track = tracks
        self.time = 0
        self.channel = channel
        self.program = program
        self.speed = speed
        self.midi.addTempo(self.track, self.time, self.speed)
        self.midi.addProgramChange(self.track, self.channel, self.time, self.program)

    def press(self, scale_val, time_long=1, volume=100):
        self.midi.addNote(self.track, self.channel, scale_val, self.time, time_long, volume)  # C4
        self.time += time_long

    def save_wav(self):
        sf2_path = os.getenv("FS_PATH")  # Windows 示例
        fs = FluidSynth(sf2_path)
        # 2. 转换 MID 到 MP3
        input_mid = self.file_name  # 输入的 MID 文件路径（如当前目录下的 input.mid）
        output_mp3 = self.file_name.replace(".mid", ".wav")  # 输出的 MP3 文件路径
        fs.midi_to_audio(input_mid, output_mp3)
        os.remove(input_mid)
        self.file_name = output_mp3
        print(f"转换完成：{output_mp3}")

    def save(self, file_name):
        if os.path.exists(file_name):
            os.remove(file_name)
        self.file_name = file_name
        with open(file_name, "wb") as ff:
            self.midi.writeFile(ff)
        self.save_wav()


    def play(self):
        # 2. 调用系统播放器播放
        if os.name == 'nt':  # Windows
            os.startfile(self.file_name)  # 用默认程序打开（通常是媒体播放器）
        elif os.name == 'posix':  # macOS/Linux
            subprocess.call(['open' if os.path.exists('/usr/bin/open') else 'xdg-open', self.file_name])
