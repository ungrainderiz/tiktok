"""Variante OST : voix + bruitages + 'It's just a burning memory' (The Caretaker) en fond, à la place de la musique originale."""
import json, sys, io, subprocess, numpy as np, soundfile as sf
R = sys.argv[1]; OST = sys.argv[2]; SR = 44100
T = json.load(open(f"{R}/timing.json")); C = T["cuts"]; TOT = T["total"]
def load(p, extra=()):
    b = subprocess.run(["ffmpeg", "-v", "quiet", "-i", p, *extra, "-ac", "1", "-ar", str(SR), "-f", "wav", "-"], capture_output=True).stdout
    return sf.read(io.BytesIO(b))[0]
base, _ = sf.read(f"{R}/audio/vo-sfx.wav"); vo, _ = sf.read(f"{R}/audio/vo-only.wav"); N = len(base)
clean = load(OST, ("-t", str(TOT + 1)))[:N]
muff = load(OST, ("-t", str(TOT + 1), "-af", "lowpass=f=500,aecho=0.8:0.7:120:0.4"))[:N]  # disque « lointain »
pad = lambda x: np.pad(x, (0, max(0, N - len(x))))
clean, muff = pad(clean), pad(muff)
t = np.arange(N) / SR
# zombies invisibles (S4) et mort de Maxx : le disque s'éloigne
w = np.clip(np.minimum((t - (C[3] - 0.3)) / 0.4, ((C[4] + 0.2) - t) / 0.4), 0, 1)
mus = (1 - w) * clean + w * muff * 1.6
mus /= np.abs(mus).max() + 1e-9
env = np.ones(N); env *= np.clip(t / 0.3, 0, 1)
tb = TOT - 2.3; env[t >= tb] = 0  # coupé net sur le freeze « To Be Continued »
ve = np.convolve(np.abs(vo), np.ones(int(0.12 * SR)) / int(0.12 * SR), "same"); act = np.clip(ve / 0.04, 0, 1)
mix = np.tanh(1.2 * (base + 0.3 * mus * env * (1 - 0.45 * act))) / np.tanh(1.2)
sf.write(f"{R}/audio/mix-ost.wav", mix.astype(np.float32), SR)
print("ok", N / SR)
