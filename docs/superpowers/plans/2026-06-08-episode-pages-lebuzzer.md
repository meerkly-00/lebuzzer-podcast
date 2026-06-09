# Pages par épisode (Le Buzzer, Phase 1) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Générer une page HTML permanente et indexable par épisode de Le Buzzer (résumé + transcript + schema), backfillée et branchée sur le workflow quotidien.

**Architecture:** Un script autonome `tools/episode_pages.py` (pattern Le Buzzer — pas de `src/` local, l'engine est dans la dépendance `media-factory`) parse les scripts versionnés `output/scripts/*.xml`, lit `feed.xml` pour les métadonnées audio, rend une page HTML légère par épisode dans `site/episodes/AAAA-MM-JJ/index.html`, et régénère `site/sitemap.xml`. Le workflow `buzzer.yml` l'exécute après la génération du jour et commit le résultat ; GitHub Pages republie au push.

**Tech Stack:** Python 3.12, stdlib uniquement (`re`, `pathlib`, `datetime`, `xml.etree`, `html`). Tests : `pytest` (dev). Aucune dépendance de templating (HTML construit en Python).

**Déviations assumées vs spec** : (1) `tools/episode_pages.py` au lieu de `src/episode_pages.py` (Le Buzzer n'a pas de `src/`, ses scripts vivent dans `tools/`). (2) Template HTML inline dans le module au lieu de `templates/episode.html` (nombre de chapitres variable + zéro dépendance).

---

## File Structure

- **Create** `tools/episode_pages.py` — module + CLI : parsing, métadonnées, rendu HTML, sitemap, orchestration.
- **Create** `tools/test_episode_pages.py` — tests pytest des fonctions pures.
- **Modify** `.github/workflows/buzzer.yml` — étape de génération + ajout au commit quotidien.
- **Generated (non commités à la main)** `site/episodes/AAAA-MM-JJ/index.html`, `site/sitemap.xml`.

Constantes en tête de module (`tools/episode_pages.py`) :

```python
BASE_URL = "https://www.lebuzzer.com"
SERIES_NAME = "LE BUZZER"
ARTWORK_URL = "https://www.lebuzzer.com/artwork.png"
SPOTIFY_URL = "https://open.spotify.com/show/033sjQPhZam8dG88KFNyzt"
APPLE_URL = "https://podcasts.apple.com/us/podcast/le-buzzer/id1896876716"
KEEP_DAYS = 7
MOIS_FR = ["", "janvier", "février", "mars", "avril", "mai", "juin",
           "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
```

---

### Task 1: Squelette du module + `parse_script`

**Files:**
- Create: `tools/episode_pages.py`
- Test: `tools/test_episode_pages.py`

- [ ] **Step 1: Installer pytest (dev)**

Run: `python -m pip install pytest`
Expected: `Successfully installed pytest-...`

- [ ] **Step 2: Écrire le test qui échoue**

Créer `tools/test_episode_pages.py` :

```python
import textwrap
from pathlib import Path
import tools.episode_pages as ep


SAMPLE = textwrap.dedent('''\
    ```xml
    <script>
      <intro>T'es au Buzzer. Eriksen s'effondre. On embarque.</intro>

      <chapitre titre="Top international">
        Premier paragraphe du top international.

        Deuxième paragraphe.
      </chapitre>

      <chapitre titre="Le buzz du jour">
        Le buzz du jour ici.
      </chapitre>

      <outro>À demain.</outro>
    </script>
    ```
    ''')


def test_parse_script(tmp_path):
    p = tmp_path / "2026-06-08.xml"
    p.write_text(SAMPLE, encoding="utf-8")
    data = ep.parse_script(p)
    assert data["date"] == "2026-06-08"
    assert data["intro"] == "T'es au Buzzer. Eriksen s'effondre. On embarque."
    assert data["outro"] == "À demain."
    assert len(data["chapters"]) == 2
    assert data["chapters"][0]["titre"] == "Top international"
    assert data["chapters"][0]["paragraphs"] == [
        "Premier paragraphe du top international.",
        "Deuxième paragraphe.",
    ]
    assert data["chapters"][1]["titre"] == "Le buzz du jour"
```

- [ ] **Step 3: Lancer le test, vérifier l'échec**

Run: `python -m pytest tools/test_episode_pages.py::test_parse_script -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'tools.episode_pages'` ou `AttributeError: parse_script`)

- [ ] **Step 4: Implémenter le squelette + `parse_script`**

Créer `tools/episode_pages.py` :

```python
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
```

- [ ] **Step 5: Lancer le test, vérifier le succès**

Run: `python -m pytest tools/test_episode_pages.py::test_parse_script -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add tools/episode_pages.py tools/test_episode_pages.py
git commit -m "feat(episode-pages): parse_script + squelette module [skip ci]"
```

---

### Task 2: `french_date`, `is_audio_active`, `iso_duration`, `meta_description`

**Files:**
- Modify: `tools/episode_pages.py`
- Test: `tools/test_episode_pages.py`

- [ ] **Step 1: Écrire les tests qui échouent**

Ajouter à `tools/test_episode_pages.py` :

```python
from datetime import date


def test_french_date():
    assert ep.french_date("2026-06-08") == "8 juin 2026"
    assert ep.french_date("2026-12-01") == "1 décembre 2026"


def test_is_audio_active():
    today = date(2026, 6, 8)
    assert ep.is_audio_active("2026-06-08", today=today) is True
    assert ep.is_audio_active("2026-06-02", today=today) is True   # 6 jours
    assert ep.is_audio_active("2026-06-01", today=today) is False  # 7 jours
    assert ep.is_audio_active("2026-05-20", today=today) is False


def test_iso_duration():
    assert ep.iso_duration(330) == "PT5M30S"
    assert ep.iso_duration(3661) == "PT1H1M1S"
    assert ep.iso_duration(60) == "PT1M"
    assert ep.iso_duration(0) == "PT0S"


def test_meta_description():
    assert ep.meta_description("Court résumé.") == "Court résumé."
    long = "mot " * 60
    out = ep.meta_description(long)
    assert len(out) <= 156
    assert out.endswith("…")
```

- [ ] **Step 2: Lancer, vérifier l'échec**

Run: `python -m pytest tools/test_episode_pages.py -k "french_date or audio_active or iso_duration or meta_description" -v`
Expected: FAIL (`AttributeError`)

- [ ] **Step 3: Implémenter**

Ajouter à `tools/episode_pages.py` :

```python
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
```

- [ ] **Step 4: Lancer, vérifier le succès**

Run: `python -m pytest tools/test_episode_pages.py -k "french_date or audio_active or iso_duration or meta_description" -v`
Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add tools/episode_pages.py tools/test_episode_pages.py
git commit -m "feat(episode-pages): helpers date/durée/description [skip ci]"
```

---

### Task 3: `episode_metadata` (lecture de feed.xml)

**Files:**
- Modify: `tools/episode_pages.py`
- Test: `tools/test_episode_pages.py`

- [ ] **Step 1: Écrire le test qui échoue**

Ajouter à `tools/test_episode_pages.py` :

```python
FEED_SAMPLE = '''<?xml version="1.0" ?>
<rss xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" version="2.0">
  <channel>
    <title>LE BUZZER</title>
    <item>
      <title>LE BUZZER — édition du 8 juin 2026</title>
      <guid isPermaLink="false">https://github.com/x/releases/download/2026-06-08/2026-06-08.mp3</guid>
      <enclosure url="https://github.com/x/releases/download/2026-06-08/2026-06-08.mp3" type="audio/mpeg" length="5714749"/>
      <itunes:duration>330</itunes:duration>
    </item>
  </channel>
</rss>'''


def test_episode_metadata_in_feed(tmp_path):
    feed = tmp_path / "feed.xml"
    feed.write_text(FEED_SAMPLE, encoding="utf-8")
    meta = ep.episode_metadata("2026-06-08", feed, today=date(2026, 6, 8))
    assert meta["title"] == "LE BUZZER — édition du 8 juin 2026"
    assert meta["audio_url"].endswith("2026-06-08.mp3")
    assert meta["duration_sec"] == 330
    assert meta["audio_active"] is True


def test_episode_metadata_not_in_feed(tmp_path):
    feed = tmp_path / "feed.xml"
    feed.write_text(FEED_SAMPLE, encoding="utf-8")
    meta = ep.episode_metadata("2026-05-20", feed, today=date(2026, 6, 8))
    assert meta["title"] == "LE BUZZER — édition du 20 mai 2026"
    assert meta["audio_url"] is None
    assert meta["audio_active"] is False
```

- [ ] **Step 2: Lancer, vérifier l'échec**

Run: `python -m pytest tools/test_episode_pages.py -k episode_metadata -v`
Expected: FAIL (`AttributeError: episode_metadata`)

- [ ] **Step 3: Implémenter**

Ajouter à `tools/episode_pages.py` :

```python
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
```

- [ ] **Step 4: Lancer, vérifier le succès**

Run: `python -m pytest tools/test_episode_pages.py -k episode_metadata -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add tools/episode_pages.py tools/test_episode_pages.py
git commit -m "feat(episode-pages): episode_metadata depuis feed.xml [skip ci]"
```

---

### Task 4: `render_episode_page` (HTML + schema)

**Files:**
- Modify: `tools/episode_pages.py`
- Test: `tools/test_episode_pages.py`

- [ ] **Step 1: Écrire le test qui échoue**

Ajouter à `tools/test_episode_pages.py` :

```python
import json


def _render(date_iso, audio_active):
    content = {
        "date": date_iso,
        "intro": "Résumé de l'épisode.",
        "chapters": [{"titre": "Top international", "paragraphs": ["Para un.", "Para deux."]}],
        "outro": "À demain.",
    }
    meta = {
        "title": f"LE BUZZER — édition du {ep.french_date(date_iso)}",
        "audio_url": "https://github.com/x/2026-06-08.mp3" if audio_active else None,
        "duration_sec": 330 if audio_active else None,
        "audio_active": audio_active,
    }
    return ep.render_episode_page(content, meta)


def test_render_active_episode():
    out = _render("2026-06-08", True)
    assert '<html lang="fr-CA">' in out
    assert "<h1" in out and "8 juin 2026" in out
    assert "Top international" in out and "Para un." in out and "Para deux." in out
    assert "<audio" in out and "2026-06-08.mp3" in out
    assert 'rel="canonical" href="https://www.lebuzzer.com/episodes/2026-06-08/"' in out
    # JSON-LD valide contenant PodcastEpisode + BreadcrumbList
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', out, re.DOTALL)
    assert blocks, "aucun bloc JSON-LD"
    types = [json.loads(b)["@type"] for b in blocks]
    assert "PodcastEpisode" in types
    assert "BreadcrumbList" in types


def test_render_archived_episode():
    out = _render("2026-05-20", False)
    assert "<audio" not in out
    assert "archivé" in out.lower()
```

- [ ] **Step 2: Lancer, vérifier l'échec**

Run: `python -m pytest tools/test_episode_pages.py -k render -v`
Expected: FAIL (`AttributeError: render_episode_page`)

- [ ] **Step 3: Implémenter le rendu + CSS de marque**

Ajouter à `tools/episode_pages.py` :

```python
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
```

- [ ] **Step 4: Lancer, vérifier le succès**

Run: `python -m pytest tools/test_episode_pages.py -k render -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add tools/episode_pages.py tools/test_episode_pages.py
git commit -m "feat(episode-pages): rendu HTML + schema PodcastEpisode/BreadcrumbList [skip ci]"
```

---

### Task 5: `build_sitemap`

**Files:**
- Modify: `tools/episode_pages.py`
- Test: `tools/test_episode_pages.py`

- [ ] **Step 1: Écrire le test qui échoue**

Ajouter à `tools/test_episode_pages.py` :

```python
def test_build_sitemap(tmp_path):
    site = tmp_path / "site"
    site.mkdir()
    ep.build_sitemap(["2026-06-08", "2026-06-07"], site)
    xml = (site / "sitemap.xml").read_text(encoding="utf-8")
    assert "https://www.lebuzzer.com/" in xml
    assert "https://www.lebuzzer.com/feed.xml" in xml
    assert "https://www.lebuzzer.com/episodes/2026-06-08/" in xml
    assert "https://www.lebuzzer.com/episodes/2026-06-07/" in xml
    assert xml.count("<url>") == 4  # home + feed + 2 épisodes
```

- [ ] **Step 2: Lancer, vérifier l'échec**

Run: `python -m pytest tools/test_episode_pages.py -k sitemap -v`
Expected: FAIL (`AttributeError: build_sitemap`)

- [ ] **Step 3: Implémenter**

Ajouter à `tools/episode_pages.py` :

```python
def build_sitemap(dates, site_dir):
    """Écrit site/sitemap.xml : home + feed + une URL par épisode (dates triées desc)."""
    urls = [f"{BASE_URL}/", f"{BASE_URL}/feed.xml"]
    urls += [f"{BASE_URL}/episodes/{d}/" for d in sorted(set(dates), reverse=True)]
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        changefreq = "daily" if u.endswith("/") and "/episodes/" not in u else "monthly"
        lines.append(f"  <url>\n    <loc>{u}</loc>\n    <changefreq>{changefreq}</changefreq>\n  </url>")
    lines.append("</urlset>\n")
    (Path(site_dir) / "sitemap.xml").write_text("\n".join(lines), encoding="utf-8")
```

- [ ] **Step 4: Lancer, vérifier le succès**

Run: `python -m pytest tools/test_episode_pages.py -k sitemap -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tools/episode_pages.py tools/test_episode_pages.py
git commit -m "feat(episode-pages): build_sitemap [skip ci]"
```

---

### Task 6: `build_all` + CLI + backfill

**Files:**
- Modify: `tools/episode_pages.py`
- Test: `tools/test_episode_pages.py`

- [ ] **Step 1: Écrire le test qui échoue**

Ajouter à `tools/test_episode_pages.py` :

```python
def test_build_all(tmp_path):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "2026-06-08.xml").write_text(SAMPLE, encoding="utf-8")
    (scripts / "2026-06-07.xml").write_text(SAMPLE.replace("06-08", "06-07"), encoding="utf-8")
    feed = tmp_path / "feed.xml"
    feed.write_text(FEED_SAMPLE, encoding="utf-8")
    site = tmp_path / "site"
    site.mkdir()
    n = ep.build_all(scripts, site, feed, today=date(2026, 6, 8))
    assert n == 2
    page = site / "episodes" / "2026-06-08" / "index.html"
    assert page.exists()
    assert "Top international" in page.read_text(encoding="utf-8")
    assert (site / "sitemap.xml").exists()
