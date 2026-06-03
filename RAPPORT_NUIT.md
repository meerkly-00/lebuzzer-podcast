# RAPPORT DE NUIT — LE BUZZER

_Session agent autonome — 2-3 juin 2026._

---

## ✅ FAIT (code prêt sur le disque, dans `C:\Users\jchal\LeBuzzer`)

### Lecteur audio + abonnement (`site/index.html`)
- Mini-lecteur HTML5 **sticky** en bas de page (play/pause, barre de progression jaune `#FFD60A`
  sur fond noir, temps écoulé/total, seek). Accessible (aria-label, clavier, range).
- Charge **le dernier épisode automatiquement** : `fetch('/feed.xml')` → parse le 1er `<enclosure>` →
  source audio. **Fallback** `/audio/<date du jour>.mp3` si le flux échoue. Auto-à-jour chaque matin, sans rebuild.
- Tous les boutons **ÉCOUTER** (hero, masthead, barre sticky) lancent la lecture.
- Section abonnement : **Spotify / Apple / YouTube = « Bientôt disponible »** (placeholders propres, aucun lien mort)
  + tuile **Flux RSS copiable** (bouton → copie `https://www.lebuzzer.com/feed.xml` + toast).

### Finitions site
- **Favicons + PWA** depuis la vraie icône buzzer : `favicon.ico` (16/32/48), `favicon-32`, `favicon-16`,
  `apple-touch-icon` (180), `icon-192`, `icon-512` + `site/site.webmanifest`. Servis par les routes Worker existantes.
- **SEO complet** : `<title>` + meta description, **Open Graph** + **Twitter Card** (`og:image=…/artwork.jpg`),
  **JSON-LD PodcastSeries** (`webFeed=/feed.xml`), `canonical`, `lang="fr-CA"`, `theme-color`,
  **preload** des 3 polices latines, `site/sitemap.xml`, `site/robots.txt`.
- **Icônes sociales** Instagram + TikTok dans le footer, liées aux vrais profils. **X/Twitter retiré** partout.
- **Page 404 brandée** (`site/404.html`) + route Worker mise à jour pour la servir (statut 404).
- **Infolettre** : prête pour **Beehiiv** (mettre l'URL d'embed dans `LB.beehiivEmbedUrl` en haut du `<script>`).
  Tant que vide → **fallback courriel fonctionnel** (le formulaire ouvre un courriel pré-rempli vers
  `lebuzzerpod@gmail.com`, donc les abonnés sont collectés dès maintenant).
- Responsive conservé (design approuvé intact), `prefers-reduced-motion` respecté.

