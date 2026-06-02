# Brief pour Claude Design

À coller dans le champ "Company name and blurb" de Claude Design (claude.ai/design).

---

## Nom + blurb

**LE BUZZER — le podcast sport quotidien francophone québécois.** 5 minutes chaque matin pour tout savoir sur la LNH, NBA, foot européen, F1 et MMA, avec attitude. Couvre les Canadiens et CF Montréal, mais aussi les joueurs québécois à l'étranger (Bédard, Suzuki, etc.) et les grandes histoires internationales. Lu par voix synthétique — mais le contenu et le ton sont éditoriaux, pas robotiques. Pas un site à potins, pas une revue de presse plate : un podcast avec une voix, des prises de position fondées sur les faits, et une connaissance réelle du sport.

## Audience cible

Amateur de sport francophone, 20-45 ans, Québec d'abord puis France/Belgique/Maghreb. Écoute pendant son commute du matin ou au gym. Connaît les bases du sport — pas besoin de lui expliquer ce qu'est un power play. Vient pour : le rythme, des prises de position intelligentes, des histoires bien racontées qu'il ne lirait pas dans le Journal de Montréal.

## Références de ton (audio)

- Pat McAfee Show (énergie + opinion + connaissance)
- Spittin' Chiclets (attitude hockey + insiders)
- Hugo Décrypte (rythme + clarté + condensation)
- Bill Simmons solo (prise de position fondée)

## Anti-références (à éviter absolument)

- Pages Facebook clickbait ("Vous ne devinerez jamais...")
- Listicles vides Buzzfeed
- Drama fabriqué sans source
- Sites tabloïd de sport bas-de-gamme

## Identité visuelle souhaitée

**Vibe** : sport broadcast moderne, énergique, premium. Pas Barstool, pas TVA Sports cheesy. Plus proche de The Athletic, Hugo Décrypte, ou Bleacher Report (sans le clickbait).

**Palette suggérée (à raffiner par Claude Design)** :
- Rouge écarlate primaire : `#E63946` (alarme buzzer, urgence sport)
- Noir profond : `#0D0D0D` (broadcast, autorité)
- Accent jaune buzzer : `#FFD60A` (signal, sirène)
- Texte clair : `#F1FAEE` (off-white)
- Texte foncé : `#1A1A1A`

Pas obligatoire de tout garder — si Claude Design propose mieux, on accepte. La règle : doit signaler "sport + énergie + sérieux" en thumbnail Spotify 64×64.

**Typographie** : sans-serif compressé style broadcast (Anton, Bebas Neue, Druk, Akkurat Mono pour mono). Pas de typo "podcast pop" surchargée.

**Assets à produire** :

1. **Wordmark / logo principal** — usage cover Spotify/Apple 3000×3000, et brand-icon 1024×1024 (avatar X/IG/TikTok). Le wordmark devrait être ÉNORME, dominer la cover. Pas d'illustration, pas de mascotte, pas de photo de joueur (problèmes de droits).

2. **Brand-icon compact** — pour social avatars 32-64px. Probablement "LB" ou un symbole minimaliste (icône de sirène/buzzer stylisé) sur fond rouge ou noir.

3. **Cover artwork Spotify/Apple** — 3000×3000, doit être lisible en thumbnail 64×64. Wordmark central énorme, accent visuel (ligne, point, forme), background uni.

4. **YouTube background 1280×720** — pour les épisodes vidéo. Wordmark top-left modeste, large zone centrale vide (sera remplie par une waveform animée pendant les épisodes), bandeau bas pour date/numéro d'épisode.

5. **Landing page lebuzzer.com** — single-page minimaliste :
   - Hero avec wordmark énorme + tagline
   - 1 phrase de description
   - Boutons "Écouter sur Spotify / Apple Podcasts / YouTube" (placeholders pour l'instant)
   - Lien vers le feed RSS
   - Footer minimal
   - Doit pouvoir se déployer comme site statique (HTML/CSS pur, ou React/Next si nécessaire)

6. **Templates clips verticaux 1080×1920** — pour TikTok/Reels/Shorts. Bandeau supérieur fixe avec logo + branding, zone centrale pour B-roll vidéo + waveform, bandeau bas pour sous-titres karaoké.

## Tagline candidate

"Le podcast sport quotidien." (simple, direct, joue sur le buzzer = fin du jeu = condensé)

Alternatives à tester : "5 minutes. Tout le sport." / "Sport. Vite. Tout."

## Contexte technique pour Claude Design

- Le site sera servi par un Cloudflare Worker (HTML/CSS pur c'est OK, pas besoin de framework lourd).
- Cover/artwork servis depuis GitHub via le worker, donc PNG/JPG statiques.
- Pas de CMS, pas de blog — c'est juste une vitrine + redirection vers Spotify/Apple/RSS.

## Ce que JE veux éviter (très important)

- Génériquement "sportif" avec des silhouettes d'athlètes ou des ballons (cheap stock).
- "Podcast micro" comme illustration centrale (c'est devenu un cliché Spotify).
- Palettes saturées de Vegas / casino sportif (paris en ligne).
- Tout ce qui rappelle TVA Sports cheesy ou les portails sport généralistes.
- Mascotte ou personnage récurrent (problèmes de cohérence et d'IP).

---

**Ressources de référence à uploader dans Claude Design si tu en as** :
- Captures d'écran de The Athletic, Hugo Décrypte, Bleacher Report (pour le ton modern broadcast).
- Aucun code existant à linker pour l'instant — le site est un placeholder dans un Cloudflare Worker.