```

- [ ] **Step 2: Lancer, vérifier l'échec**

Run: `python -m pytest tools/test_episode_pages.py -k build_all -v`
Expected: FAIL (`AttributeError: build_all`)

- [ ] **Step 3: Implémenter `build_all` + bloc CLI**

Ajouter à `tools/episode_pages.py` :

```python
def build_all(scripts_dir, site_dir, feed_path, today=None):
    """Génère une page par script + le sitemap. Retourne le nombre de pages écrites."""
    scripts_dir, site_dir = Path(scripts_dir), Path(site_dir)
    dates = []
    for script in sorted(scripts_dir.glob("*.xml")):
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", script.stem):
            continue
        content = parse_script(script)
        if not content["chapters"]:
            continue
        meta = episode_metadata(content["date"], feed_path, today=today)
        html_out = render_episode_page(content, meta)
        out_dir = site_dir / "episodes" / content["date"]
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(html_out, encoding="utf-8")
        dates.append(content["date"])
    build_sitemap(dates, site_dir)
    return len(dates)


if __name__ == "__main__":
    repo = Path(__file__).resolve().parent.parent
    count = build_all(repo / "output" / "scripts", repo / "site", repo / "feed.xml")
    print(f"{count} page(s) d'épisode générée(s) dans site/episodes/ + sitemap.xml")