### Icône de marque (corrigée)
- Nouvelle icône officielle **« Z + lampe de but »** (Z crème, dôme rouge, rayons jaunes sur noir),
  rendue avec la vraie police **Anton** depuis le dossier de marque → `artwork/brand-icon-buzzer.png`.
  (L'ancienne icône « LB » a été remplacée partout : favicons + photo de profil.)

### Pipeline clips vidéo (`tools/`)
- `tools/clip_selector.py` — LLM **Anthropic** choisit 2-3 moments punchy (hook, segment, caption, hashtags) → JSON.
- `tools/generate_clip_video.py` — **TTS OpenAI voix `ash`** → **Whisper word-level** → **sous-titres karaoke .ass**
  (mot courant en jaune) → **ffmpeg vertical 1080×1920** : fond marque `#0D0D0D` + **waveform jaune animée**
  + **logo « LE BUZZER » (Anton)** + bandeau thème + **outro CTA `lebuzzer.com`**. Cache TTS/Whisper pour re-rendus rapides.
  Police Anton/Oswald embarquées dans `tools/assets/` (portable CI). B-roll Pexels = sauté (pas de clé) — fond+waveform suffit.
- **2 clips générés et vérifiés visuellement** depuis l'épisode du 2 juin :
  - `output/clips/2026-06-02_clip_1.mp4` (~40 s) — bombe de Patrik Laine
  - `output/clips/2026-06-02_clip_2.mp4` (~52 s) — chaos NFL (Garrett/Brown)

### Kit réseaux
- `docs/SOCIAL_KIT.md` : photo de profil, bios (IG 94/150, TikTok 60/80), lien, captions des 2 clips + post de lancement.

---

## 🔴 LIVE & VÉRIFIÉ

- `https://www.lebuzzer.com` et `/feed.xml` : **toujours fonctionnels** (prod intacte, non cassée).
- Le flux RSS pointe bien vers le MP3 du jour (HTTP 200 vérifié) → le lecteur jouera ce fichier.
- **⚠️ Les nouveautés du site ne sont PAS encore en ligne** : il faut **push** (le Worker sert le site depuis
  `raw.githubusercontent.com/.../main`) **+ déployer le Worker** pour la route 404. Voir « Reste au proprio ».
- Clips & icônes : **fichiers vérifiés sur le disque** (rendus + frames inspectés), pas encore publiés (voir ci-dessous).
- Aucun commit/push fait par l'agent : pas d'identifiants Git/Cloudflare dans le bac à sable + verrou `.git/index.lock`.

---

## 🟡 RESTE AU PROPRIO (court et actionnable)

### 1. Publier le site (2 commandes, depuis Windows)
```bash
cd C:\Users\jchal\LeBuzzer
git add site/ worker/ artwork/brand-icon-buzzer.png docs/SOCIAL_KIT.md RAPPORT_NUIT.md .gitignore
git commit -m "feat: lecteur audio + abonnement, favicons/SEO/404, icône buzzer, pipeline clips"
git push                       # → met le SITE en ligne (index, favicons, SEO, 404, manifest)
cd worker && npx wrangler deploy   # → active la route 404 brandée + content-type .ico
```
Puis re-tester : `https://www.lebuzzer.com` (le bouton ÉCOUTER doit jouer le son), `/feed.xml`, `/audio/<date>.mp3`,
`/favicon.ico`, `/site.webmanifest`, `/sitemap.xml`, `/robots.txt`, une URL bidon (→ 404 brandée).
_(NB : le repo a déjà plein d'autres fichiers modifiés d'une session précédente — à revoir/committer séparément.)_

### 2. Connexion réseaux (l'agent ne peut pas se connecter à un compte)
Dans Chrome, les comptes connectés sont `djee.whiz`/`benito.3d` (IG) — **pas** `le_buzzer_qc` ; TikTok est déconnecté.
→ **Connecte-toi à `@le_buzzer_qc` (IG) et `@le_buzzerqc` (TikTok)** puis relance l'agent
(« comptes LE BUZZER connectés, configure profils + publie clip 1 »). Sinon, fais-le à la main avec `docs/SOCIAL_KIT.md` (~5 min).
Photo de profil prête : `site/assets/profile-1024.png`. Clips prêts dans `output/clips/`.

### 3. Infolettre Beehiiv (gratuit)
Crée la publication Beehiiv (`lebuzzerpod@gmail.com`), récupère l'URL d'embed du formulaire,
colle-la dans `LB.beehiivEmbedUrl` (haut du `<script>` de `site/index.html`), push. (Sinon le fallback courriel marche déjà.)

### 4. Soumissions podcast
Soumettre le flux `https://www.lebuzzer.com/feed.xml` à **Spotify for Podcasters** et **Apple Podcasts Connect**.
Quand les liens existent, remplacer les tuiles « Bientôt disponible » par les vrais liens dans `site/index.html`.

### 5. Activer les clips en auto (NON activé — validation humaine requise)
Le pipeline est prêt. Pour l'automatiser dans `.github/workflows/buzzer.yml`, ajouter **après** l'étape
« Publier le MP3 » (qui fait déjà `gh release upload "$DATE" …`) :
```yaml
      - name: Générer + publier les clips
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          python tools/clip_selector.py "$DATE" --n 2
          python tools/generate_clip_video.py "$DATE" 1
          python tools/generate_clip_video.py "$DATE" 2
          gh release upload "$DATE" output/clips/${DATE}_clip_1.mp4 output/clips/${DATE}_clip_2.mp4 --clobber
```
Les clips deviennent alors servis via `https://www.lebuzzer.com/clips/<date>_1.mp4` (route Worker déjà en place).
La **publication auto** TikTok/IG reste manuelle (pas d'API/connecteur dispo) — ou via Meta Graph API / Postiz (voir `docs/CLIPS_PIPELINE.md`).

---

## ⚠️ Petits caveats
- Sous-titres clips = transcription **Whisper** : 1-2 mots parfois mal transcrits (ex. « bombe » → « bonde »).
  Audio correct. Amélioration future : alignement forcé sur le texte source connu.
- `output/clips/` est gitignoré (les clips se publient en *release assets*, pas dans le repo) — normal.
- Fichier temporaire `.sync_probe` à la racine (ajouté à `.gitignore`) : supprimable.
