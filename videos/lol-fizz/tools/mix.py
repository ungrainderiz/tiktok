"""Musique chiptune originale (shanty de pirate), ambiance mer et bruitages ElevenLabs, voix au-dessus."""
import json, sys, io, subprocess, numpy as np, soundfile as sf
R = sys.argv[1]; SR = 44100
T = json.load(open(f"{R}/audio/timeline.json")); TOT = T["total"]; N = int(TOT * SR); FZ = T["fizz"]
C = json.load(open(f"{R}/timing.json"))["cuts"]
WD = T["words"]
def at(txt, after=0):
    for w in WD:
        if w["start"] >= after and txt in w["text"].lower(): return w["start"]
    raise SystemExit("missing " + txt)
def load(p):
    b = subprocess.run(["ffmpeg", "-v", "quiet", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "wav", "-"], capture_output=True).stdout
    return sf.read(io.BytesIO(b))[0]
def add(buf, x, t, g=1.0):
    i = int(t * SR)
    if i < 0: x = x[-i:]; i = 0
    j = min(len(buf), i + len(x))
    if j > i: buf[i:j] += g * x[: j - i]
vo = load(f"{R}/audio/voice.wav")[:N]; vo = np.pad(vo, (0, N - len(vo)))
rng = np.random.default_rng(3)
nt = lambda m: 440 * 2 ** ((m - 69) / 12)
def sq(m, d, g=0.18, duty=0.5, dec=0.25):
    n = int(d * SR); t = np.arange(n) / SR; x = np.where((t * nt(m)) % 1 < duty, 1.0, -1.0)
    return g * x * np.minimum(1, t / 0.005) * np.exp(-t / dec) * np.minimum(1, (d - t) / 0.01)
def tri(m, d, g=0.3):
    n = int(d * SR); t = np.arange(n) / SR; ph = (t * nt(m)) % 1; x = 4 * np.abs(ph - 0.5) - 1
    return g * x * np.minimum(1, (d - t) / 0.02)
def noise(d, g, dec): n = int(d * SR); return g * rng.uniform(-1, 1, n) * np.exp(-np.arange(n) / SR / dec)
mus = np.zeros(N)
BPM = 112; b = 60 / BPM
# mélodie originale en ré mineur (2 mesures de 6 croches = 1 phrase)
MEL = [(62, 1), (65, 1), (69, 1), (67, 2), (65, 1), (64, 1), (62, 1), (64, 1), (65, 3),
       (69, 1), (72, 1), (70, 1), (69, 2), (67, 1), (65, 1), (64, 1), (61, 1), (62, 3)]
BASS = [50, 50, 46, 45, 50, 50, 43, 45]
def shanty(t0, t1, lead=True, g=1.0, low=False):
    e = b / 2; t = t0; k = 0; bar = 0
    while t < t1 - 1e-6:
        if lead:
            m, ln = MEL[k % len(MEL)]
            add(mus, sq(m + (-12 if low else 0), ln * e * 0.95, 0.12 * g, 0.25, 0.3), t)
            t_next = t + ln * e; k += 1
        else: t_next = t + 3 * e
        # basse + percussions sur la mesure (6 croches)
        while bar * 6 * e + t0 <= t and bar * 6 * e + t0 < t1:
            tb = t0 + bar * 6 * e
            add(mus, tri(BASS[bar % 8], 3 * e * 0.9, 0.28 * g), tb); add(mus, tri(BASS[bar % 8] + 7, 3 * e * 0.9, 0.18 * g), tb + 3 * e)
            if not low:
                for q in range(6): add(mus, noise(0.04, 0.12 * g, 0.01), tb + q * e)
                add(mus, noise(0.12, 0.25 * g, 0.04), tb + 3 * e)
            bar += 1
        t = t_next
def drone(t0, t1, m=38, g=0.25):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * nt(m) * t) + 0.5 * np.sin(2 * np.pi * nt(m + 7) * t * 1.003)
    add(mus, g * x * np.minimum(1, t / 0.6) * np.minimum(1, (t1 - t0 - t) / 0.4) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.3 * t)), t0)
# vagues (bruit filtré, en continu)
n = N; wv = np.convolve(rng.uniform(-1, 1, n), np.ones(60) / 60, "same"); tt = np.arange(n) / SR
waves = 0.5 * wv * (0.55 + 0.45 * np.sin(2 * np.pi * tt / 4.5) ** 2)
# arrangement
drone(0, C[1] + 0.2, 38, 0.22)
for i in range(4): add(mus, sq(74 - i * 3, 0.4, 0.06, 0.5, 0.2), 0.8 + i * 1.1)   # notes mystérieuses
shanty(C[1], C[4], lead=True)
drone(C[4], C[5], 38, 0.25); shanty(C[4], C[5], lead=True, g=0.6, low=True)       # sous l'eau
shanty(C[5], C[9], lead=True)
end_chomp = FZ[5]["start"] + 3.4
shanty(C[9], FZ[5]["start"] + 1.4, lead=True, g=0.9)
# bruitages
fx = np.zeros(N)
def sfx(name, t, g=1.0, maxd=None):
    x = load(f"{R}/audio/sfx/{name}.mp3")
    if maxd: x = x[: int(maxd * SR)]; x = x * np.minimum(1, (len(x) - np.arange(len(x))) / (0.05 * SR))
    x = x / (np.abs(x).max() + 1e-9); add(fx, x, t, g)
