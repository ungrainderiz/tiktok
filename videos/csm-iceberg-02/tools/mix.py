"""Original underwater chiptune + SFX, ducked under the ElevenLabs voiceover (episode 2)."""
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
vo = np.zeros(N); add(vo, load(f"{R}/audio/vo.mp3"), OFF)
rng = np.random.default_rng(11)
def env(n, a, r):
    t = np.arange(n) / SR; e = np.minimum(1, t / max(a, 1e-4)); tail = int(r * SR)
    if 0 < tail < n: e[-tail:] *= np.linspace(1, 0, tail)
    return e
def pulse(f, d, duty=0.25, g=0.2):
    n = int(d * SR); t = np.arange(n) / SR; return g * np.where((t * f) % 1 < duty, 1.0, -1.0) * env(n, 0.003, min(0.05, d / 3))
def tri(f, d, g=0.3):
    n = int(d * SR); t = np.arange(n) / SR; ph = (t * f) % 1; return g * (4 * np.abs(ph - 0.5) - 1) * env(n, 0.003, min(0.04, d / 3))
def noise(d, g=0.15, dec=0.05):
    n = int(d * SR); x = np.round(rng.uniform(-1, 1, n) * 4) / 4; return g * x * np.exp(-np.arange(n) / SR / dec)
def kick():
    n = int(0.18 * SR); t = np.arange(n) / SR; f = 45 + 130 * np.exp(-t / 0.03); ph = np.cumsum(f) / SR % 1
    return 0.55 * (4 * np.abs(ph - 0.5) - 1) * np.exp(-t / 0.08)
nt = lambda m: 440 * 2 ** ((m - 69) / 12)
BPM = 88; b = 60 / BPM; s16 = b / 4
prog = [(50, 53, 57), (46, 50, 53), (48, 52, 55), (45, 49, 52)]   # Dm Bb C A
mus = np.zeros(N)
def section(t0, t1, arp=True, bass=True, drums=False, oct=12, pat=(0, 2, 1, 2)):
    t = t0; bar = 0
    while t < t1 - 1e-6:
        ch = prog[bar % 4]
        if arp:
            for i in range(16):
                tt = t + i * s16
                if tt < t1: add(mus, pulse(nt(ch[pat[i % 4]] + oct), s16 * 0.8, 0.125 if i % 2 else 0.25, 0.09), tt)
        if bass:
            for q in range(8):
                tt = t + q * b / 2
                if tt < t1: add(mus, tri(nt(ch[0] - 12), b * 0.4, 0.32), tt)
        if drums:
            for q in range(4):
                tt = t + q * b
                if tt >= t1: break
                if q in (0, 2): add(mus, kick(), tt, 0.9)
                if q in (1, 3): add(mus, noise(0.2, 0.22, 0.07), tt)
                add(mus, noise(0.04, 0.05, 0.01), tt + b / 2)
        t += 4 * b; bar += 1
def drone(t0, d, m, g=0.16):
    n = int(d * SR); x = tri(nt(m), d, g); e = np.minimum(1, np.linspace(0, 4, n)) * np.minimum(1, np.linspace(4, 0, n)); add(mus, x * e, t0)
def blub(t, f=600):
    n = int(0.12 * SR); tt = np.arange(n) / SR; fr = f * (1 + 2 * tt / 0.12); add(mus, 0.12 * np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-tt / 0.05), t)
def boom(t, g=1.0):
    n = int(0.9 * SR); tt = np.arange(n) / SR; f = 35 + 80 * np.exp(-tt / 0.08); add(mus, g * 0.7 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.35), t); add(mus, noise(0.5, 0.35 * g, 0.12), t)
def swoosh(t):
    n = int(0.35 * SR); x = rng.uniform(-1, 1, n); x = np.convolve(x, np.ones(6) / 6, "same"); add(mus, 0.25 * x * np.sin(np.linspace(0, np.pi, n)) ** 2, t)
# S1
drone(0, C[1], 38, 0.14); section(0.0, C[1], bass=False, oct=12)
tp = at("pieuvre"); boom(tp, 0.9)
for k in range(4): swoosh(at("partout") - 0.5 + k * 0.15)
for k in range(10): blub(at("descend") + k * 0.17, 500 + 60 * k)
# S2 Yoshida: chill groove
section(C[1], C[2], drums=False, pat=(0, 1, 2, 1))
# S3 action
section(C[2], C[3], drums=True)
boom(at("tentacules", 24), 1.0)
for w in ("attrapent", "frappent", "écrasent"): boom(at(w), 0.6)
# S4 deep: drone + heartbeat
drone(C[3], C[4] - C[3], 26, 0.2); drone(C[3], C[4] - C[3], 33, 0.12)
hb = C[3] + 0.3
while hb < C[4] - 0.3: add(mus, kick(), hb, 0.7); add(mus, kick(), hb + 0.22, 0.45); hb += 1.0
boom(at("énorme"), 0.8)
# S5 school
section(C[4], C[5], drums=True, bass=True, oct=24, pat=(0, 1, 2, 1))
ta = at("chainsaw", 45)
n = int(1.0 * SR); tt = np.arange(n) / SR; saw = 0.18 * np.where((tt * (110 + 20 * np.sin(2 * np.pi * 9 * tt))) % 1 < 0.5, 1, -1) * np.exp(-tt / 0.6); add(mus, saw, at("arrêter") - 0.25)
boom(ta, 0.7)
# S6 mystery: drone + ticking
drone(C[5], C[6] - C[5], 38, 0.18); drone(C[5], C[6] - C[5], 44, 0.08)
tk = C[5]
while tk < C[6] - 0.1: add(mus, noise(0.03, 0.12, 0.008), tk); tk += b / 2
# S7
section(C[6], T["total"] - 0.3, drums=True)
for c in C[1:-1]: swoosh(c - 0.15)
mus /= np.abs(mus).max() + 1e-9
ve = np.convolve(np.abs(vo), np.ones(int(0.1 * SR)) / int(0.1 * SR), "same")
duck = 1 - 0.5 * np.clip(ve / 0.05, 0, 1)
vo = vo / (np.abs(vo).max() + 1e-9) * 0.92
mix = np.tanh(1.15 * (vo + 0.28 * mus * duck)) / np.tanh(1.15)
sf.write(f"{R}/audio/mix.wav", mix.astype(np.float32), SR)
sf.write(f"{R}/audio/vo-only.wav", (np.tanh(1.15 * vo) / np.tanh(1.15)).astype(np.float32), SR)
print("mix ok")
