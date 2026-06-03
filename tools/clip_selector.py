#!/usr/bin/env python3
"""LE BUZZER — Sélection des meilleurs moments pour clips verticaux (LLM Anthropic).

Lit output/scripts/<date>.xml, demande au LLM 2-3 segments punchy self-contained,
et écrit output/clips/<date>_clips.json (hook, segment_text, caption, hashtags...).

Usage: python tools/clip_selector.py [YYYY-MM-DD] [--n 2]
Env  : ANTHROPIC_API_KEY (ou fichier pointé par BUZZER_ENV / .env local).
"""
import os, sys, re, json, glob, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")

def load_env():
    # cherche une clé dans l'environnement, sinon dans des .env connus
    if os.environ.get("ANTHROPIC_API_KEY"):
        return
    candidates = [os.environ.get("BUZZER_ENV",""), os.path.join(ROOT, ".env"),
                  os.path.join(ROOT, "..", "Podcast", ".env")]
    for c in candidates:
        if c and os.path.isfile(c):
            for line in open(c, encoding="utf-8"):
                line=line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k,_,v=line.partition("=")
                    v=v.strip().strip('"').strip("'")
                    if k.strip() and k.strip() not in os.environ:
                        os.environ[k.strip()]=v
            if os.environ.get("ANTHROPIC_API_KEY"):
                return

def latest_date():
    files=sorted(glob.glob(os.path.join(ROOT,"output","scripts","*.xml")))
    if not files: sys.exit("Aucun script dans output/scripts/")
    return os.path.basename(files[-1])[:-4]

def read_script(date):
    p=os.path.join(ROOT,"output","scripts",date+".xml")
    raw=open(p,encoding="utf-8").read()
    raw=re.sub(r"^```xml\s*","",raw.strip()); raw=re.sub(r"```$","",raw.strip())
    # texte lisible
    txt=re.sub(r"<[^>]+>"," ",raw)
    txt=re.sub(r"\s+"," ",txt).strip()
    return raw, txt

PROMPT = """Voici un script de podcast sport quotidien québécois (LE BUZZER).
Identifie les {n} moments les plus punchy / partageables pour un clip vertical 30-60s sur TikTok/Reels.

Critères:
- Self-contained: compréhensible isolé du reste de l'épisode.
- WOW / drama / chiffre marquant: la phrase qui fait "ah ouain?!".
- Durée audio 25-55s lue à voix haute (~75-160 mots).
- Hook fort dans les 5 premiers mots.
- Ton: québécois, sport-broadcast, punchy.

SCRIPT:
{script}

Réponds UNIQUEMENT avec du JSON valide, sans texte autour, ce format exact:
{{"clips":[{{"rank":1,"hook_text":"...","segment_text":"texte exact à lire à voix haute, 75-160 mots, fluide","estimated_duration_sec":42,"theme":"Hockey|NBA|Foot|F1|MMA|Potin","social_caption":"caption courte avec emoji","hashtags":["#lebuzzer","#..."]}}]}}"""

def call_llm(script_text, n):
    body=json.dumps({
        "model": MODEL,
        "max_tokens": 2000,
        "messages":[{"role":"user","content":PROMPT.format(n=n, script=script_text)}]
    }).encode("utf-8")
    req=urllib.request.Request("https://api.anthropic.com/v1/messages", data=body, headers={
        "x-api-key": os.environ["ANTHROPIC_API_KEY"],
        "anthropic-version":"2023-06-01",
        "content-type":"application/json",
    })
    with urllib.request.urlopen(req, timeout=120) as r:
        data=json.loads(r.read())
    text="".join(b.get("text","") for b in data.get("content",[]))
    m=re.search(r"\{.*\}", text, re.S)
    return json.loads(m.group(0))

def main():
    load_env()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY manquante.")
    args=[a for a in sys.argv[1:] if not a.startswith("--")]
    n=2
    if "--n" in sys.argv: n=int(sys.argv[sys.argv.index("--n")+1])
    date=args[0] if args else latest_date()
    raw, txt = read_script(date)
    print(f"[selector] date={date} mots~{len(txt.split())} modele={MODEL}")
    res=call_llm(txt, n)
    clips=res.get("clips",[])[:n]
    out=os.path.join(ROOT,"output","clips",date+"_clips.json")
    json.dump({"date":date,"clips":clips}, open(out,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"[selector] {len(clips)} clips -> {out}")
    for c in clips:
        print(f"  #{c.get('rank')} [{c.get('theme')}] {c.get('hook_text')}  (~{c.get('estimated_duration_sec')}s)")
    return out

if __name__=="__main__":
    main()
