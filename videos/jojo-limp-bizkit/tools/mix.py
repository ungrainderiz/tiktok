"""Original dark nu-metal groove (no copyrighted music) + ElevenLabs-generated JoJo-style SFX, ducked under the voiceover."""
import json, sys, io, subprocess, numpy as np, soundfile as sf
R = sys.argv[1]; SR = 44100
T = json.load(open(f"{R}/timing.json")); C = T["cuts"]; OFF = T["off"]; TOT = T["total"]; N = int((TOT + 0.3) * SR)
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
    if i < 0: x = x[-i:]; i = 0
    if j > i: buf[i:j] += g * x[: j - i]
vo = np.zeros(N); add(vo, load(f"{R}/audio/vo.mp3"), OFF)
rng = np.random.default_rng(7)
nt = lambda m: 440 * 2 ** ((m - 69) / 12)
def lp(x, a):  # one-pole lowpass
    y = np.empty_like(x); s = 0.0
    for i in range(len(x)): s += a * (x[i] - s); y[i] = s
    return y
def noise(d, g, dec): n = int(d * SR); return g * rng.uniform(-1, 1, n) * np.exp(-np.arange(n) / SR / dec)

# ---------- instruments
def kick():
    n = int(0.3 * SR); t = np.arange(n) / SR; f = 45 + 140 * np.exp(-t / 0.03)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.14) + noise(0.3, 0.15, 0.004)
def snare():
    n = int(0.25 * SR); t = np.arange(n) / SR
    return noise(0.25, 0.7, 0.07) + 0.4 * np.sin(2 * np.pi * 185 * t) * np.exp(-t / 0.05)
def hat(): return noise(0.05, 0.22, 0.012)
GT = {}
def chug(m, d, mute=True):  # distorted drop-D guitar, two detuned saws
    key = (m, round(d, 3), mute)
    if key not in GT:
        n = int(d * SR); t = np.arange(n) / SR; x = np.zeros(n)
        for det in (0.995, 1.0, 1.006): x += 2 * ((t * nt(m) * det) % 1) - 1
        x += 0.6 * (2 * ((t * nt(m + 12) * 1.003) % 1) - 1)
        x = np.tanh(5 * x / 3); x = lp(x, 0.18 if mute else 0.35)
        env = np.minimum(1, t / 0.003) * (np.exp(-t / (0.09 if mute else d * 0.6)))
        GT[key] = 0.5 * x * env
    return GT[key]
def drone(d, m=26, g=0.35):
    n = int(d * SR); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * nt(m) * t) + 0.5 * np.sin(2 * np.pi * nt(m + 7) * t * 1.002) + 0.3 * np.sin(2 * np.pi * nt(m + 1) * t)  # dissonant b2
    e = np.minimum(1, t / 0.8) * np.minimum(1, (d - t) / 0.6)
    return g * x * e * (0.75 + 0.25 * np.sin(2 * np.pi * 5.5 * t))
def strings(ms, d, g=0.12):  # horror tremolo cluster
    n = int(d * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for m in ms: x += 2 * ((t * nt(m) * (1 + 0.003 * rng.standard_normal())) % 1) - 1
    x = lp(x / len(ms), 0.08) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 12 * t)))
    return g * x * np.minimum(1, t / 0.3) * np.minimum(1, (d - t) / 0.3)

mus = np.zeros(N)
BPM = 100; b = 60 / BPM; s16 = b / 4
PAT = [1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0]
NOTES = [38, 38, 38, 38, 38, 38, 41, 41, 38, 38, 38, 38, 38, 44, 44, 43]
def groove(t0, t1, half=False, heavy=1.0, gtr=True, drums=True):
    t = t0; bar = 0
    while t < t1 - 1e-6:
        for k in range(16):
            tk = t + k * s16
            if tk >= t1: break
            if gtr and PAT[k]: add(mus, chug(NOTES[k] + (0 if bar % 4 < 3 else 3), s16 * 0.95), tk, heavy)
            if not drums: continue
            if PAT[k] and k % 4 != 2: add(mus, kick(), tk, 0.9)
            if (k == 8 if half else k in (4, 12)): add(mus, snare(), tk, 0.8)
            if k % 2 == 0: add(mus, hat(), tk, 0.7)
        if gtr and bar % 4 == 3: add(mus, chug(38, b * 1.2, mute=False), t + 3 * b, 0.7 * heavy)
        t += 16 * s16; bar += 1