```

- [ ] **Step 4: Lancer, vérifier le succès (tous les tests)**

Run: `python -m pytest tools/test_episode_pages.py -v`
Expected: PASS (tous : parse, helpers, metadata, render×2, sitemap, build_all)

- [ ] **Step 5: Backfill réel + inspection manuelle**

Run: `python tools/episode_pages.py`
Expected: `7 page(s) d'épisode générée(s) ...` (≈ scripts versionnés présents)

Run: `python -c "import os; print(sorted(os.listdir('site/episodes')))"`
Expected: liste des dates (ex. `['2026-06-02', ..., '2026-06-08']`)

Vérifier le poids : `python -c "import os;p='site/episodes/2026-06-08/index.html';print(os.path.getsize(p),'octets')"`
Expected: < 50000

Ouvrir `site/episodes/2026-06-08/index.html` dans un navigateur : transcript lisible, lecteur audio présent (épisode du jour), style Le Buzzer.

- [ ] **Step 6: Commit (code + backfill)**

```bash
git add tools/episode_pages.py tools/test_episode_pages.py site/episodes site/sitemap.xml
git commit -m "feat(episode-pages): build_all, CLI et backfill des épisodes existants [skip ci]"
```

---

### Task 7: Intégration au workflow quotidien `buzzer.yml`

