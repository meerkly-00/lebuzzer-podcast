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
