# TikTok LoL — Fizz, le Filou des mers

Style « dossiers » pixel art (inspiré de la vidéo de référence `src/reference.mp4`) : scène fixe sur un quai de Bilgewater, personnages pixel animés, sous-titres en haut révélés mot à mot, étiquettes et fiches « ANECDOTE N° ». Palette mer / nuit (bleu marine, turquoise, or) au lieu du rouge de la référence.

**Fichiers**
- `renders/FIZZ_LE_FILOU_DES_MERS.mp4` : version complète, 89,8 s (voix Mattyang + répliques officielles de Fizz + shanty chiptune original + bruitages)
- `renders/FIZZ_voix_bruitages.mp4` : sans musique, pour ajouter un son TikTok

**Voix** : ta voix ElevenLabs « Mattyang » (eleven_v4) + 6 répliques FR de Fizz tirées de ton fichier (« Vous ne m'attraperez pas ! », « Et plouf dans les dents ! », « Sans crainte, j'ai toujours un bond d'avance », « Vous voulez voir un tour ? », « Ça sent le poisson », « Requin, c'est l'heure de manger. À table ! »).

**Anecdotes** (bio officielle et kit du champion) : yordle amphibie des récifs de Bilgewater, rapporte les offrandes jetées par les capitaines, pris pour un esprit de l'océan qui commande les créatures des abysses ; le requin de l'ultime grandit avec la distance (Guppy, Chomper, Gigalodon) ; le trident le rend intouchable ; il aime piéger ses alliés autant que ses ennemis ; un skin le transforme en chien.

## Légende
Le champion le plus énervant de LoL cache bien son jeu 🦈 4 anecdotes sur Fizz, le Filou des mers ! Quel champion je fais ensuite ? 👇
#leagueoflegends #lol #fizz #lolfr #bilgewater #runeterra #gaming #pixelart #pourtoi

## Refaire
```bash
python3 tools/sprites.py     # sprites/*.png
python3 tools/assemble.py    # audio/voice.wav + audio/timeline.json (voix + répliques)
python3 tools/build.py .     # index.html + timing.json
python3 tools/mix.py .       # audio/mix.wav, audio/vo-sfx.wav
npx hyperframes render . -o renders/raw.mp4
```