**Files:**
- Modify: `.github/workflows/buzzer.yml`

- [ ] **Step 1: Vérifier la config GitHub Pages (avant de modifier)**

Run: `gh api repos/meerkly-00/lebuzzer-podcast/pages --jq '{source: .source, build_type: .build_type, html_url: .html_url}'`
Expected attendu : `build_type: "legacy"` (deploy from branch) et `source.path` = `/` ou `/site`.
- Si `build_type: legacy` → un push sur `main` republie même avec `[skip ci]` (ce qui ne concerne que GitHub Actions). Continuer.
- Si `build_type: workflow` (GitHub Actions) → noter qu'il faudra que le commit quotidien NE contienne PAS `[skip ci]` pour le path Pages, ou déclencher le workflow Pages. Documenter le cas dans le commit message et adapter à l'étape 2.

Si `source.path` = `/` (et non `/site`), les pages doivent être servies depuis `site/` autrement (Worker/règle). Confirmer où `index.html` est réellement servi en testant `curl -sI https://www.lebuzzer.com/episodes/2026-06-08/` APRÈS le premier déploiement (Task 8).

- [ ] **Step 2: Ajouter l'étape de génération et étendre le commit**

Dans `.github/workflows/buzzer.yml`, APRÈS l'étape « Générer LE BUZZER du jour » (et avant « Sauvegarder feed.xml... »), insérer :

