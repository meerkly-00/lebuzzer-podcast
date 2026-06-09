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
