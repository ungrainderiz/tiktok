#!/bin/bash
# Extraits de src/grand_sage.mp4 (640x360) -> clips verticaux 1080x1920 (fond flouté bleu + plan au centre, bandeau sous-titres/logo rogné)
set -e
cut() { name=$1; a=$2; b=$3
  ffmpeg -v error -y -ss $a -to $b -i src/grand_sage.mp4 -an -filter_complex "[0:v]fps=30,crop=640:300:0:60,split[a][b];[a]scale=-2:1920,crop=1080:1920,boxblur=24:2,eq=brightness=-0.22:contrast=1.1,colorchannelmixer=rr=0.35:gg=0.6:bb=1[bg];[b]scale=1080:-2,eq=contrast=1.1:saturation=1.15[fg];[bg][fg]overlay=0:575,format=yuv420p" -c:v libx264 -crf 21 -preset fast -movflags +faststart clips/$name.mp4
  echo $name $(ffprobe -v error -show_entries format=duration -of csv=p=0 clips/$name.mp4); }
cut evo 0.0 2.8
cut harvest 18.6 23.2
cut raph 23.3 28.0
cut belz 29.6 33.5
