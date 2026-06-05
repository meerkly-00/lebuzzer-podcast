"""Génère des échantillons de voix TTS pour comparer le ton (Le Buzzer)."""
import os, re
from pathlib import Path
from openai import OpenAI

# clé depuis le .env de Presto (même compte OpenAI)
for line in Path(r"C:\Users\jchal\Podcast\.env").read_text(encoding="utf-8").splitlines():
    m = re.match(r"\s*OPENAI_API_KEY\s*=\s*(.+)", line)
    if m:
        os.environ["OPENAI_API_KEY"] = m.group(1).strip()

client = OpenAI()
out = Path(r"C:\Users\jchal\LeBuzzer\voice_samples")
out.mkdir(exist_ok=True)

# Extrait sport réel, punchy
TEXTE = (
    "T'es au Buzzer. Grosse soirée hier dans la Ligue nationale. "
    "Le Canadien l'emporte cinq à trois contre Toronto, Caufield avec deux buts. "
    "En NBA, finale de fou: les Spurs arrachent le match un en prolongation. "
    "Et la bombe du jour, un échange majeur s'en vient à Montréal. On embarque."
)

ENERGIE = (
    "Parle comme un animateur sportif québécois: énergique, naturel, rythmé. "
    "Débit vif et fluide, intonation vivante, de l'enthousiasme sans crier. "
    "Enchaîne les phrases sans traîner."
)
POSE = (
    "Parle comme un animateur sport posé mais dynamique: ton confiant, naturel, "
    "rythme soutenu, intonation expressive. Pas monotone, pas lent."
)

# (label, model, voice, instructions, speed)
SAMPLES = [
    ("1_ash_energie",   "gpt-4o-mini-tts", "ash",   ENERGIE, None),
    ("2_onyx_energie",  "gpt-4o-mini-tts", "onyx",  ENERGIE, None),
    ("3_verse_energie", "gpt-4o-mini-tts", "verse", ENERGIE, None),
    ("4_ballad_pose",   "gpt-4o-mini-tts", "ballad", POSE,   None),
    ("5_onyx_hd_x115",  "tts-1-hd",        "onyx",  None,     1.15),
    ("6_ash_hd_x115",   "tts-1-hd",        "ash",   None,     1.15),
]

for label, model, voice, instr, speed in SAMPLES:
    print(f"-> {label} ({model}/{voice})")
    kwargs = dict(model=model, voice=voice, input=TEXTE, response_format="mp3")
    if instr and "gpt-4o" in model:
        kwargs["instructions"] = instr
    if speed:
        kwargs["speed"] = speed
    try:
        r = client.audio.speech.create(**kwargs)
        r.stream_to_file(str(out / f"{label}.mp3"))
    except Exception as e:
        print("   ERREUR:", str(e)[:200])

print("\nÉchantillons dans:", out)
