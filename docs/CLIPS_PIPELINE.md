# LE BUZZER — Pipeline clips courts auto

Le différenciateur stratégique vs Presto : à chaque épisode, extraire 2-3 moments forts → vidéos verticales 30-60s sous-titrées → push auto sur TikTok / Instagram Reels / YouTube Shorts.

**Pourquoi c'est critique** : Presto fait des threads X qui génèrent peu de découverte. Les shorts/reels sont LE canal #1 de découverte 2024-2026 pour des podcasts naissants. Sans ça, LE BUZZER aura le même problème de distribution que Presto.

## Architecture

```
[Script XML généré]
        │
        ▼
[1. LLM sélection moments forts]
   ↓ retourne 2-3 segments avec timestamps + hook text
        │
        ▼
[2. ffmpeg extract audio segments]
   ↓ output/clips/$DATE_clip_$N.mp3
        │
        ▼
[3. Whisper timing word-level]
   ↓ JSON avec timestamps par mot
        │
        ▼
[4. ffmpeg compose video]
   ↓ B-roll (Pexels API) + waveform + subtitles karaoke
   ↓ logo overlay + outro CTA "lebuzzer.com"
   ↓ output/clips/$DATE_clip_$N.mp4
        │
        ▼
[5. LLM génère caption + hashtags]
        │
        ▼
[6. Distribution]
   ├─ YouTube Shorts API (auto)
   ├─ Meta Graph API (Instagram Reels, auto)
   └─ TikTok : Postiz self-hosted OU upload manuel
```

## Spec détaillée

### Étape 1 : Sélection moments forts (LLM)

Nouveau fichier : `tools/clip_selector.py`

Prompt :

> Voici un script de podcast sport. Identifie les 2-3 moments les plus "punchy / partageables" pour un clip 30-60s vertical sur TikTok/Reels.
>
> Critères :
> - **Self-contained** : compréhensible isolé du reste de l'épisode
> - **WOW / drama / chiffre marquant** : la phrase qui fait "ah ouain?!"
> - **Durée audio 25-55s** quand lue à voix haute (~75-165 mots)
> - **Avec un hook fort dans les 5 premiers mots** (le crochet TikTok)
>
> Sortie JSON :
> ```json
> {
>   "clips": [
>     {
>       "rank": 1,
>       "hook_text": "Bédard a fait QUOI hier?!",
>       "segment_text": "[texte exact à lire, copie depuis le script]",
>       "estimated_duration_sec": 42,
>       "theme": "Hockey / NBA / Foot / F1 / MMA / Potin",
>       "social_caption": "Bédard, 22e but, 3 matchs d'affilée. Les Hawks reviennent sur Vegas. 🔥",
>       "hashtags": ["#hockey", "#bedard", "#nhl", "#blackhawks", "#lebuzzer"]
>     }
>   ]
> }
> ```

### Étape 2 : Extraction audio

Depuis le MP3 complet `output/audio/$DATE.mp3`, on a déjà les chapitres (CHAP frames ID3). Mais pour un segment ARBITRAIRE (pas forcément aligné sur un chapitre), on retrouve son timing :

1. Re-générer le TTS de juste le `segment_text` du clip (rapide, ~$0.01)
2. OU localiser le segment dans le MP3 maître via recherche de texte sur transcript Whisper + timestamps

Option 1 est plus simple et déterministe pour le MVP.

### Étape 3 : Whisper word-level timing

```python
from openai import OpenAI
client = OpenAI()
transcript = client.audio.transcriptions.create(
    file=open("clip.mp3", "rb"),
    model="whisper-1",
    response_format="verbose_json",
    timestamp_granularities=["word"],
)
# transcript.words = [{word: "Bédard", start: 0.0, end: 0.35}, ...]
```

Coût Whisper API : $0.006/min. Pour un clip 45s = $0.0045. Négligeable.

### Étape 4 : Composition vidéo

Nouveau fichier : `tools/generate_clip_video.py`

```bash
ffmpeg -i broll1.mp4 -i broll2.mp4 -i broll3.mp4 -i clip.mp3 \
  -filter_complex "[0:v]scale=1080:1920,setsar=1[v0]; \
                   [1:v]scale=1080:1920,setsar=1[v1]; \
                   [2:v]scale=1080:1920,setsar=1[v2]; \
                   [v0][v1][v2]concat=n=3:v=1:a=0[bg]; \
                   [bg]subtitles=clip.ass:force_style='...'[v]" \
  -map "[v]" -map 3:a -shortest -c:v libx264 -c:a aac \
  output/clips/$DATE_clip_$N.mp4
```

