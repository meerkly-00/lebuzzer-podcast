"""Génère un lit sonore original (libre de droits) pour les reels — ~24s, looped."""
import subprocess
from pathlib import Path

out = Path(__file__).resolve().parent.parent / "assets" / "reel_music.mp3"
out.parent.mkdir(parents=True, exist_ok=True)

D = 24
# Beat électro sport ~120 BPM : kick (0.5s), basse alternée, pluck brillant. Commas échappées pour lavfi.
kick   = r"0.9*exp(-32*mod(t\,0.5))*sin(2*PI*53*t)"
bass   = r"0.22*exp(-5*mod(t\,0.25))*sin(2*PI*(if(lt(mod(t\,1)\,0.5)\,82.41\,110.0))*t)"
pluck  = r"0.12*exp(-14*mod(t\,0.5))*(sin(2*PI*523.25*t)+0.6*sin(2*PI*784*t))"
expr = f"({kick})+({bass})+({pluck})"

cmd = [
    "ffmpeg", "-y",
    "-f", "lavfi", "-i", f"aevalsrc={expr}:d={D}:s=44100",
    "-af", "lowpass=f=13000,highpass=f=35,loudnorm=I=-15:TP=-1.5:LRA=11,alimiter=limit=0.93",
    "-c:a", "libmp3lame", "-q:a", "4",
    str(out),
]
subprocess.run(cmd, check=True, capture_output=True)
print("OK ->", str(out), round(out.stat().st_size/1024), "KB")
