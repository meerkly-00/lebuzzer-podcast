# LE BUZZER — Branding visuel

## Identité de marque

**Nom** : LE BUZZER
**Tagline** : *Le podcast sport quotidien. Cinq minutes, tout le drame.*
**Ton** : Punchy, sport-anchor, attitude. Pas corporate.

## Palette de couleurs

Reco basée sur les codes du sport broadcast moderne + différenciation visuelle vs PRESTO :

| Rôle | Couleur | Hex |
|---|---|---|
| Primaire | Rouge écarlate (urgence buzzer, alarme finale) | `#E63946` |
| Secondaire | Noir profond (broadcast, autorité) | `#0D0D0D` |
| Accent 1 | Jaune buzzer (sirène, signal) | `#FFD60A` |
| Texte clair | Off-white | `#F1FAEE` |
| Texte foncé | Gris graphite | `#1A1A1A` |

Pourquoi rouge + noir + jaune : les codes universels du "signal de fin de match" (buzzer, sirène, drapeau jaune F1). Différencié visuellement de PRESTO (qui est plus probablement bleu/blanc/typographie sobre).

## Typographie

- **Wordmark / logo** : *Anton* (Google Fonts, free) ou *Bebas Neue* — sans-serif compressé, hauteur maximale, "broadcast headline" vibe
- **Titres** : *Inter Tight Bold* ou *Archivo Black*
- **Corps** : *Inter* (système, lisible)

## Assets à produire

### 1. Cover artwork (Spotify/Apple) — 3000×3000 px

Spec :
- Fond noir profond `#0D0D0D`
- Wordmark "LE BUZZER" en rouge `#E63946`, Anton Bold, centré, énorme
- Petit accent jaune `#FFD60A` : ligne horizontale fine sous le wordmark OU petit icône buzzer/sirène stylisée en haut à gauche
- Pas de visage humain, pas de stock photo joueur (problème de droits image)
- Lisible en thumbnail 64×64 (test : si tu vois "LE BUZZER" à 64px, c'est bon)

Outils : Figma (gratuit), Canva, ou pipeline `tools/gen_artwork.py` adapté.

### 2. Brand icon — 1024×1024 px transparent PNG

Petit logo symbole pour favicon, X profile, etc. :
- Soit un icône de buzzer/sirène stylisé minimal
- Soit les initiales "LB" en wordmark Anton sur fond rouge en cercle

### 3. YouTube background — 1280×720 px (16:9)

Pour les épisodes vidéo YouTube :
- Fond noir avec léger gradient vers gris très foncé
- Wordmark "LE BUZZER" en haut à gauche, plus petit
- Espace central libre pour la waveform audio animée (générée par le pipeline)
- Bandeau bas avec date du jour + numéro d'épisode

### 4. Intro sting sonore (0.5-1 sec)

Court signal d'identité audio :
- Option A : buzzer électrique court (1 beep grave + 1 beep aigu)
- Option B : "swoosh + impact" cinématique (style intro sport TV)
- Option C : sirène marine très courte (~0.5s)

Sources gratuites : Pixabay Sound Effects, Freesound.org, ou générer via ElevenLabs SFX ($).

### 5. Templates clips vertical (1080×1920)

Pour les clips TikTok/Reels/Shorts (pipeline à venir) :
- Bandeau supérieur fixe : logo "LE BUZZER" rouge, hauteur ~80px
- Zone centrale : B-roll vidéo (Pexels) ou waveform animée
- Bandeau bas : sous-titres dynamiques karaoke (mot allumé en jaune)
- Bandeau bas inférieur : "lebuzzer.com" + handle social

## Workflow de production

1. **Génération avec IA** : Adapter `tools/gen_artwork.py` pour générer artwork via DALL-E ou Flux. Prompt suggéré :

   > *"Bold sport podcast cover art, 'LE BUZZER' in massive red Anton bold typography centered on deep black background, small bright yellow accent line, minimalist, broadcast TV vibe, no people, no photo, vector style, 1:1 square format, high contrast, readable at thumbnail size."*

2. **Validation manuelle** : tu approuves visuellement avant de pusher

3. **Upload** : artwork dans le repo + URL via `PODCAST_ARTWORK_URL` env var

## Inspirations à étudier

- **Pat McAfee Show** — typographie agressive, jaune/noir
- **Spittin' Chiclets** — punchy hockey vibe
- **Hugo Décrypte** — typographie minimaliste mais reconnaissable
- **The Athletic / The Ringer** — esthétique broadcast moderne
