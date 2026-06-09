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
