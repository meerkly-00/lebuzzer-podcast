# LE BUZZER — Kit réseaux sociaux (prêt à coller)

Tout est prêt. Il manque **une seule action humaine** : être connecté aux **bons comptes**
dans Chrome (voir « Pourquoi ce n'est pas auto » plus bas). Une fois connecté, tout se colle en ~5 min.

---

## 1) Photo de profil (les deux plateformes)

Fichier : `site/assets/profile-1024.png` (icône buzzer officielle : Z crème + lampe rouge / rayons jaunes sur noir).
Carré 1024×1024, déjà cadré pour le rognage circulaire d'Instagram et TikTok.

> ⚠️ Remplace l'ancienne icône « LB ». La nouvelle est tirée du dossier de marque (Z + lampe de but).

---

## 2) Lien en bio (les deux)

```
https://www.lebuzzer.com
```

---

## 3) Bio Instagram (@le_buzzer_qc) — 94 / 150 caractères

```
Le sport du Québec en 5 min ⏱️ LNH·NBA·Foot·F1·MMA. Nouvel épisode chaque matin 6h 🏒🔥 Écoute 👇
```

## 4) Bio TikTok (@le_buzzerqc) — 60 / 80 caractères

```
Le sport du Québec en 5 min, chaque matin 6h 🏒🔥 lebuzzer.com
```

## 5) Bannière / photo de couverture
- **Instagram** : pas de bannière (n'existe pas sur IG). Rien à faire.
- **TikTok** : pas d'image de couverture de profil sur le web ; l'app permet une courte vidéo de couverture (optionnel, plus tard).
- **YouTube** (si activé un jour) : `artwork/youtube-bg-v1.png` (1536×1024) est prêt.

---

## 6) Clips à publier (TikTok + Reels Instagram)

Générés ce soir depuis l'épisode du 2 juin, verticaux 1080×1920, sous-titrés karaoke + outro `lebuzzer.com` :

| Fichier | Sujet | Durée |
|---|---|---|
| `output/clips/2026-06-02_clip_1.mp4` | Bombe de Patrik Laine / dossier CH | ~40 s |
| `output/clips/2026-06-02_clip_2.mp4` | Chaos NFL : Garrett aux Rams, Brown aux Patriots | ~52 s |

### Caption clip 1
```
Laine pas blessé en fin de saison?! 😳 Le dossier le plus chaud de l'été pour le CH

#lebuzzer #canadiensmtl #patriklaine #habs #nhl #hockeyqc
```

### Caption clip 2
```
Le meilleur défenseur de la NFL échangé! 🤯 Journée de chaos total

#lebuzzer #nfl #mylesgarrett #ajbrown #rams #patriots
```

---

## 7) Post de lancement (image = cover, si tu préfères annoncer avant un clip)

Visuel : `artwork/cover-v1.png`

### Caption lancement (IG + TikTok)
```
🔴🟡 LE BUZZER EST LÀ.

Le sport du Québec, décortiqué en 5 minutes chaque matin à 6h.
Canadiens, LNH, NBA, foot, F1, MMA — pas juste les résultats, un point de vue.

Abonne-toi 👉 lebuzzer.com

#lebuzzer #sportquebec #hockeyqc #canadiensmtl #nhl #nba #podcastqc
```

---

## Pourquoi ce n'est pas 100 % automatisé ce soir

L'agent pilote Chrome, mais **les bons comptes ne sont pas connectés** dans le profil Chrome contrôlable :
- **Instagram** propose seulement `djee.whiz` et `benito.3d` (pas `le_buzzer_qc`).
- **TikTok** affiche « Connexion » (déconnecté).

L'agent **ne se connecte jamais à un compte** (saisie de mot de passe interdite) et **ne publie pas
depuis un mauvais compte**. Pour finir l'automatisation :

1. Dans Chrome, connecte-toi à **@le_buzzer_qc** (Instagram) et **@le_buzzerqc** (TikTok).
2. Relance l'agent : « les comptes LE BUZZER sont connectés, configure les profils + publie le clip 1 ».
   Il fera : photo de profil, bio, lien, puis upload du clip avec la caption.

(Ou fais-le à la main avec ce kit : ~5 min.)
