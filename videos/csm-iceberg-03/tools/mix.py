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
BPM = 80; b = 60 / BPM; s16 = b / 4
prog = [(45, 48, 52), (41, 45, 48), (43, 47, 50), (40, 44, 47)]   # Am F G E
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
drone(0, C[1], 33, 0.16); section(0.0, C[1], bass=False, oct=12)
tm = at("malédiction"); boom(tm, 1.0)
for k in range(8): blub(at("descend") + k * 0.2, 400 + 40 * k)
# S2: tension groove, 3 hits on "trois coups"
section(C[1], C[2], drums=False, pat=(0, 1, 2, 1))
for i in range(3): boom(at("trois", 14) + 0.15 + i * 0.22, 0.45)
# S3: summon -> full drums, crush
section(C[2], C[3], drums=True)
for i in range(3): add(mus, noise(0.15, 0.4, 0.05), C[2] + 0.35 + i * 0.3)
boom(at("apparaît"), 1.0); boom(at("broie"), 1.1)
# S4: price, minor groove softer
section(C[3], C[4], drums=False, oct=0)
# S5: the question -> silence, drone, BOOM on "deux ans"
drone(C[4], C[5] - C[4], 33, 0.18)
td = at("deux", at("répond")); boom(td, 1.2)
tk = td + 0.5
while tk < C[5]: add(mus, noise(0.03, 0.14, 0.008), tk); tk += 0.5
# S6: sad music box
mel = [76, 72, 69, 72, 74, 71, 67, 71, 72, 69, 64, 69]
t = C[5] + 0.1; k = 0
while t < C[6] - 0.3:
    m = mel[k % len(mel)]; n = int(1.0 * SR); tt = np.arange(n) / SR
    add(mus, 0.13 * np.sin(2 * np.pi * nt(m + 12) * tt) * np.exp(-tt / 0.4) + 0.05 * np.sin(4 * np.pi * nt(m + 12) * tt) * np.exp(-tt / 0.2), t)
    t += 0.42; k += 1
drone(C[5], C[6] - C[5], 45, 0.08)
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
