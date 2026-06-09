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