L = "../../library/sfx"
def lib(path, t, g=1.0, maxd=None):
    x = load(f"{L}/{path}.mp3")
    if maxd: x = x[: int(maxd * SR)]
    x = x / (np.abs(x).max() + 1e-9); add(fx, x, t, g)
for c in C[1:-1]: lib("whoosh/whoosh_1", c - 0.15, 0.35, 0.7)
lib("ambiance/pop_0", at("énervant"), 0.4, 0.4); lib("ambiance/pop_1", at("mystérieux"), 0.4, 0.4)
lib("impact/impact_2", C[1] + 0.05, 0.7); lib("ambiance/pop_2", at("filou"), 0.35, 0.4)
sfx("splash_0", C[2] + 0.05, 0.7); lib("ambiance/pop_0", at("yordle"), 0.35, 0.4); sfx("splash_1", at("amphibie") + 0.7, 0.5); sfx("splash_3", at("amphibie") + 1.0, 0.4, 1.2)
lib("ambiance/door_0", at("bilgewater") - 0.05, 0.4)
sfx("coins_2", at("jettent"), 1.0); sfx("splash_0", at("jettent") + 0.75, 0.5); sfx("bubbles_1", at("fizz", 19.5), 0.6); sfx("coins_0", at("récupère"), 0.9)
sfx("splash_1", at("rapporte") - 0.05, 0.6); lib("ambiance/pop_3", at("vieux"), 0.4, 0.4); lib("ambiance/stamp_0", at("jamais", 25), 0.8)
sfx("bubbles_0", C[4], 0.6); sfx("bubbles_2", C[4] + 2.2, 0.5); lib("stand/summon_1", at("commander") - 0.2, 0.4)
lib("ambiance/stamp_1", C[5] + 0.05, 0.6); sfx("splash_3", at("jette") + 0.6, 0.4, 0.8); sfx("splash_1", at("loin") + 0.5, 0.4, 0.8)
for w in ("guppy", "chomper", "gigalodon"): sfx("chomp_2", at(w), {"guppy": 0.4, "chomper": 0.6, "gigalodon": 0.9}[w])
sfx("chomp_0", FZ[1]["start"], 0.8); sfx("chomp_2", FZ[1]["end"] - 0.4, 1.0)
lib("ambiance/stamp_1", C[6] + 0.05, 0.6); lib("ambiance/pop_1", at("sauter"), 0.5, 0.4)
sfx("beam_0", at("esquive"), 0.5); sfx("beam_2", at("esquive") + 0.4, 0.5); sfx("beam_3", at("ultimes") - 0.15, 1.0)
lib("ambiance/pop_2", at("déteste"), 0.4, 0.4)
lib("ambiance/stamp_1", C[7] + 0.05, 0.6); sfx("splash_0", at("piéger"), 0.6); sfx("splash_1", at("ennemis") - 0.1, 0.6)
lib("ambiance/stamp_1", C[8] + 0.05, 0.6); sfx("poof_2", at("chien") - 0.15, 0.8, 1.2); sfx("bark_3", at("chien") + 0.3, 0.8)
lib("ambiance/pop_0", at("esprit", 79), 0.35, 0.4); lib("ambiance/pop_1", at("filou", 80), 0.35, 0.4)
sfx("bubbles_0", FZ[5]["start"] + 1.6, 0.6); sfx("chomp_0", end_chomp - 0.2, 1.0); sfx("splash_3", end_chomp - 0.1, 0.6, 1.0)
# mix
mus /= np.abs(mus).max() + 1e-9; fx /= np.abs(fx).max() + 1e-9
mus[int(end_chomp * SR):] = 0
ve = np.convolve(np.abs(vo), np.ones(int(0.12 * SR)) / int(0.12 * SR), "same"); act = np.clip(ve / 0.04, 0, 1)
mix = vo * 0.95 + 0.17 * mus * (1 - 0.45 * act) + 0.4 * fx * (1 - 0.25 * act) + 0.04 * waves
mix = np.tanh(1.1 * mix) / np.tanh(1.1)
sf.write(f"{R}/audio/mix.wav", mix.astype(np.float32), SR)
sf.write(f"{R}/audio/vo-sfx.wav", (np.tanh(1.1 * (vo * 0.95 + 0.4 * fx * (1 - 0.25 * act))) / np.tanh(1.1)).astype(np.float32), SR)
print("mix ok", TOT)
