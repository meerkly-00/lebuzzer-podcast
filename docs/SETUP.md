# LE BUZZER — Setup

Repo client léger basé sur l'engine partagé `media-factory-engine`. Tout le code core (agrégation, génération script, TTS, RSS) vit dans l'engine ; ce repo ne contient que la configuration et le branding spécifiques à LE BUZZER.

## Pré-requis

- Engine `media-factory-engine` pushé sur GitHub (privé OK) à `meerkly-00/media-factory-engine`
- Python 3.10+
- ffmpeg dans le PATH (pour TTS et audio mastering)

## 1. Créer le repo GitHub

Sur GitHub : nouveau repo `meerkly-00/lebuzzer-podcast`. Ne pas initialiser avec README (on push depuis local).

## 2. Setup local

```bash
# Cloner le dossier produit par cette session (déplace-le hors du scratchpad d'abord)
cp -r ~/lebuzzer-podcast-starter ~/dev/lebuzzer-podcast
cd ~/dev/lebuzzer-podcast

# Init git et push
git init
git add -A
git commit -m "Initial commit — LE BUZZER thin client over media-factory engine"
git remote add origin https://github.com/meerkly-00/lebuzzer-podcast.git
git push -u origin main

# Setup venv et install
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Config locale
cp .env.example .env
# Édite .env avec tes vraies clés
```

## 3. Test local

```bash
# Dry-run : agrégation seulement, pas de LLM ni TTS (gratuit)
python run.py --dry-run --fenetre 24

# Avec script LLM mais sans TTS (test du prompt)
python run.py --no-tts

# Pipeline complet local
python run.py

# Servir le feed RSS local pour tester
python run.py --serve
# Ouvre http://localhost:8000/feed.xml
```

## 4. Secrets GitHub Actions

Dans `lebuzzer-podcast` → Settings → Secrets and variables → Actions :

- `ANTHROPIC_API_KEY` (peut être la même que Presto)
- `OPENAI_API_KEY` (peut être la même que Presto)

Si l'engine est dans un **repo privé** : il faut aussi configurer un PAT pour que GitHub Actions puisse `pip install git+https://...` :

- Créer un PAT GitHub avec scope `repo` (read-only suffit)
- Ajouter le secret `ENGINE_INSTALL_TOKEN`
- Modifier `requirements.txt` pour utiliser :
  ```
  media-factory @ git+https://x-access-token:${ENGINE_INSTALL_TOKEN}@github.com/meerkly-00/media-factory-engine.git@main
  ```
- (Alternative) Utiliser une `deploy key` SSH dans Actions

## 5. Domaine et site

```
1. Acheter lebuzzer.com (~$15.50/an sur Namecheap/Cloudflare Registrar)
2. Cloudflare :
   - Add site lebuzzer.com → DNS chez Cloudflare
   - Pages : créer un projet pointant sur ce repo, build command `# none`, publish dir = `/`
   - Workers (optionnel) : déployer worker/audio-proxy.js pour servir l'audio depuis GitHub Releases
3. DNS : configuré automatiquement par Cloudflare Pages
```

Note : le `worker/` n'est pas inclus dans le starter — copie-le depuis Presto si tu veux la même infra audio-proxy. Sinon, ajouter `PODCAST_BASE_URL=https://lebuzzer-podcast.pages.dev` (URL Cloudflare Pages par défaut) suffit pour démarrer.

## 6. Brander

Voir `docs/BRANDING.md` pour les specs cover/icon/YouTube background/intro sting.

Mets les assets finalisés dans :

```
artwork/
├── cover.jpg          (3000×3000, soumission Spotify/Apple)
├── brand-icon.png     (1024×1024 transparent)
├── youtube-bg.jpg     (1280×720)
└── intro-sting.mp3    (0.5-1s)
```

Et expose-les via `PODCAST_ARTWORK_URL` dans .env / workflow.

## 7. Soumettre aux plateformes

Une fois le feed validé localement et déployé :

- **Spotify for Podcasters** : https://podcasters.spotify.com → soumettre `https://lebuzzer.com/feed.xml`
- **Apple Podcasts Connect** : https://podcastsconnect.apple.com → idem
- **YouTube** : créer chaîne LE BUZZER, configurer le workflow `youtube.yml` (à porter depuis Presto)

Validation : 24-72h en moyenne.

## 8. Activer le cron

Le workflow `.github/workflows/buzzer.yml` est en cron 7h EDT par défaut. Première vérification : déclenche-le manuellement via `workflow_dispatch` (bouton "Run workflow" dans l'onglet Actions du repo).

Si tu veux un déclenchement plus fiable que le cron natif GitHub : configure un `cron-job.org` ou un Cloudflare Cron Trigger qui hit l'API GitHub `workflow_dispatch`.

## 9. Premier épisode live

Après avoir validé une exécution locale et un dispatch manuel réussi du workflow :

1. Vérifie que `feed.xml` est commité et accessible publiquement
2. Vérifie que le MP3 est dans GitHub Releases
3. Soumets aux plateformes
4. Active le cron auto

## Architecture en bref

```
lebuzzer-podcast/  (CE REPO — léger)
├── config/sources_buzzer.yaml
├── prompts/system_buzzer_v1.md
├── artwork/
├── .env
├── feed.xml
├── run.py            (2 lignes : délègue à l'engine)
└── requirements.txt  (1 ligne : tire l'engine via pip git+)
        │
        ▼
media-factory-engine (REPO SÉPARÉ — code core partagé avec Presto)
└── media_factory/
    ├── aggregate.py
    ├── generate.py
    ├── tts.py
    ├── feed.py
    ├── pipeline.py
    └── cli.py
```

Voir `docs/ARCHITECTURE.md` pour le détail.

## Mise à jour de l'engine

Quand l'engine est mis à jour :

```bash
pip install --upgrade --force-reinstall git+https://github.com/meerkly-00/media-factory-engine.git@main
```

En CI/CD GitHub Actions, c'est automatique à chaque run (le `pip install -r requirements.txt` tire le dernier `main`).

Pour pinner une version stable, modifier `requirements.txt` :

```
media-factory @ git+https://github.com/meerkly-00/media-factory-engine.git@v0.1.0
```

## Roadmap

- **Maintenant** : MVP audio (5 min daily, voix `onyx`, sources sport + potins indirects)
- **Semaine 2** : pipeline clips courts TikTok/Reels/Shorts (voir `docs/CLIPS_PIPELINE.md`) — à construire DANS l'engine pour bénéficier aussi à Presto
- **Semaine 3-4** : iteration sur le prompt en fonction des écoutes + ajout sources si gaps détectés
- **Mois 2** : potentielle voix B pour cameos (rester sur OpenAI TTS, pas ElevenLabs tant que pas rentable)
- **Mois 3+** : si LE BUZZER traction validée → média #3 (newsletter écrite ou autre verticale)
