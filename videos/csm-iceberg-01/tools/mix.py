"""Original chiptune bed + SFX, ducked under the ElevenLabs voiceover."""
import json, sys, io, subprocess, numpy as np, soundfile as sf
R = sys.argv[1]; SR = 44100
T = json.load(open(f"{R}/timing.json")); C = T["cuts"]; OFF = T["off"]; N = int((T["total"] + 0.3) * SR)
W = [w for w in json.load(open(f"{R}/audio/words.json"))["words"] if w["type"] == "word"]
def at(txt, after=0):
    for w in W:
        if w["start"] >= after and txt in w["text"].lower(): return w["start"] + OFF
def load(p):
    b = subprocess.run(["ffmpeg", "-v", "quiet", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "wav", "-"], capture_output=True).stdout
    return sf.read(io.BytesIO(b))[0]
def add(buf, x, t, g=1.0):
    i = int(t * SR); j = min(len(buf), i + len(x))
    if j > i and i >= 0: buf[i:j] += g * x[: j - i]
vo = np.zeros(N); add(vo, load(f"{R}/audio/vo-angel.mp3"), OFF)
rng = np.random.default_rng(3)
def env(n, a, r):
    t = np.arange(n) / SR; e = np.minimum(1, t / max(a, 1e-4)); tail = int(r * SR)
    if tail and tail < n: e[-tail:] *= np.linspace(1, 0, tail)
    return e
def pulse(f, d, duty=0.25, g=0.2):
    n = int(d * SR); t = np.arange(n) / SR; ph = (t * f) % 1
    return g * np.where(ph < duty, 1.0, -1.0) * env(n, 0.003, min(0.05, d / 3))
def tri(f, d, g=0.3):
    n = int(d * SR); t = np.arange(n) / SR; ph = (t * f) % 1
    return g * (4 * np.abs(ph - 0.5) - 1) * env(n, 0.003, min(0.04, d / 3))
def noise(d, g=0.15, dec=0.05):
    n = int(d * SR); x = rng.uniform(-1, 1, n)
    x = np.round(x * 4) / 4  # crunchy
    return g * x * np.exp(-np.arange(n) / SR / dec)
def kick():
    n = int(0.16 * SR); t = np.arange(n) / SR; f = 50 + 140 * np.exp(-t / 0.03)
    ph = np.cumsum(f) / SR % 1; return 0.5 * (4 * np.abs(ph - 0.5) - 1) * np.exp(-t / 0.07)
nt = lambda m: 440 * 2 ** ((m - 69) / 12)
BPM = 96; b = 60 / BPM; s16 = b / 4
# Am - F - C - G   (arp patterns)
prog = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]
mus = np.zeros(N)
def section(t0, t1, arp=True, bass=True, drums=False, oct=12, dark=False):
    t = t0; bar = 0
    while t < t1 - 1e-6:
        ch = prog[bar % 4] if not dark else [(57, 60, 64), (56, 59, 64)][bar % 2]
        if arp:
            pat = [0, 1, 2, 1, 0, 2, 1, 2] * 2
            for i, k in enumerate(pat):
                tt = t + i * s16
                if tt < t1: add(mus, pulse(nt(ch[k] + oct), s16 * 0.9, 0.25 if i % 2 else 0.125, 0.10), tt)
        if bass:
            for q in range(4):
                tt = t + q * b
                if tt < t1: add(mus, tri(nt(ch[0] - 12), b * 0.8, 0.32), tt)
        if drums:
            for q in range(4):
                tt = t + q * b
                if tt >= t1: break
                if q in (0, 2): add(mus, kick(), tt, 0.9)
                if q in (1, 3): add(mus, noise(0.18, 0.22, 0.06), tt)
                add(mus, noise(0.04, 0.06, 0.01), tt + b / 2)
        t += 4 * b; bar += 1
def pad(notes, t0, d, g=0.06):
    for m in notes:
        for det in (0.997, 1.003):
            x = pulse(nt(m) * det, d, 0.5, g); x *= np.minimum(1, np.linspace(0, 3, len(x))) * np.minimum(1, np.linspace(3, 0, len(x)))
            add(mus, x, t0)
# S1: soft arp, then choir swell on "ange"
section(0.0, C[1], arp=True, bass=False)
ta = at("ange", 7)
pad([69, 72, 76, 81], ta - 0.6, 3.0, 0.05)
# S2..S5 full groove
section(C[1], C[3], drums=True)
section(C[3], C[4], drums=True, dark=True, oct=0)       # touch: tension, lower
section(C[4], C[5], drums=True, oct=12)
# S6: music box melody until wake, then drone
mel = [76, 74, 72, 71, 72, 74, 76, 79, 77, 76, 74, 72]
tw = at("réveillé")
t = C[5] + 0.2
for i, m in enumerate(mel * 2):
    if t > tw - 0.2: break
    n = int(0.9 * SR); tt = np.arange(n) / SR
    x = 0.12 * np.sin(2 * np.pi * nt(m + 12) * tt) * np.exp(-tt / 0.35) + 0.05 * np.sin(4 * np.pi * nt(m + 12) * tt) * np.exp(-tt / 0.2)
    add(mus, x, t); t += b / 2 * 1.5
drone = lambda t0, d, m: add(mus, tri(nt(m), d, 0.18) * np.minimum(1, np.linspace(0, 4, int(d * SR))) * np.minimum(1, np.linspace(4, 0, int(d * SR))), t0)
drone(tw + 0.1, C[6] - tw, 33)
# S7: dark drone + heartbeat
drone(C[6], C[7] - C[6] + 0.3, 33); drone(C[6], C[7] - C[6] + 0.3, 40)
hb = C[6] + 0.3
while hb < C[7] - 0.2: add(mus, kick(), hb, 0.8); add(mus, kick(), hb + 0.22, 0.5); hb += 0.9
# S8: arp returns
section(C[7], T["total"] - 0.2, drums=True)
# ---- SFX
def blip(f0, f1, d, g=0.18):
    n = int(d * SR); t = np.arange(n) / SR; f = np.linspace(f0, f1, n); ph = np.cumsum(f) / SR % 1
    return g * np.where(ph < 0.5, 1, -1) * np.exp(-t / (d / 2))
add(mus, blip(300, 1400, 0.5, 0.16), at("chainsaw") - 0.05)
add(mus, blip(1600, 400, 0.6, 0.14), ta)
add(mus, noise(0.4, 0.5, 0.12), at("peau"))
add(mus, blip(2000, 3000, 0.25, 0.12), at("épées") - 0.05); add(mus, blip(1800, 2800, 0.25, 0.12), at("lances") - 0.05)
add(mus, noise(0.6, 0.45, 0.2), tw - 0.1)
add(mus, blip(500, 900, 0.15, 0.15), C[7] + 0.85)
for c in C[1:-1]: add(mus, noise(0.12, 0.08, 0.03), c - 0.02)
# ---- mix
mus /= np.abs(mus).max() + 1e-9
ve = np.convolve(np.abs(vo), np.ones(int(0.1 * SR)) / int(0.1 * SR), "same")
duck = 1 - 0.5 * np.clip(ve / 0.05, 0, 1)
vo = vo / (np.abs(vo).max() + 1e-9) * 0.92
mix = vo + 0.28 * mus * duck
mix = np.tanh(1.15 * mix) / np.tanh(1.15)
sf.write(f"{R}/audio/mix.wav", mix.astype(np.float32), SR)
sf.write(f"{R}/audio/vo-only.wav", (np.tanh(1.15 * vo) / np.tanh(1.15)).astype(np.float32), SR)
print("mix ok", len(mix) / SR)
