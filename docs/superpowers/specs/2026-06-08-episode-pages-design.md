# Spec — Pages par épisode (Le Buzzer, Phase 1)

**Date** : 2026-06-08
**Statut** : Design validé, prêt pour plan d'implémentation
**Portée** : Le Buzzer uniquement (Phase 1). Presto = Phase 2 ultérieure.

## Contexte

Le Buzzer (podcast sport quotidien QC) est live sur Spotify/Apple + lebuzzer.com. Le pipeline Python génère chaque matin (workflow GitHub Actions `buzzer.yml`) un script d'épisode (`output/scripts/AAAA-MM-JJ.xml`, versionné), un MP3 (GitHub release) et met à jour `feed.xml`. **L'audio et les items du feed sont purgés après 7 jours** (`FEED_KEEP_DAYS=7`) — décision produit assumée (personne ne réécoute les nouvelles de 2 semaines).

**Problème** : aujourd'hui le site n'a qu'une homepage + un feed. Zéro surface indexable par épisode → quasi aucun bénéfice SEO, et aucune page citable par les moteurs IA (ChatGPT, Perplexity, Google AI Overviews). Aucune page web lisible/partageable pour un épisode donné.

**Objectif** : générer une **page HTML par épisode** qui sert deux audiences :
1. **Humains** (épisode du jour) : lire au lieu d'écouter, lien partageable pour les réseaux.
2. **Machines** (archive permanente) : surface indexable + citable, qui composé dans le temps à coût zéro une fois bâtie.

Les transcripts existent déjà dans les scripts versionnés (`<intro>`, `<chapitre titre>`, `<outro>`) → l'archive est persistante par construction.

## Décisions prises

- **Permanence** : pages texte **permanentes** (archive), même quand l'audio expire à 7j. L'audio reste éphémère (inchangé).
- **Discrétion** : pages accessibles par URL + sitemap seulement ; **pas** mises en avant sur la homepage (préserver l'esprit « éphémère » côté auditeur).
- **Déploiement** : phasé — **Le Buzzer d'abord** (chemin propre, GitHub Pages auto-redéploie au push). Presto plus tard.

## Architecture

Le Buzzer = **GitHub Pages** servant le dossier `site/` du repo `meerkly-00/lebuzzer-podcast`, proxifié par Cloudflare. Un push sur `main` redéploie le site.

### Composants

**1. `src/episode_pages.py`** (nouveau module)
- `parse_script(path) -> EpisodeContent` : extrait la date (nom de fichier), `<intro>`, liste `[(titre, corps)]` des `<chapitre>`, `<outro>`. Robuste au préambule de raisonnement avant le bloc `<script>`.
- `episode_metadata(date, feed_path) -> EpisodeMeta` : titre, durée, URL audio, booléen `audio_actif` (date > aujourd'hui − 7j). Lit `feed.xml` quand l'épisode y figure ; sinon mode transcript-seul (audio expiré).
- `render_episode_page(content, meta) -> str` : HTML depuis le template.
- `build_all(scripts_dir, site_dir, feed_path)` : génère `site/episodes/AAAA-MM-JJ/index.html` pour **tous** les scripts versionnés + régénère `site/sitemap.xml` (home + feed + toutes les pages épisodes). Idempotent.
- CLI : `python -m src.episode_pages` (régénère tout).

**2. Template `templates/episode.html`**
- Page **légère** (cible < 50 Ko, idéalement ~15-30 Ko) — surtout PAS dérivée de la homepage (1,18 Mo). CSS minimal inline aux couleurs Le Buzzer.
- Structure :
  - `<h1>` : titre + date
  - Résumé on-page : le paragraphe `<intro>` complet (déjà rédigé comme un sommaire « au menu »)
  - **Lecteur audio** `<audio>` si `audio_actif` ; sinon encart « Épisode archivé — l'audio n'est plus disponible (épisodes dispo 7 jours) » + CTA vers l'épisode du jour
  - **Transcript** : chaque chapitre = `<h2 titre>` + paragraphes du corps
  - Liens Spotify/Apple (de la série)
  - Breadcrumb : Accueil › Épisodes › [date]
- `<head>` complet : `lang="fr-CA"`, title **unique** (`LE BUZZER — édition du [date]`) + meta description = ~155 premiers caractères de l'intro, canonical `https://www.lebuzzer.com/episodes/AAAA-MM-JJ/`, OG (title/description/url/image artwork).

**3. Schema JSON-LD par page**
- `PodcastEpisode` : `name`, `datePublished`, `timeRequired` (durée ISO 8601), `partOfSeries` (PodcastSeries LE BUZZER), `associatedMedia` (`AudioObject` avec contentUrl) **uniquement si audio actif**, `description`.
- `BreadcrumbList` : Accueil → Épisodes → date.

**4. Intégration `buzzer.yml`**
- Nouvelle étape après « Générer LE BUZZER du jour » (et après la mise à jour du feed) : `python -m src.episode_pages`.
- Étendre l'étape de commit existante pour inclure `site/episodes/` et `site/sitemap.xml`.
- **À vérifier en implémentation** : confirmer que GitHub Pages republie au push malgré `[skip ci]` (Pages « deploy from branch » ignore `[skip ci]`, qui ne concerne que GitHub Actions). Si Pages passe par un workflow Actions, ajuster.

**5. Backfill** : le premier run (manuel via `workflow_dispatch` ou local) génère les ~7 épisodes déjà versionnés → archive démarre non-vide.

## Structure d'URL

`https://www.lebuzzer.com/episodes/AAAA-MM-JJ/` → fichier `site/episodes/AAAA-MM-JJ/index.html`.

## Hors-portée (Phase 1)

- Presto (Phase 2 : nécessite de régler le déploiement Cloudflare Pages / wrangler).
- Page d'index navigable « toutes les archives » (pages accessibles par URL/sitemap seulement pour l'instant).
- Réécriture des tweets auto pour pointer vers les pages (amélioration future, une fois les pages live).
- Page FAQ / autres surfaces AEO.

## Vérification (critères d'acceptation)

1. `python -m src.episode_pages` génère une page par script versionné sans erreur, idempotent.
2. Une page épisode valide sur https://validator.schema.org et le Rich Results Test (PodcastEpisode + BreadcrumbList détectés).
3. Page du jour : lecteur audio présent et jouable. Page > 7j : encart « audio expiré », pas de lecteur cassé.
4. Poids d'une page < 50 Ko.
5. `site/sitemap.xml` contient la home, le feed et toutes les URLs d'épisodes.
6. Après déploiement : `curl https://www.lebuzzer.com/episodes/2026-06-08/` retourne 200 + le transcript ; meta/canonical corrects.
7. Le commit quotidien de `buzzer.yml` inclut bien les nouvelles pages et le sitemap, et elles arrivent en live.