```yaml
      - name: Générer les pages par épisode + sitemap
        run: python tools/episode_pages.py
```

Puis, dans l'étape « Sauvegarder feed.xml, contexte et script », modifier la ligne `git add` pour inclure les pages et le sitemap. Remplacer :

```yaml
          git add feed.xml data/context.json "output/scripts/$DATE.xml"
```

par :

```yaml
          git add feed.xml data/context.json "output/scripts/$DATE.xml" site/episodes site/sitemap.xml
```

- [ ] **Step 3: Valider la syntaxe YAML**

Run: `python -c "import yaml; yaml.safe_load(open('.github/workflows/buzzer.yml', encoding='utf-8')); print('YAML OK')"`
Expected: `YAML OK`

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/buzzer.yml
git commit -m "ci(buzzer): générer + committer les pages par épisode chaque matin [skip ci]"
```

---

### Task 8: Déploiement + vérification live (critères d'acceptation)

**Files:** aucun (déploiement)

- [ ] **Step 1: Pousser (déclenche GitHub Pages)**

Run: `git push origin main`
Expected: push réussi. (Note : ce push N'A PAS `[skip ci]` au niveau du push lui-même → GitHub Pages republie.)

- [ ] **Step 2: Attendre le déploiement (~1-2 min) puis vérifier la page live**

Run: `curl -s -o /dev/null -w "%{http_code}\n" https://www.lebuzzer.com/episodes/2026-06-08/`
Expected: `200`

Run: `curl -s https://www.lebuzzer.com/episodes/2026-06-08/ | grep -oE 'lang="fr-CA"|PodcastEpisode|<h2>[^<]*'`
Expected: `lang="fr-CA"`, `PodcastEpisode`, et les titres de chapitres.

- [ ] **Step 3: Vérifier le sitemap live**

Run: `curl -s https://www.lebuzzer.com/sitemap.xml | grep -c "/episodes/"`
Expected: ≥ 7

- [ ] **Step 4: Validation schema**

Coller l'URL `https://www.lebuzzer.com/episodes/2026-06-08/` dans https://validator.schema.org et dans le Rich Results Test de Google.
Expected: `PodcastEpisode` + `BreadcrumbList` détectés, 0 erreur.

- [ ] **Step 5: Vérifier une page archivée (audio expiré)**

Run: `curl -s https://www.lebuzzer.com/episodes/<la-plus-vieille-date>/ | grep -i "archivé"`
Expected: présence de l'encart « archivé » et absence de `<audio`.

- [ ] **Step 6: Soumettre le sitemap (optionnel, manuel)**

Dans Google Search Console (si configurée pour lebuzzer.com), soumettre `https://www.lebuzzer.com/sitemap.xml`.

---

## Self-Review (rempli par l'auteur du plan)

- **Couverture spec** : parse/intro/chapitres/outro ✓ (T1) · audio_actif <7j ✓ (T2) · métadonnées feed ✓ (T3) · template léger + schema PodcastEpisode/BreadcrumbList + meta/canonical/OG ✓ (T4) · sitemap ✓ (T5) · build_all + backfill ✓ (T6) · intégration buzzer.yml ✓ (T7) · 7 critères d'acceptation ✓ (T6 step 5 + T8). 
- **Placeholders** : aucun — code complet à chaque étape.
- **Cohérence des types** : `parse_script`→dict{date,intro,chapters:[{titre,paragraphs}],outro} consommé tel quel par `render_episode_page` et `build_all` ; `episode_metadata`→dict{title,audio_url,duration_sec,audio_active} consommé par `render_episode_page`. Cohérent.
- **Risque connu** : la config GitHub Pages (`[skip ci]` / path `/site` vs `/`) est vérifiée explicitement en T7 step 1 et T8 step 2 avant de s'y fier.
