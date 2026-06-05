"""Échantillons accent québécois : verse steered vs edge-tts fr-CA."""
import os, re, asyncio
from pathlib import Path
from openai import OpenAI

for line in Path(r"C:\Users\jchal\Podcast\.env").read_text(encoding="utf-8").splitlines():
    m = re.match(r"\s*OPENAI_API_KEY\s*=\s*(.+)", line)
    if m:
        os.environ["OPENAI_API_KEY"] = m.group(1).strip()

out = Path(r"C:\Users\jchal\LeBuzzer\voice_samples")
out.mkdir(exist_ok=True)

TEXTE = (
    "T'es au Buzzer. Grosse soirée hier dans la Ligue nationale. "
    "Le Canadien l'emporte cinq à trois contre Toronto, Caufield avec deux buts. "
    "En NBA, finale de fou: les Spurs arrachent le match un en prolongation. "
    "Et la bombe du jour, un échange majeur s'en vient à Montréal. On embarque."
)

QC = (
    "Parle avec un ACCENT QUÉBÉCOIS authentique, comme un animateur sportif de Montréal. "
    "Surtout PAS l'accent de France. Prononciation québécoise: 'but' se dit court et sec "
    "(pas 'bute'), les voyelles québécoises, le rythme du Québec. Énergique, naturel, rythmé."
)
QC_FORT = (
    "Tu es un animateur sportif QUÉBÉCOIS de Montréal (RDS / 98,5). Accent québécois marqué, "
    "joual léger et naturel. JAMAIS l'accent parisien/européen. Prononce 'but' bref (pas 'bute'), "
    "'Toronto', 'Canadien' à la québécoise. Débit vif, intonation vivante, du punch."
)

client = OpenAI()
for label, instr in [("3_verse_QC", QC), ("3_verse_QC_fort", QC_FORT)]:
    print(f"-> {label}")
    try:
        r = client.audio.speech.create(model="gpt-4o-mini-tts", voice="verse",
                                       input=TEXTE, response_format="mp3", instructions=instr)
        r.stream_to_file(str(out / f"{label}.mp3"))
    except Exception as e:
        print("   ERREUR:", str(e)[:200])

# edge-tts : vraies voix fr-CA (canadien)
try:
    import edge_tts
except ImportError:
    os.system("py -m pip install edge-tts -q")
    import edge_tts

async def edge(voice, path):
    await edge_tts.Communicate(TEXTE, voice).save(path)

EDGE = [
    ("edge_Antoine_frCA", "fr-CA-AntoineNeural"),
    ("edge_Jean_frCA",    "fr-CA-JeanNeural"),
    ("edge_Thierry_frCA", "fr-CA-ThierryNeural"),
    ("edge_Sylvie_frCA",  "fr-CA-SylvieNeural"),
]
for label, voice in EDGE:
    print(f"-> {label}")
    try:
        asyncio.run(edge(voice, str(out / f"{label}.mp3")))
    except Exception as e:
        print("   ERREUR:", str(e)[:200])

print("\nÉchantillons dans:", out)
