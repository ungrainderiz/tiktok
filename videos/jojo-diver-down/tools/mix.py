"""Original funky JoJo-inspired groove (no copyrighted melodies) + SFX, ducked under the voiceover."""
import json, sys, io, subprocess, numpy as np, soundfile as sf
R = sys.argv[1]; SR = 44100
T = json.load(open(f"{R}/timing.json")); C = T["cuts"]; OFF = T["off"]; N = int((T["total"] + 0.3) * SR)
WD = [w for w in json.load(open(f"{R}/audio/words.json"))["words"] if w["type"] == "word"]
def at(txt, after=0):
    for w in WD:
        if w["start"] + OFF >= after and txt in w["text"].lower(): return w["start"] + OFF
    raise SystemExit("missing " + txt)
def load(p):
    b = subprocess.run(["ffmpeg", "-v", "quiet", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "wav", "-"], capture_output=True).stdout
    return sf.read(io.BytesIO(b))[0]
def add(buf, x, t, g=1.0):
    i = int(t * SR); j = min(len(buf), i + len(x))
    if j > i and i >= 0: buf[i:j] += g * x[: j - i]
vo = np.zeros(N); add(vo, load(f"{R}/audio/vo.mp3"), OFF)
rng = np.random.default_rng(5)
nt = lambda m: 440 * 2 ** ((m - 69) / 12)
def env(n, a, d): t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
def noise(d, g, dec): n = int(d * SR); return g * rng.uniform(-1, 1, n) * np.exp(-np.arange(n) / SR / dec)
def kick():
    n = int(0.25 * SR); t = np.arange(n) / SR; f = 48 + 120 * np.exp(-t / 0.035)
    return 0.9 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.12)
def snare(): n = int(0.2 * SR); t = np.arange(n) / SR; return noise(0.2, 0.5, 0.06) + 0.3 * np.sin(2 * np.pi * 200 * t) * np.exp(-t / 0.05)
def hat(o=False): return noise(0.18 if o else 0.05, 0.16, 0.06 if o else 0.012)
def slap(m, d):  # funky bass: saw-ish with fast pluck
    n = int(d * SR); t = np.arange(n) / SR; ph = (t * nt(m)) % 1
    x = (2 * ph - 1) * 0.6 + 0.4 * np.sin(2 * np.pi * nt(m) * t)
    return 0.42 * np.tanh(2.2 * x) * env(n, 0.002, d * 0.5)
def brass(ms, d, g=0.12):
    n = int(d * SR); t = np.arange(n) / SR; out = np.zeros(n)
    for m in ms:
        for det in (0.996, 1.004): out += np.where((t * nt(m) * det) % 1 < 0.35, 1, -1)
    e = np.minimum(1, t / 0.01) * np.exp(-t / (d * 0.7)); return g * out / len(ms) * e
mus = np.zeros(N)
BPM = 120; b = 60 / BPM
# Em funky riff pattern (original): root, octave, b7, 5 syncopated
riff = [(40, 0), (52, 0.75), (50, 1.5), (47, 2.0), (40, 2.5), (43, 3.0), (45, 3.5)]
def groove(t0, t1, full=True, brass_on=True, shift=0):
    t = t0; bar = 0
    while t < t1 - 1e-6:
        for q in range(4):
            tq = t + q * b
            if tq >= t1: break
            add(mus, kick(), tq, 0.9 if q in (0, 2) else 0.0)
            if q in (1, 3) and full: add(mus, snare(), tq)
            add(mus, hat(), tq + b / 2, 0.8); add(mus, hat(q == 3), tq, 0.5)
        for m, off in riff:
            tt = t + off * b
            if tt < t1: add(mus, slap(m + shift + (2 if bar % 4 == 3 else 0), b * 0.45), tt)
        if brass_on and full and bar % 2 == 1:
            for k, o in enumerate((2.5, 3.0)):
                if t + o * b < t1: add(mus, brass([64 + shift, 67 + shift, 71 + shift], b * 0.4), t + o * b)
        t += 4 * b; bar += 1
def boom(t, g=1.0):
    n = int(0.9 * SR); tt = np.arange(n) / SR; f = 40 + 90 * np.exp(-tt / 0.07)
    add(mus, g * 0.8 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.3), t); add(mus, noise(0.5, 0.4 * g, 0.1), t)
