# LE BUZZER

Podcast sport quotidien francophone québécois, généré automatiquement. Résultats, histoires et potins de la LNH, NBA, foot, F1 et MMA en 5 minutes.

## Stack

- **Agrégation** : RSS sport (La Presse, RDS, TVA Sports, L'Équipe, RMC, ESPN) + Reddit (r/hockey, r/Habs, r/nba, r/soccer, r/formula1, r/mma) + agrégateurs rumeurs Google News
- **Génération script** : Claude (anthropic API)
- **TTS** : OpenAI TTS (voix `onyx`, fallback edge-tts gratuit)
- **Distribution** : GitHub Releases (MP3) + Cloudflare Pages (RSS + site) + Spotify/Apple/YouTube
- **Hébergement** : GitHub Actions (cron quotidien) + Cloudflare Pages/Workers
- **Coût** : ~$0.20-1 par épisode

## Lancement rapide

```bash
git clone https://github.com/meerkly-00/lebuzzer-podcast.git
cd lebuzzer-podcast
pip install -r requirements.txt
cp .env.example .env  # édite .env avec tes clés
python run.py --dry-run  # test agrégation
python run.py            # épisode complet
```

Voir `docs/SETUP.md` pour le setup complet.

## Structure

```
lebuzzer-podcast/
├── config/
│   └── sources_buzzer.yaml      # RSS feeds sport + potins
├── prompts/
│   └── system_buzzer_v1.md      # prompt LLM avec persona et règles éditoriales
├── src/                          # pipeline core (hérité de Presto)
│   ├── aggregate.py
│   ├── generate.py
│   ├── tts.py
│   ├── feed.py
│   └── pipeline.py
├── tools/                        # scripts auxiliaires (tweet, YouTube, artwork)
├── worker/                       # Cloudflare Worker pour proxy audio
├── .github/workflows/
│   └── buzzer.yml                # cron quotidien GitHub Actions
└── run.py                        # entrée CLI
```

## Famille de podcasts

LE BUZZER fait partie d'une famille de podcasts auto-générés construite sur la même base technique :

- **PRESTO** — actualité matinale francophone québécois ([prestopodcast.online](https://prestopodcast.online))
- **LE BUZZER** — sport quotidien ([lebuzzer.com](https://lebuzzer.com))

## Licence

Tous droits réservés.
