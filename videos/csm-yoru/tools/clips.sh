#!/bin/bash
# Extraits de src/extra.mp4 -> clips verticaux 1080x1920 (fond flouté rouge + plan cinéma au centre)
set -e
cut() { name=$1; a=$2; b=$3
  ffmpeg -v error -y -ss $a -to $b -i src/extra.mp4 -an -filter_complex "[0:v]fps=30,split[a][b];[a]scale=-2:1920,crop=1080:1920,boxblur=24:2,eq=brightness=-0.28:contrast=1.1,colorchannelmixer=rr=1:gg=0.25:bb=0.25[bg];[b]scale=1080:-2,eq=contrast=1.15[fg];[bg][fg]overlay=0:520,format=yuv420p" -c:v libx264 -crf 22 -preset fast -movflags +faststart clips/$name.mp4
  echo $name $(ffprobe -v error -show_entries format=duration -of csv=p=0 clips/$name.mp4); }
cut yoru_face 84.4 88.6
cut yoru_eye 46.0 49.0
cut yoru_street 31.0 35.5
cut gun_txt 100.8 103.0
cut tank_txt 99.0 100.7
cut gulf 104.0 111.5
cut vault 118.0 127.5
cut elbrus 128.0 134.6
cut ak 136.0 141.6
cut hands 174.0 177.6
cut hands2 183.0 187.6
cut yoru_point 189.0 191.8
cut statue_face 194.0 203.5
cut people 204.0 206.8
cut statue_gun 220.0 228.6
cut statue_aim 229.0 233.6
cut bang 238.3 240.0
cut bullet 241.0 247.8
cut explode 252.5 256.8
