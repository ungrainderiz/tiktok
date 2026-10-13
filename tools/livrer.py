#!/usr/bin/env python3
"""Copie TikTok d'un rendu HyperFrames : son à -14 LUFS (gain + limiteur hors-ligne, sans changer la durée),
vidéo H.264 en 2 passes calculée pour tenir sous 28 Mo, + un test de boucle ×2 en basse définition.

Usage : python3 tools/livrer.py <rendu.mp4> <copie-tiktok.mp4> [test-boucle.mp4]
(loudnorm d'ffmpeg est évité : il raccourcit la piste d'~0,1 s et casserait le raccord de boucle)
"""
import os
import re
import subprocess
import sys
import tempfile

import numpy as np
from scipy.ndimage import maximum_filter1d, uniform_filter1d

SR = 48000
CIBLE_LUFS = -14.0
PLAFOND = 0.84  # ≈ -1,5 dBFS avant encodage AAC
MAX_MO = 28


def lufs(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[0-9.]+) LUFS", err)[-1])


def limite(x, gain_db):
    x = x * 10 ** (gain_db / 20)
    env = maximum_filter1d(np.abs(x).max(axis=1), size=481)  # fenêtre centrée ±5 ms : pas de latence (hors-ligne)
    red = np.minimum(1, PLAFOND / np.maximum(env, 1e-9))
    red = uniform_filter1d(maximum_filter1d(1 - red, size=961), size=961)
    return x * (1 - red)[:, None]


def main(src, dst, boucle=None):
    tmp = tempfile.mkdtemp()
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-vn", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    mix = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).astype(float)
    gain = CIBLE_LUFS - lufs(src)
    audio = os.path.join(tmp, "a.m4a")
    for _ in range(4):  # le limiteur mange un peu de volume : on ajuste jusqu'à -14 ± 0,3
        y = limite(mix, gain).astype(np.float32)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "aac",
                        "-b:a", "160k", audio], input=y.tobytes(), check=True)
        mesure = lufs(audio)
        if abs(mesure - CIBLE_LUFS) < 0.3:
            break
        gain += CIBLE_LUFS - mesure
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src],
                               capture_output=True, text=True).stdout)
    kbps = int(MAX_MO * 8 * 1024 / dur - 170)
    log = os.path.join(tmp, "x264")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-c:v", "libx264", "-preset", "slow", "-b:v", f"{kbps}k", "-pass", "1",
                    "-passlogfile", log, "-an", "-f", "null", "/dev/null"], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
                    "-preset", "slow", "-b:v", f"{kbps}k", "-pass", "2", "-passlogfile", log, "-pix_fmt", "yuv420p", "-c:a", "copy",
                    "-movflags", "+faststart", dst], check=True)
    print(f"{dst} : {os.path.getsize(dst) / 1e6:.1f} Mo, {lufs(dst):.1f} LUFS, vidéo {kbps} kb/s")
    if boucle:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-stream_loop", "1", "-i", dst, "-c:v", "libx264", "-crf", "30", "-preset", "fast",
                        "-vf", "scale=540:960", "-c:a", "aac", "-b:a", "128k", boucle], check=True)
        print(f"{boucle} : {os.path.getsize(boucle) / 1e6:.1f} Mo")


if __name__ == "__main__":
    main(*sys.argv[1:])
