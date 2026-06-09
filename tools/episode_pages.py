"""Génère une page HTML par épisode de Le Buzzer (archive permanente + SEO/AEO)."""

import html
import re
from datetime import date as date_cls, datetime, timedelta
from pathlib import Path
from xml.etree.ElementTree import parse as parse_xml

BASE_URL = "https://www.lebuzzer.com"
SERIES_NAME = "LE BUZZER"
ARTWORK_URL = "https://www.lebuzzer.com/artwork.png"
SPOTIFY_URL = "https://open.spotify.com/show/033sjQPhZam8dG88KFNyzt"
APPLE_URL = "https://podcasts.apple.com/us/podcast/le-buzzer/id1896876716"
KEEP_DAYS = 7
MOIS_FR = ["", "janvier", "février", "mars", "avril", "mai", "juin",
           "juillet", "août", "septembre", "octobre", "novembre", "décembre"]


def parse_script(path):
    """Parse un script .xml en dict {date, intro, chapters:[{titre,paragraphs}], outro}."""
    raw = Path(path).read_text(encoding="utf-8")
    m = re.search(r"<script>(.*)</script>", raw, re.DOTALL)
    if not m:
        raise ValueError(f"Aucun bloc <script> trouvé dans {path}")
    body = m.group(1)

    def _tag(name):
        t = re.search(rf"<{name}>(.*?)</{name}>", body, re.DOTALL)
        return t.group(1).strip() if t else ""

    chapters = []
    for cm in re.finditer(r'<chapitre titre="([^"]+)">(.*?)</chapitre>', body, re.DOTALL):
        text = cm.group(2).strip()
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        chapters.append({"titre": cm.group(1).strip(), "paragraphs": paragraphs})

    return {
        "date": Path(path).stem,
        "intro": _tag("intro"),
        "chapters": chapters,
        "outro": _tag("outro"),
    }


def french_date(iso):
    d = datetime.strptime(iso, "%Y-%m-%d").date()
    return f"{d.day} {MOIS_FR[d.month]} {d.year}"


def is_audio_active(iso, today=None, keep_days=KEEP_DAYS):
    today = today or date_cls.today()
    ep_date = datetime.strptime(iso, "%Y-%m-%d").date()
    return ep_date > today - timedelta(days=keep_days)


def iso_duration(seconds):
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    out = "PT"
    if h:
        out += f"{h}H"
    if m:
        out += f"{m}M"
    if s or out == "PT":
        out += f"{s}S"
    return out


def meta_description(intro, limit=155):
    text = " ".join(intro.split())
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0] + "…"


_ITUNES = "{http://www.itunes.com/dtds/podcast-1.0.dtd}"


def episode_metadata(iso, feed_path, today=None):
    """Métadonnées d'un épisode. Lit feed.xml si l'item y est ; sinon mode archivé."""
    title = f"{SERIES_NAME} — édition du {french_date(iso)}"
    meta = {
        "title": title,
        "audio_url": None,
        "duration_sec": None,
        "audio_active": is_audio_active(iso, today=today),
    }
    feed_path = Path(feed_path)
    if not feed_path.exists():
        return meta
    root = parse_xml(feed_path).getroot()
    for item in root.iter("item"):
        enc = item.find("enclosure")
        url = enc.get("url") if enc is not None else ""
        if iso in url:
            t = item.find("title")
            if t is not None and t.text:
                meta["title"] = t.text
            meta["audio_url"] = url
            dur = item.find(f"{_ITUNES}duration")
            if dur is not None and dur.text and dur.text.isdigit():
                meta["duration_sec"] = int(dur.text)
            meta["audio_active"] = True
            break
    return meta


