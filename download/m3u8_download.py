from pathlib import Path

m3u8_url = 'https://hls.ted.com/project_masters/11650/manifest.m3u8?intro_master_id=9294'

save_path = r'F:\study\m3u8\TED_TALK_11650'

if not Path(save_path).exists():
    Path(save_path).mkdir(parents=True, exist_ok=True)