def whoosh(t, d=0.4, g=0.3):
    n = int(d * SR); x = np.convolve(rng.uniform(-1, 1, n), np.ones(8) / 8, "same"); add(mus, g * x * np.sin(np.linspace(0, np.pi, n)) ** 2, t)
def menace_sfx(t, d=2.0):  # low rumbling "gogogo"
    n = int(d * SR); tt = np.arange(n) / SR
    x = np.sin(2 * np.pi * 55 * tt) * (0.6 + 0.4 * np.sin(2 * np.pi * 8 * tt)) + 0.3 * np.convolve(rng.uniform(-1, 1, n), np.ones(40) / 40, "same")
    add(mus, 0.35 * x * np.minimum(1, tt / 0.2) * np.minimum(1, (d - tt) / 0.3), t)
def ping(t, f=1760, g=0.15):
    n = int(0.4 * SR); tt = np.arange(n) / SR; add(mus, g * np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.12), t)
# ---- arrangement
t_temps, t_celui, t_diver = at("temps"), at("celui"), at("diver")
# intro: ticking clock, then freeze
tk = 0.3
while tk < t_temps: add(mus, noise(0.03, 0.2, 0.006), tk); tk += 0.5
n = int(1.0 * SR); tt = np.arange(n) / SR; add(mus, 0.3 * rng.uniform(-1, 1, n) * (tt / 1.0) ** 2, t_temps - 1.0)  # reverse swell
add(mus, 0.4 * np.sin(2 * np.pi * 70 * np.arange(int(1.2 * SR)) / SR) * np.exp(-np.arange(int(1.2 * SR)) / SR / 0.5), t_temps)  # "dooon"
boom(t_diver, 1.2); whoosh(t_diver - 0.3); menace_sfx(t_diver, 3.0)
groove(t_diver + 0.1, C[2], full=True)
# S2 details
for w, a in (("bizarre", 0), ("bizarre", 13), ("meurtrier", 0)): boom(at(w, a), 0.6)
boom(at("démonte"), 1.3); whoosh(at("démonte"), 0.6, 0.4)
# S3
groove(C[2], C[3], full=False, shift=0); menace_sfx(at("plongeur"), 2.5)
for i in range(5): ping(at("partout") - 0.25 + i * 0.1, 1320 + 110 * i, 0.1)
# S4
groove(C[3], C[4], full=True, shift=2)
boom(at("poing"), 1.0); boom(at("exploser"), 1.6); whoosh(at("poing") - 0.2)
# S5: dive splash + gears
groove(C[4], C[5], full=False, shift=-2)
tdv = at("plonge", 38); add(mus, noise(0.6, 0.45, 0.2), tdv); whoosh(tdv - 0.2, 0.5)
gt = at("modifier") - 0.4
while gt < C[5] - 0.2: add(mus, noise(0.02, 0.18, 0.004), gt); gt += 0.09
# S6: love pings then Jotaro menace
groove(C[5], at("jotaro") - 0.2, full=True)
for i in range(3): ping(at("épouser") - 0.2 + i * 0.12, 1568 + i * 200, 0.14)
boom(at("jotaro"), 1.3); menace_sfx(at("jotaro"), C[6] - at("jotaro"))
# S7 + S8
groove(C[6], T["total"] - 1.7, full=True, shift=0)
boom(C[6] + 0.35, 0.9); boom(at("créatifs"), 0.7)
tb = T["total"] - 1.6; add(mus, brass([52, 59, 64], 1.4, 0.2), tb)  # final stab, then freeze
for c in C[1:-1]: whoosh(c - 0.2, 0.35, 0.22)
# ---- mix
mus /= np.abs(mus).max() + 1e-9
ve = np.convolve(np.abs(vo), np.ones(int(0.1 * SR)) / int(0.1 * SR), "same")
duck = 1 - 0.45 * np.clip(ve / 0.05, 0, 1)
vo = vo / (np.abs(vo).max() + 1e-9) * 0.92
mix = np.tanh(1.15 * (vo + 0.3 * mus * duck)) / np.tanh(1.15)
sf.write(f"{R}/audio/mix.wav", mix.astype(np.float32), SR)
sf.write(f"{R}/audio/vo-only.wav", (np.tanh(1.15 * vo) / np.tanh(1.15)).astype(np.float32), SR)
print("mix ok")
