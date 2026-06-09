import re
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
