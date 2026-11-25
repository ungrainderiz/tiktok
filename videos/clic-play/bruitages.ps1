# Bruitages synthetises avec ffmpeg (aucun telechargement), cales sur l'animation d'index.html -> assets/bruitages.wav
$env:PATH = "$env:LOCALAPPDATA\ffmpeg\ffmpeg-master-latest-win64-gpl\bin;$env:PATH"
Set-Location $PSScriptRoot
$S = 48000
$f = @(
  # [temps (ms), source lavfi, filtres, volume]
  @(40,   "anoisesrc=d=0.45:c=pink:r=${S}:a=0.9", "highpass=f=300,lowpass=f=4000,afade=t=in:d=0.25,afade=t=out:st=0.25:d=0.2", 0.9),   # carte qui arrive : whoosh
  @(330,  "aevalsrc='sin(2*PI*(500*t+2600*t*t))*exp(-t*22)':d=0.18:s=${S}", "anull", 0.7),                                        # titre : pop
  @(600,  "anoisesrc=d=0.6:c=white:r=${S}:a=0.6", "highpass=f=1200,lowpass=f=7000,afade=t=in:d=0.3,afade=t=out:st=0.3:d=0.3", 0.45), # souris qui file
  @(1550, "aevalsrc='sin(2*PI*2400*t)*exp(-t*300)':d=0.04:s=${S}", "anull", 0.5),                                                 # survol : tic
  @(1850, "anoisesrc=d=0.03:c=white:r=${S}:a=1", "highpass=f=2000,afade=t=out:d=0.03", 0.9),                                      # clic (appui)
  @(1850, "aevalsrc='sin(2*PI*180*t)*exp(-t*90)':d=0.06:s=${S}", "anull", 0.8),
  @(1960, "anoisesrc=d=0.025:c=white:r=${S}:a=1", "highpass=f=3000,afade=t=out:d=0.025", 0.6),                                    # clic (relache)
  @(1970, "aevalsrc='(sin(2*PI*1319*t)+sin(2*PI*1760*t)+0.7*sin(2*PI*2637*t)+0.5*sin(2*PI*3520*t))*exp(-t*5)/3':d=0.9:s=${S}", "aecho=0.6:0.5:60:0.3", 0.55), # etincelles
  @(2020, "aevalsrc='sin(2*PI*(90*t-35*t*t))*exp(-t*7)':d=0.6:s=${S}", "anull", 1.0),                                             # JOUE ! : impact grave
  @(2020, "anoisesrc=d=0.25:c=brown:r=${S}:a=1", "lowpass=f=900,afade=t=out:d=0.25", 0.6)
)
$in = @(); $fc = ""; $mix = ""
for ($i = 0; $i -lt $f.Count; $i++) {
  $in += "-f"; $in += "lavfi"; $in += "-i"; $in += $f[$i][1]
  $fc += "[$($i):a]$($f[$i][2]),volume=$($f[$i][3]),adelay=$($f[$i][0])|$($f[$i][0]),aformat=channel_layouts=stereo[s$i];"
  $mix += "[s$i]"
}
$fc += "$($mix)amix=inputs=$($f.Count):normalize=0:duration=longest,apad=pad_dur=3,atrim=0:4,alimiter=limit=0.9"
& ffmpeg -v error -y @in -filter_complex $fc -ar $S assets\b0.wav
& ffmpeg -v error -y -i assets\b0.wav -af apad -t 4 assets\bruitages.wav; Remove-Item assets\b0.wav
"ok"