_CSS = """
:root{--bg:#0D0D0D;--panel:#16140F;--fg:#F1FAEE;--muted:rgba(241,250,238,.6);
--hair:rgba(241,250,238,.15);--yellow:#FFD60A;--red:#E63946}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
font-family:'Archivo',system-ui,sans-serif;line-height:1.65;
-webkit-font-smoothing:antialiased}
.wrap{max-width:760px;margin:0 auto;padding:32px 20px 80px}
a{color:var(--yellow)}
.crumb{font:600 13px/1.4 'Oswald',sans-serif;text-transform:uppercase;
letter-spacing:.04em;color:var(--muted);margin-bottom:24px}
.crumb a{color:var(--muted);text-decoration:none}
h1{font-family:'Anton',sans-serif;font-weight:400;font-size:clamp(30px,7vw,52px);
line-height:1.02;text-transform:uppercase;margin:0 0 8px}
h1 .hl{color:var(--red)}
.date{font:600 14px 'Oswald',sans-serif;text-transform:uppercase;
letter-spacing:.05em;color:var(--yellow);margin-bottom:24px}
.lede{font-size:1.12rem;color:var(--fg);border-left:3px solid var(--yellow);
padding-left:16px;margin:0 0 28px}
audio{width:100%;margin:0 0 28px}
.archived{background:var(--panel);border:1px solid var(--hair);border-radius:10px;
padding:16px 18px;margin:0 0 28px;color:var(--muted);font-size:.95rem}
h2{font-family:'Oswald',sans-serif;font-weight:700;text-transform:uppercase;
letter-spacing:.02em;font-size:1.35rem;margin:36px 0 10px;
padding-top:18px;border-top:1px solid var(--hair)}
p{margin:0 0 16px}
.listen{margin-top:40px;padding-top:24px;border-top:1px solid var(--hair);
font:600 14px 'Oswald',sans-serif;text-transform:uppercase;letter-spacing:.04em}
.listen a{margin-right:18px}
"""


def render_episode_page(content, meta):
    iso = content["date"]
    fdate = french_date(iso)
    url = f"{BASE_URL}/episodes/{iso}/"
    desc = meta_description(content["intro"])
    title_tag = f"{meta['title']} — transcript & résumé"

    if meta["audio_active"] and meta["audio_url"]:
        player = f'<audio controls preload="none" src="{html.escape(meta["audio_url"])}"></audio>'
    else:
        player = ('<div class="archived">Épisode archivé — l\'audio n\'est plus '
                  'disponible (les épisodes restent en ligne 7 jours). '
                  f'<a href="{BASE_URL}/">Écouter l\'édition du jour →</a></div>')

    chapters_html = ""
    for ch in content["chapters"]:
        paras = "\n".join(f"<p>{html.escape(p)}</p>" for p in ch["paragraphs"])
        chapters_html += f'<h2>{html.escape(ch["titre"])}</h2>\n{paras}\n'

    podcast_ld = {
        "@context": "https://schema.org",
        "@type": "PodcastEpisode",
        "name": meta["title"],
        "datePublished": iso,
        "url": url,
        "description": desc,
        "inLanguage": "fr-CA",
        "partOfSeries": {"@type": "PodcastSeries", "name": SERIES_NAME, "url": BASE_URL + "/"},
    }
    if meta["duration_sec"]:
        podcast_ld["timeRequired"] = iso_duration(meta["duration_sec"])
    if meta["audio_active"] and meta["audio_url"]:
        podcast_ld["associatedMedia"] = {"@type": "AudioObject", "contentUrl": meta["audio_url"]}

    breadcrumb_ld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Accueil", "item": BASE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": "Épisodes", "item": BASE_URL + "/episodes/"},
            {"@type": "ListItem", "position": 3, "name": fdate, "item": url},
        ],
    }
    import json as _json
    ld = (f'<script type="application/ld+json">{_json.dumps(podcast_ld, ensure_ascii=False)}</script>\n'
          f'<script type="application/ld+json">{_json.dumps(breadcrumb_ld, ensure_ascii=False)}</script>')

    return f"""<!DOCTYPE html>
<html lang="fr-CA"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title_tag)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow">
<meta name="theme-color" content="#0D0D0D">
<meta property="og:type" content="article">
<meta property="og:title" content="{html.escape(meta['title'])}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{ARTWORK_URL}">
<meta property="og:locale" content="fr_CA">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Archivo:wght@400;600&family=Oswald:wght@600;700&display=swap" rel="stylesheet">
<style>{_CSS}</style>
{ld}
</head><body>
<div class="wrap">
<nav class="crumb"><a href="{BASE_URL}/">Accueil</a> › Épisodes › {fdate}</nav>
<h1>{html.escape(meta['title'])}</h1>
<div class="date">{fdate}</div>
<p class="lede">{html.escape(content['intro'])}</p>
{player}
{chapters_html}<div class="listen">Écouter : <a href="{SPOTIFY_URL}">Spotify</a><a href="{APPLE_URL}">Apple Podcasts</a></div>
</div>
</body></html>
"""