# ---------- SFX bank (ElevenLabs text-to-sound, see PUBLICATION.md)
fx = np.zeros(N)
def sfx(name, t, g=1.0):
    x = load(f"{R}/audio/sfx/{name}.mp3"); x = x / (np.abs(x).max() + 1e-9); add(fx, x, t, g)
def beep(t, d=0.12, f=1000, g=0.25):
    n = int(d * SR); tt = np.arange(n) / SR; add(fx, g * np.sin(2 * np.pi * f * tt) * np.minimum(1, (d - tt) / 0.01), t)
def whoosh(t, d=0.35, g=0.35):
    n = int(d * SR); x = np.convolve(rng.uniform(-1, 1, n), np.ones(10) / 10, "same"); add(fx, g * x * np.sin(np.linspace(0, np.pi, n)) ** 2, t)

# S1 cold open
add(mus, drone(6.9, 26, 0.3), 0.0)
sfx("rumble_2", 0.0, 0.8); sfx("door_0", 0.42, 1.0); sfx("impact_2", 0.6, 0.6); sfx("heart_3", 1.2, 0.7); sfx("reveal_0", 1.35, 0.55)
add(mus, strings([62, 63, 69, 70], 1.6, 0.18), at("film") - 0.1); sfx("glitch_3", at("horreur") + 0.3, 0.5)
tl1 = at("limp") - 0.08
sfx("impact_1", tl1 + 0.1, 1.0); sfx("reveal_2", tl1 + 0.1, 0.8); sfx("summon_0", tl1 - 0.5, 0.7)
groove(tl1 + 0.1, C[1] + 0.2, heavy=1.0)
sfx("summon_2", at("sports") - 0.3, 0.45)
# S2 dossier
groove(C[1] + 0.2, at("celui") - 0.1, half=True, heavy=0.8)
sfx("impact_3", C[1] + 0.3, 0.6); sfx("impact_0", at("gangster"), 0.7); whoosh(at("homme") - 0.1, 0.45)
sfx("glitch_0", at("whitesnake") + 0.2, 0.6); sfx("rumble_0", at("surtout"), 0.6)
add(mus, drone(at("son", 15.9) - at("celui") + 0.4, 25, 0.35), at("celui") - 0.1)
sfx("impact_2", at("tué"), 1.0); sfx("crack_2", at("tué") + 0.02, 0.5); sfx("heart_1", at("gloria"), 0.6)
# S3 resurrection
sfx("summon_3", C[2], 0.8); sfx("impact_1", C[2] + 0.35, 0.6)
groove(C[2] + 0.4, at("invisibles") - 0.05, half=True, heavy=0.75)
sfx("rumble_3", at("ramène"), 0.6); sfx("groan_0", at("morts"), 0.8); sfx("impact_3", at("morts") + 0.1, 0.5)
sfx("groan_2", at("humains"), 0.5); sfx("groan_1", at("animaux"), 0.5); sfx("impact_0", at("importe") - 0.1, 0.6)
sfx("groan_3", at("relèvent"), 0.7); sfx("rumble_1", at("relèvent") + 0.1, 0.5)
whoosh(at("détail") - 0.1, 0.4); sfx("heart_3", at("tout", 25), 0.5)
sfx("glitch_2", at("invisibles"), 0.8); sfx("reveal_2", at("invisibles") + 0.05, 0.6)
# S4 invisible army: music drops out, footsteps + heartbeat
add(mus, drone(C[4] - C[3] + 0.3, 24, 0.4), C[3])
for i in range(12): sfx(["steps_2", "steps_1", "steps_0"][i % 3], at("imagine") + 0.2 + i * 0.48, 0.5 + 0.04 * i)
sfx("heart_3", at("imagine") + 0.1, 0.6); sfx("heart_1", at("armée") + 0.6, 0.6); sfx("heart_2", at("entends") + 0.2, 0.7); sfx("heart_0", at("sens", 30) + 0.2, 0.8)
sfx("groan_0", at("armée"), 0.6); sfx("glitch_1", at("vois") - 0.1, 0.5); sfx("groan_1", at("entends"), 0.7); sfx("groan_3", at("sens", 30), 0.6)
tv = at("voir", 33)
for i in range(3): sfx(["impact_0", "impact_3", "impact_1"][i], tv + i * 0.12, 0.7)
# S5 death -> zombie -> head
sfx("reveal_3", at("fou") - 0.1, 0.8); sfx("impact_2", at("fou"), 0.6)
groove(at("fou") + 0.2, at("meurt") - 0.05, half=True, heavy=0.7, drums=True)
beep(at("quand") + 0.05); beep(at("quand") + 0.42)
beep(at("meurt"), 0.9, 1000, 0.28); sfx("impact_1", at("meurt"), 0.9)
sfx("summon_1", at("devient") - 0.1, 0.6); sfx("glitch_0", at("devient") + 0.1, 0.4); sfx("groan_2", at("zombie", 37), 0.6)
add(mus, drone(at("attaquer") - at("devient") + 0.3, 26, 0.35), at("devient"))
sfx("crack_1", at("détacher"), 0.6); sfx("crack_0", at("tête"), 1.0); sfx("impact_3", at("tête") + 0.02, 0.6)
for k in range(4): whoosh(at("attaquer") + k * 0.29, 0.3, 0.4)
groove(at("attaquer"), C[5] - 0.05, heavy=0.9)
sfx("impact_2", at("impossible"), 1.0); sfx("reveal_0", at("impossible") + 0.05, 0.6)
# S6 Ermes
sfx("summon_2", C[5] - 0.1, 0.6)
te = at("ermes", 43); sfx("impact_1", te, 1.0); sfx("reveal_2", te + 0.05, 0.9)
groove(te + 0.1, C[6] - 0.05, heavy=1.0)
for i in range(4): sfx("impact_0", at("ermes", 45) + i * 0.22, 0.35)
sfx("impact_2", at("venger"), 1.0); sfx("rumble_2", at("venger") + 0.1, 0.6)
# S7 nu metal fact: heaviest groove
sfx("impact_3", C[6] + 0.3, 0.8)
groove(C[6] + 0.3, C[7] - 0.05, heavy=1.15)
sfx("impact_1", at("metal"), 0.8); sfx("glitch_3", at("donné") - 0.15, 0.4); sfx("rumble_3", at("combats"), 0.5)
sfx("impact_2", at("glauques"), 1.0); sfx("groan_0", at("glauques") + 0.1, 0.6)
# S8 CTA + freeze
sfx("impact_3", at("abonne"), 0.8); beep(at("abonne") + 0.68, 0.08, 1800, 0.18)
tb = TOT - 2.3
groove(C[7] + 0.05, tb, half=True, heavy=0.8)
add(mus, chug(38, 0.9, mute=False), tb - 0.6, 0.9)
sfx("sting_0", tb, 1.0); sfx("impact_1", tb, 0.5)
for c in C[1:-1]: whoosh(c - 0.18, 0.3, 0.25)

# ---------- mix
mus /= np.abs(mus).max() + 1e-9; fx /= np.abs(fx).max() + 1e-9
ve = np.convolve(np.abs(vo), np.ones(int(0.12 * SR)) / int(0.12 * SR), "same")
act = np.clip(ve / 0.04, 0, 1)
vo = vo / (np.abs(vo).max() + 1e-9) * 0.92
mix = np.tanh(1.2 * (vo + 0.26 * mus * (1 - 0.5 * act) + 0.42 * fx * (1 - 0.3 * act))) / np.tanh(1.2)
sf.write(f"{R}/audio/mix.wav", mix.astype(np.float32), SR)
sf.write(f"{R}/audio/vo-sfx.wav", (np.tanh(1.2 * (vo + 0.42 * fx * (1 - 0.3 * act))) / np.tanh(1.2)).astype(np.float32), SR)
sf.write(f"{R}/audio/vo-only.wav", (np.tanh(1.2 * vo) / np.tanh(1.2)).astype(np.float32), SR)
print("mix ok", TOT)
