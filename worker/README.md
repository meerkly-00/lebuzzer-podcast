# LE BUZZER - Cloudflare Worker

Worker qui sert les MP3, le flux RSS et une landing page via `lebuzzer.com`.

## Routes

- `https://lebuzzer.com/` -> landing page minimaliste
- `https://lebuzzer.com/feed.xml` -> flux RSS depuis le repo GitHub
- `https://lebuzzer.com/audio/YYYY-MM-DD.mp3` -> MP3 depuis GitHub Release
- `https://lebuzzer.com/clips/YYYY-MM-DD_N.mp4` -> clip vidéo (quand pipeline clips actif)
- `https://lebuzzer.com/artwork.jpg|png` -> cover

## Déployer

```bash
cd worker/
npm install -g wrangler   # si pas déjà installé
wrangler login
wrangler deploy
```

Puis dans Cloudflare Dashboard :
1. `Workers & Pages` → `lebuzzer-audio-proxy` → **Settings → Triggers**
2. Vérifie que les routes du `wrangler.toml` sont actives (devrait être auto)

## Test après déploiement

```bash
curl -IL https://lebuzzer.com/
# Doit retourner 200 text/html

curl -IL https://lebuzzer.com/feed.xml
# 200 application/rss+xml

curl -IL https://lebuzzer.com/audio/2026-06-02.mp3
# 200 audio/mpeg (après le premier épisode publié)
```

## Activer le cron Twitter plus tard (optionnel)

Quand tu veux ajouter une distribution Twitter automatique :

1. Décommente les `[triggers]` dans `wrangler.toml`
2. Configure les secrets :
   ```bash
   wrangler secret put TWITTER_API_KEY
   wrangler secret put TWITTER_API_SECRET
   wrangler secret put TWITTER_ACCESS_TOKEN
   wrangler secret put TWITTER_ACCESS_TOKEN_SECRET
   ```
3. Le pipeline doit générer `data/tweets/YYYY-MM-DD.json` quotidiennement (copier `tools/post_tweets.py` de Presto + adapter)
4. Re-déployer : `wrangler deploy`

## Si tu renommes le repo GitHub

Change la constante `REPO` dans `audio-proxy.js` et redéploie.
