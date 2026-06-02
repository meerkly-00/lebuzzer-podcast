# Architecture Media Factory (solution C)

Décision : **chaque média a son propre repo léger qui dépend d'un package partagé** `media-factory-engine`. Repos séparés = flippables/tuables indépendamment. Engine partagé = zero duplication de code, les bugfixes profitent à tous.

## Vue d'ensemble

```
                ┌──────────────────────────────┐
                │  media-factory-engine        │
                │  (repo privé, GitHub)        │
                │                              │
                │  - aggregate.py              │
                │  - generate.py               │
                │  - tts.py                    │
                │  - feed.py                   │
                │  - pipeline.py               │
                │  - tools/ (clips, YT, X)     │
                │                              │
                │  installable via pip         │
                └────────────┬─────────────────┘
                             │
            ┌────────────────┴────────────────┐
            │                                 │
            ▼                                 ▼
┌──────────────────────┐         ┌──────────────────────┐
│  Presto_Podcast      │         │  lebuzzer-podcast    │
│  (repo client léger) │         │  (repo client léger) │
│                      │         │                      │
│  config/sources.yaml │         │  config/sources_     │
│  prompts/system_     │         │    buzzer.yaml       │
│    presto_v1.md      │         │  prompts/system_     │
│  .env                │         │    buzzer_v1.md      │
│  .github/workflows/  │         │  .env                │
│  artwork/            │         │  .github/workflows/  │
│  run.py (1 ligne)    │         │  artwork/            │
│  requirements.txt    │         │  run.py (1 ligne)    │
│   └─ engine via pip  │         │  requirements.txt    │
└──────────────────────┘         │   └─ engine via pip  │
                                 └──────────────────────┘
```

## Repos à créer/refactorer

### 1. `media-factory-engine` (NOUVEAU)

Repo privé. Package Python pip-installable.

Structure :

```
media-factory-engine/
├── media_factory/
│   ├── __init__.py
│   ├── aggregate.py       # ex src/aggregate.py de Presto
│   ├── generate.py        # ex src/generate.py de Presto
│   ├── tts.py             # ex src/tts.py de Presto
│   ├── feed.py            # ex src/feed.py de Presto
│   ├── pipeline.py        # ex src/pipeline.py de Presto
│   └── tools/             # scripts partagés
│       ├── youtube_upload.py
│       ├── tweet.py
│       └── clip_generator.py  # (à venir : pipeline clips)
├── tests/
├── requirements.txt
├── pyproject.toml         # package metadata
└── README.md
```

Installable via :

```
pip install git+https://github.com/meerkly-00/media-factory-engine.git@main
```

### 2. `Presto_Podcast` (REFACTOR)

Le repo existant : on **supprime** `src/`, `tools/` (sauf ce qui est Presto-spécifique). On **garde** : `config/sources.yaml`, `prompts/system_presto_v1.md`, `.env`, `.github/workflows/`, branding, `run.py`, `feed.xml`, `data/`, `output/`.

`run.py` devient :

```python
from media_factory.pipeline import run_from_cli
if __name__ == "__main__":
    run_from_cli()
```

`requirements.txt` devient :

```
git+https://github.com/meerkly-00/media-factory-engine.git@main
python-dotenv>=1.0
```

### 3. `lebuzzer-podcast` (NOUVEAU, thin)

Structure :

```
lebuzzer-podcast/
├── config/
│   └── sources_buzzer.yaml
├── prompts/
│   └── system_buzzer_v1.md
├── artwork/
│   ├── cover.jpg
│   ├── brand-icon.png
│   └── youtube-bg.jpg
├── output/                 # gitignored sauf scripts/
├── data/
├── .github/workflows/
│   └── buzzer.yml
├── .env.example
├── run.py
├── requirements.txt
├── feed.xml
└── README.md
```

Zéro fichier de code core. Juste config + prompts + branding + workflow.

## Étapes du refactor

### Phase 1 — Extraction engine (4-6h)

