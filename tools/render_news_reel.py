"""Rend le template reel_news.html en MP4 1080x1920 (musique optionnelle).

Usage:
  py tools/render_news_reel.py [data.json] [sortie.mp4]
Si data.json est fourni, il est injecté comme window.__REEL_DATA.
Si assets/reel_music.mp3 existe, il est mixé en fond (bouclé, coupé à la durée).
"""
import sys, time, glob, os, json, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent   # racine du repo (portable CI + local)
TPL = (ROOT / "templates" / "reel_news.html").resolve()
MUSIC = ROOT / "assets" / "reel_music.mp3"

data_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
out = Path(sys.argv[2]) if len(sys.argv) > 2 else (ROOT / "output" / "clips" / "news_reel.mp4")
out.parent.mkdir(parents=True, exist_ok=True)
rawdir = out.parent / "_raw"; rawdir.mkdir(exist_ok=True)

init = None
if data_path and data_path.exists():
    data = json.loads(data_path.read_text(encoding="utf-8"))
    init = "window.__REEL_DATA = " + json.dumps(data, ensure_ascii=False) + ";"

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width":1080,"height":1920}, device_scale_factor=1,
                        record_video_dir=str(rawdir), record_video_size={"width":1080,"height":1920})
    pg = ctx.new_page()
    if init:
        pg.add_init_script(init)
    t0 = time.time()
    pg.goto(TPL.as_uri())
    started = False
    for _ in range(200):
        try:
            if pg.evaluate("window.__started===true"): started = True; break
        except Exception: pass
        time.sleep(0.1)
    mount_off = time.time() - t0
    dur_ms = pg.evaluate("window.__DURATION_MS") or 23000
    dur = dur_ms/1000.0
    print(f"started={started} mount_off={mount_off:.2f}s duration={dur:.1f}s")
    time.sleep(dur + 0.8)
    ctx.close(); b.close()

raw = max(glob.glob(str(rawdir / "*.webm")), key=os.path.getmtime)
start = max(0, mount_off - 0.15)

vf = "fps=30,scale=1080:1920:flags=lanczos,setsar=1,format=yuv420p"
if MUSIC.exists():
    cmd = ["ffmpeg","-y","-ss",f"{start:.2f}","-t",f"{dur:.2f}","-i",raw,
           "-stream_loop","-1","-i",str(MUSIC),
           "-vf",vf,"-map","0:v:0","-map","1:a:0",
           "-c:v","libx264","-preset","slow","-crf","19",
           "-c:a","aac","-b:a","160k","-shortest","-movflags","+faststart",str(out)]
else:
    cmd = ["ffmpeg","-y","-ss",f"{start:.2f}","-t",f"{dur:.2f}","-i",raw,
           "-vf",vf,"-c:v","libx264","-preset","slow","-crf","19","-an","-movflags","+faststart",str(out)]
subprocess.run(cmd, check=True, capture_output=True)
print("MP4:", out, "-", round(out.stat().st_size/1024), "KB", "| audio:", MUSIC.exists())
