# LE BUZZER - Test local du premier épisode

Le sandbox de cette session a un timeout de 45s par appel qui m'empêche de générer un épisode complet (le pipeline Claude + TTS prend 1-2 minutes). Sur ta machine, **pas de timeout**, donc tu peux le faire.

## Pré-requis machine locale

- Python 3.10+
- ffmpeg dans le PATH
- Clés API Anthropic + OpenAI dans `.env`

## Étapes

### 1. Setup local (5 min)

```bash
# Copie le starter du scratchpad vers ton dossier dev
cp -r ~/Podcast/../lebuzzer-podcast ~/dev/lebuzzer-podcast
# Ou utilise les fichiers du dossier outputs/lebuzzer-podcast/ de cette session

cd ~/dev/lebuzzer-podcast

# Venv
python3 -m venv .venv
source .venv/bin/activate

# IMPORTANT : pour l'instant l'engine n'est pas encore sur GitHub.
# Installe-le en mode editable depuis le scratchpad :
pip install -e ../media-factory-engine
# (ajuste le chemin selon où tu as copié le dossier)

# Quand tu auras pushé l'engine sur GitHub, tu remplaces par :
# pip install -r requirements.txt

# Config
cp .env.example .env
# Édite .env avec tes clés Anthropic et OpenAI (mêmes que Presto)
```

### 2. Dry-run (gratuit, 30s)

```bash
python run.py --dry-run --fenetre 24
```

Tu devrais voir ~80-110 articles agrégés depuis les sources sport + analyse + trade rumors. Pas de coût.

### 3. Script-only (sans TTS, ~$0.02, 15-30s)

```bash
python run.py --no-tts --no-feed
```

Génère le script XML dans `output/scripts/YYYY-MM-DD.xml`. Lis-le pour valider :

- L'intro démarre in medias res (pas "bonjour bienvenue").
- Top international a 3-4 stories avec attribution.
- Le moment QC mentionne Canadiens / CFM / joueurs QC.
- "L'angle du jour" : présent SEULEMENT si un angle solide existe dans les sources. Si tu vois une section vide ou vague, c'est un bug à signaler.
- Pas de tirets longs.
- Pas de formulations clickbait.

### 4. Épisode complet (script + audio MP3, ~$0.07, 1-2 min)

```bash
python run.py --no-feed
```

Écoute le MP3 généré dans `output/audio/YYYY-MM-DD.mp3`. Validations :

- Voix onyx tient bien pour 4-6 minutes ?
- Le rythme est punchy ou plat ?
- Les acronymes (NHL, NBA, F1) sont bien prononcés ?
- Les noms de joueurs francophones / anglophones passent ?
- L'intro accroche ?

### 5. Itération sur le prompt

Si l'épisode te déçoit, ouvre `prompts/system_buzzer_v1.md` et ajuste :

- **Trop neutre / pas assez de personnalité** → renforce la section "Attitude et prises de position autorisées" + ajoute plus d'exemples de prises de position acceptables.
- **Trop clickbait / forcé** → renforce la liste "NON" + section anti-référence Facebook.
- **Section "Angle du jour" toujours vide** → soit les sources ne te donnent pas assez d'angles (ajoute plus de sources analyse-sport), soit tu peux assouplir un critère de la Règle 7.
- **Trop court / trop long** → ajuste les targets de mots par section.
- **Voix trop lente / rapide** → ajuste `_speed` dans `media_factory/tts.py` (pas exposé en env pour l'instant), ou switch en `ash` pour un autre rendu.

### 6. Tester avec une AUTRE date

```bash
python run.py --no-feed --date 2026-05-30 --fenetre 48
```

Permet de tester avec une autre fenêtre temporelle si tu trouves qu'il y a pas assez d'actu sport aujourd'hui.

## Coûts par itération de test

| Action | Coût approx |
|---|---|
| dry-run | 0 $ |
| script-only | 0.02 $ |
| Pipeline complet 5 min | 0.07 $ |
| 20 itérations de prompt | 1.50 $ |

## Quand tu es satisfait du prompt et de la voix

→ Push sur GitHub
→ Lance le workflow GitHub Actions
→ Soumets le feed RSS à Spotify et Apple Podcasts

## Si l'épisode est BON mais quelque chose te dérange

Note ce que tu veux changer, partage-le dans la prochaine session, on itère sur le prompt v1.2. C'est itératif - les 5 premiers épisodes serviront à caler le ton.