1. Créer le repo `media-factory-engine` sur GitHub (privé)
2. Copier `Presto_Podcast/src/*` → `media-factory-engine/media_factory/*`
3. Copier les tools partageables (`upload_youtube.py`, `tweet.py`, `gen_artwork.py`) → `media-factory-engine/media_factory/tools/`
4. Adapter les imports (`from .aggregate import` reste valide)
5. Créer `pyproject.toml` avec `[project] name = "media-factory"`
6. Ajouter une fonction `run_from_cli()` dans `pipeline.py` qui fait l'argparse actuel de `run.py`
7. Push + tag `v0.1.0`
8. Test : `pip install git+...` dans un venv frais et `python -c "from media_factory.pipeline import run"`

### Phase 2 — Refactor Presto (2-3h)

1. Dans le repo Presto : `git rm -r src/ tools/` (sauf ce qui est Presto-only)
2. Mettre à jour `requirements.txt` (engine git)
3. Réduire `run.py` à la version 2-lignes
4. Test local : `python run.py --dry-run`, puis `python run.py --no-tts`, puis full
5. Test GitHub Actions : trigger manuel via `workflow_dispatch`
6. Commit + push

### Phase 3 — Build LE BUZZER (2h)

1. Créer repo `lebuzzer-podcast` (vide sur GitHub)
2. Init local avec la structure thin ci-dessus
3. Copier les configs/prompts/.env.example/workflow déjà préparés
4. requirements.txt + run.py ultra-minces
5. Push
6. Setup secrets GitHub Actions (mêmes clés que Presto)
7. Test workflow_dispatch manuel
8. Buy lebuzzer.com, setup DNS Cloudflare, déployer site statique

### Phase 4 — Brand + soumission plateformes (4-6h, parallel)

- Génération artwork via prompt DALL-E ou Flux (voir `BRANDING.md`)
- Soumission Spotify + Apple (24-72h de validation)
- Setup YouTube channel + premier upload test

### Phase 5 — Pipeline clips (post-MVP)

Voir `CLIPS_PIPELINE.md`. Construit DANS l'engine pour que Presto en bénéficie aussi (clips de Presto sur Politique/Éco/Tech = potentiel viral aussi).

## Effort total estimé

| Phase | Effort |
|---|---|
| 1 (engine) | 4-6h |
| 2 (Presto refactor) | 2-3h |
| 3 (lebuzzer build) | 2h |
| 4 (brand + soumission) | 4-6h (parallèle) |
| **TOTAL MVP** | **12-17h** (~2 jours focused) |
| 5 (clips, post-MVP) | 2-3 jours additionnels |

## Comparatif avec solution A (fork-clone, code dupliqué)

| | Solution A (fork-clone) | Solution C (engine partagé) |
|---|---|---|
| Effort MVP | 4-8h | 12-17h |
| Maintenance long terme | 2× chaque fix | 1× chaque fix |
| Risque code drift | Élevé | Nul |
| Flippable séparément | Oui | Oui (voir ci-dessous) |
| Killable séparément | Oui | Oui |
| Onboard média #3 | 4-8h | 2h |

## Flippabilité avec engine partagé

Question légitime : si je vends `lebuzzer-podcast` qui dépend d'un engine privé que je garde, l'acheteur peut-il faire tourner le repo ?

**Options à la vente** :

1. **Vendor-in à la vente** : au moment du flip, on fait `pip download media-factory-engine`, on copie le code dans le repo lebuzzer, et l'acheteur reçoit un repo 100% self-contained. C'est une opération de 1h.
2. **Licensing perpetual** : on donne à l'acheteur un accès au repo engine (read-only + maj). Plus simple si on vend à plusieurs.
3. **Open-source l'engine** : on rend `media-factory-engine` public MIT/Apache. Tout le monde peut l'utiliser, on vend juste le repo média + l'audience + le domaine + les secrets.

Option 1 = par défaut, c'est ce qu'on fera pour le premier flip.
Option 3 = stratégiquement intéressant (positionne Anthropic comme "celui qui a ouvert le code", génère de la goodwill + peut attirer des sponsors). À considérer plus tard.

## Killabilité avec engine partagé

Tuer LE BUZZER sans toucher Presto :

1. Archive le repo `lebuzzer-podcast` sur GitHub (1 clic)
2. Stop le workflow (auto, le repo archivé n'exécute plus de cron)
3. Désactive le DNS du domaine, laisse-le expirer
4. Done. Presto continue de tourner normalement, l'engine est inchangé.
