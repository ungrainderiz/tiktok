# TikTok — BECK : Mongolian Chop Squad

**Fichier :** `renders/BECK_tiktok_final.mp4` — 1080×1920, ~69 s, voix off FR + musique originale (synthétisée, libre de droits).

## Légende à copier
Cet anime a 20 ans et personne n'en parle 🎸 #beck #mongolianchopsquad #anime #manga #animefr #animerecommendations #rock #madhouse #pourtoi #fyp

## Conseils pour maximiser les vues
- Poste entre 18h et 21h, et réponds aux premiers commentaires dans l'heure (la vidéo finit sur une question pour ça).
- Option : ajoute dans TikTok le son « Hit in the USA » (Beat Crusaders) à volume bas (~10 %) par-dessus — un son reconnu peut booster la découverte.
- Épingle un commentaire : « Team Koyuki ou team Ryûsuke ? »
- Couverture : la frame « BECK / MONGOLIAN CHOP SQUAD » (~6 s).

## Modifier la vidéo
- Texte de la voix off : `audio/lines.tsv` (orthographe phonétique pour la synthèse) + `audio/display.tsv` (sous-titres).
- Regénérer : `npx hyperframes tts` par ligne → `python3 tools/timing.py .` → `python3 tools/mix.py .` → `python3 tools/build.py .` → `npx hyperframes render`.
- Visuels/animations : `tools/index.src.html` (le `index.html` est généré).
