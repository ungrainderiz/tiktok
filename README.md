# Découpeur vidéo – parties de 30 Mo

Envoie une seule grosse vidéo, l'application la coupe automatiquement en
plusieurs parties de **30 Mo maximum** chacune (taille modifiable).

- **Aucune perte de qualité** : pas de réencodage, la vidéo est juste découpée (très rapide).
- Coupes propres sur des images clés : chaque partie se lit normalement.
- Les parties sont créées dans un dossier `<nom>_parties` à côté de la vidéo
  (`video_partie01.mp4`, `video_partie02.mp4`, …).

## Installation (une seule fois)

1. Installer **Python 3** : https://www.python.org/downloads/ (cocher « Add Python to PATH »).
2. Installer **ffmpeg** :
   - Windows : `winget install ffmpeg` (ou télécharger sur https://www.gyan.dev/ffmpeg/builds/
     et mettre `ffmpeg.exe` + `ffprobe.exe` dans ce dossier)
   - Mac : `brew install ffmpeg`
   - Linux : `sudo apt install ffmpeg`

## Utilisation

- **Windows** : glisse ta vidéo sur `Lancer.bat` → c'est fini, le dossier des parties s'ouvre.
  Ou double-clique `Lancer.bat` puis « Choisir une vidéo… ».
- **Mac / Linux** : `python3 decoupeur.py`
- **Ligne de commande** : `python decoupeur.py ma_video.mp4 --console --taille 30`

> 1 Mo = 1 000 000 octets (la définition la plus stricte), donc chaque partie
> passe sous la limite de 30 Mo quel que soit le site.

## Version Android (APK)

Le code est dans `android/`. L'APK est compilé automatiquement par GitHub Actions
à chaque modification, puis publié dans la release **« apk »** du dépôt
(fichier `DecoupeurVideo.apk`).

1. Sur le téléphone, ouvre la page *Releases* du dépôt et télécharge `DecoupeurVideo.apk`.
2. Ouvre le fichier et autorise « Installer des applis inconnues » si Android le demande.
3. Ouvre **Découpeur 30 Mo** → « Choisir une vidéo », ou depuis la galerie :
   *Partager* → *Découpeur 30 Mo*.
4. Les parties arrivent dans la galerie, dossier `Movies/Decoupeur`. Le bouton
   « Partager les parties » permet de les envoyer directement.

Android 10 ou plus. Pas de réencodage : découpe instantanée et qualité intacte
(la vidéo doit être en MP4/MOV, comme celles filmées par un téléphone).
