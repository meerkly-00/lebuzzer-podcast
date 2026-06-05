"""Distille l'épisode du jour en 5 manchettes pour le reel vidéo.

Usage: py tools/news_video_data.py output/scripts/2026-06-05.xml data/news_video/2026-06-05.json
Sortie JSON: {date, headlines:[{tag,text,hl}]}
"""
import sys, os, re, json
from pathlib import Path

# clé Anthropic : env (CI) ou .env de Presto (local)
if not os.getenv("ANTHROPIC_API_KEY"):
    envf = Path(r"C:\Users\jchal\Podcast\.env")
    if envf.exists():
        for line in envf.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\s*ANTHROPIC_API_KEY\s*=\s*(.+)", line)
            if m: os.environ["ANTHROPIC_API_KEY"] = m.group(1).strip()

import anthropic

_MOIS = ["janvier","février","mars","avril","mai","juin","juillet","août",
         "septembre","octobre","novembre","décembre"]

script_path = Path(sys.argv[1])
out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("news_video.json")
out_path.parent.mkdir(parents=True, exist_ok=True)

# date FR depuis le nom de fichier YYYY-MM-DD
try:
    y,m,d = (int(x) for x in script_path.stem.split("-"))
    date_fr = f"{d} {_MOIS[m-1]} {y}"
except Exception:
    date_fr = ""

script_xml = script_path.read_text(encoding="utf-8")

PROMPT = """Voici le script d'un podcast sport quotidien québécois (LE BUZZER).
Sors les 5 nouvelles les plus FORTES et partageables pour un reel vidéo vertical.

Pour chaque nouvelle, un objet JSON avec :
- "tag"  : la ligue, EXACTEMENT un de : LNH, NFL, NBA, FOOT, F1, MMA, QC
- "text" : la manchette, percutante, français québécois, MAX 42 caractères, sans point final
- "hl"   : UN chiffre ou mot-clé court à surligner (ex: "TRADE", "2-1", "20 ANS", "No 1"), MAX 10 caractères. "" si rien de pertinent.

Règles : commence par le fait, pas de "Le" mou. Varie les ligues si possible. Mets la nouvelle QC en valeur si elle existe.

Réponds UNIQUEMENT avec un JSON valide de cette forme, rien d'autre :
{"headlines":[{"tag":"LNH","text":"...","hl":"..."}, ...]}

Script :
""" + script_xml[:8000]

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
msg = client.messages.create(
    model=os.getenv("VIDEO_LLM_MODEL", "claude-haiku-4-5-20251001"),
    max_tokens=800,
    messages=[{"role":"user","content":PROMPT}],
)
raw = msg.content[0].text.strip()
raw = re.sub(r"^```(json)?|```$", "", raw, flags=re.MULTILINE).strip()
data = json.loads(raw)
heads = data.get("headlines", data) if isinstance(data, dict) else data
heads = heads[:5]

out = {"date": date_fr.upper(), "headlines": heads}
out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(out, ensure_ascii=False, indent=2))
print("OK ->", str(out_path))