Sous-titres karaoke style TikTok via fichier `.ass` (Advanced SubStation Alpha) généré depuis les timings Whisper word-level. Le mot courant est mis en évidence en jaune `#FFD60A`.

Logo "LE BUZZER" en overlay top via `-vf "drawtext=text='LE BUZZER':..."`.

### Étape 5 : B-roll sourcing

[Pexels API](https://www.pexels.com/api/) — gratuit, sport footage de qualité.

```python
import requests
r = requests.get(
    "https://api.pexels.com/videos/search",
    headers={"Authorization": os.getenv("PEXELS_API_KEY")},
    params={"query": "hockey", "per_page": 5, "orientation": "portrait"},
)
videos = r.json()["videos"]
# télécharge le meilleur match
```

Mots-clés par `theme` :

| Theme | Mots-clés Pexels |
|---|---|
| Hockey | hockey, ice rink, NHL |
| Foot | soccer, football pitch, stadium |
| NBA / Basket | basketball, court, dunk |
| F1 | formula one, racing, grand prix |
| MMA | mma, octagon, boxing |
| Potin | crowd cheer, stadium silhouette (générique) |

### Étape 6 : Distribution auto

**YouTube Shorts** : extension du `tools/upload_youtube.py` existant. Flag : ajouter `#Shorts` dans description + format vertical détecté auto.

**Instagram Reels** : Meta Graph API. Pré-requis :
- Compte Instagram Business connecté à une Facebook Page
- Meta App créée avec permissions `instagram_basic`, `instagram_content_publish`
- Long-lived access token

```python
import requests
# Étape 1 : upload media
r = requests.post(
    f"https://graph.facebook.com/v18.0/{IG_USER_ID}/media",
    params={
        "media_type": "REELS",
        "video_url": "https://github.com/.../clip.mp4",
        "caption": caption,
        "access_token": META_TOKEN,
    }
)
creation_id = r.json()["id"]

# Étape 2 : publish
r = requests.post(
    f"https://graph.facebook.com/v18.0/{IG_USER_ID}/media_publish",
    params={"creation_id": creation_id, "access_token": META_TOKEN}
)
```

**TikTok** : pas d'API publique grand public stable. Options :
- **Postiz** (self-hosted, open-source) : https://github.com/gitroomhq/postiz-app — gère TikTok + LinkedIn + autres
- **Buffer** : SaaS, ~$15/mois
- **Manuel** : tu uploads les MP4 toi-même quotidiennement (10 min de travail, mais sape la promesse d'autonomie)

## Coût additionnel par épisode

| Item | Coût |
|---|---|
| LLM sélection moments | $0.01 |
| TTS re-gen segments (3 clips × 45s) | $0.03 |
| Whisper timing | $0.015 |
| Pexels API | $0 (free tier) |
| ffmpeg compute | $0 (GitHub Actions inclus) |
| **TOTAL** | **~$0.05 / épisode** |

## Effort d'implémentation

| Étape | Effort | Priorité |
|---|---|---|
| 1. clip_selector LLM | 2 h | P0 |
| 2. extract audio | 1 h | P0 |
| 3. Whisper timing | 1 h | P0 |
| 4. ffmpeg compose | 6-8 h (sous-titres karaoke = le plus dur) | P0 |
| 5. Pexels integration | 2 h | P0 |
| 6a. YouTube Shorts | 2 h (extension existant) | P0 |
| 6b. Instagram Reels | 4-6 h (setup Meta app long) | P1 |
| 6c. TikTok (Postiz) | 4 h (setup VPS) | P1 |
| **TOTAL MVP (P0)** | **~2 jours** | |
| **TOTAL complet (P0+P1)** | **~3-4 jours** | |

## Quand le construire

**Option A** : MVP LE BUZZER lancé d'abord avec juste audio (3-5 jours), CLIPS_PIPELINE en semaine 2.
**Option B** : Tout shipper en bundle (~1 semaine de build) avant lancement public.

Reco : **A** — lance vite, valide le contenu, puis ajoute clips dès la semaine 2. Si tu attends d'avoir tout, tu ne lances jamais.
