"""Voix Mattyang + musique (OST fournie si src/ost.* existe, sinon musique originale) + bruitages ElevenLabs.
Sorties : audio/mix.wav (musique originale, version sûre), audio/mix_ost.wav (avec l'OST si présente), audio/vo-sfx.wav."""
import glob, json, sys, io, subprocess, numpy as np, soundfile as sf
R = sys.argv[1]; SR = 44100
T = json.load(open(f"{R}/timing.json")); TOT = T["total"]; LEAD = T["lead"]; C = T["cuts"]; N = int(TOT * SR)
V = {c: (a, b) for c, a, b in T["videos"]}
WD = [w for w in json.load(open(f"{R}/audio/words.json"))["words"] if w["type"] == "word"]
def at(txt, after=0):
    for w in WD:
        if w["start"] >= after and txt in w["text"].lower(): return w["start"] + LEAD
    raise SystemExit("missing " + txt)
def load(p, extra=()):
    b = subprocess.run(["ffmpeg", "-v", "quiet", *extra, "-i", p, "-ac", "1", "-ar", str(SR), "-f", "wav", "-"], capture_output=True).stdout
    return sf.read(io.BytesIO(b))[0]
def add(buf, x, t, g=1.0):
    i = int(t * SR)
    if i < 0: x = x[-i:]; i = 0
    j = min(len(buf), i + len(x))
    if j > i: buf[i:j] += g * x[: j - i]
vo = np.zeros(N); add(vo, load(f"{R}/audio/vo.mp3"), LEAD)
t_all = np.arange(N) / SR

# ---------- musique originale : ambiance « explication » mystique (ré mineur pentatonique) ----------
rng = np.random.default_rng(5)
nt = lambda m: 440 * 2 ** ((m - 69) / 12)
def pluck(m, d=1.2, g=0.2):
    n = int(d * SR); t = np.arange(n) / SR; f = nt(m)
    x = np.sin(2 * np.pi * f * t) + 0.45 * np.sin(4 * np.pi * f * t) * np.exp(-t / 0.15) + 0.2 * np.sin(6 * np.pi * f * t) * np.exp(-t / 0.08)
    return g * x * np.minimum(1, t / 0.004) * np.exp(-t / 0.45)
def pad(t0, t1, ms, g=0.07):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for k, m in enumerate(ms): x += np.sin(2 * np.pi * nt(m) * t * (1 + 0.002 * k)) + 0.3 * np.sin(2 * np.pi * nt(m + 12) * t)
    return g * x * np.minimum(1, t / 0.8) * np.minimum(1, (t1 - t0 - t) / 0.6)
def noise(d, g, dec): n = int(d * SR); return g * rng.uniform(-1, 1, n) * np.exp(-np.arange(n) / SR / dec)
def kick(g=0.5):
    n = int(0.3 * SR); t = np.arange(n) / SR; return g * np.sin(2 * np.pi * (50 + 90 * np.exp(-t / 0.03)) * t) * np.exp(-t / 0.12)
mus = np.zeros(N)
BPM = 84; b = 60 / BPM
CH = [[50, 57, 62], [46, 53, 58], [48, 55, 60], [45, 52, 57]]          # Dm  Bb  C  Am
ARP = [62, 65, 69, 72, 69, 65, 67, 69, 74, 72, 69, 67, 65, 64, 62, 57]
def section(t0, t1, dens=1, drums=0, g=1.0, oct=0):
    bar = 0; t = t0
    while t < t1 - 0.05:
        c = CH[bar % 4]; add(mus, pad(t, min(t1, t + 4 * b), c, 0.05 * g), t)
        step = b / (2 if dens >= 2 else 1)
        for k in range(int(4 * b / step)):
            tt = t + k * step
            if tt >= t1: break
            add(mus, pluck(ARP[(bar * 8 + k) % len(ARP)] + oct, 1.0, 0.11 * g), tt)
            if drums and k % (2 if dens >= 2 else 1) == 0:
                q = k // (2 if dens >= 2 else 1)
                if q in (0, 2) or drums > 1: add(mus, kick(0.35 * g), tt)
                if q in (1, 3): add(mus, noise(0.15, 0.12 * g, 0.05), tt)
                if drums > 1: add(mus, noise(0.03, 0.05 * g, 0.01), tt + step / 2)
        t += 4 * b; bar += 1
section(0, C[2], dens=1, drums=0)
section(C[2], C[4], dens=1, drums=1)
section(C[4], C[9], dens=2, drums=1)
section(C[9], V["harvest"][0], dens=2, drums=2, g=1.1)
section(V["harvest"][0], C[10], dens=2, drums=2, g=1.25, oct=12)
section(C[10], TOT - 0.3, dens=1, drums=1, g=0.9)
mus *= np.clip((TOT - t_all) / 1.2, 0, 1)

# ---------- bruitages ----------
fx = np.zeros(N); L = "../../library/sfx"
def sfx(name, tt, g=1.0, maxd=None):
    x = load(f"{L}/{name}.mp3")
    if maxd: x = x[: int(maxd * SR)]; x = x * np.minimum(1, (len(x) - np.arange(len(x))) / (0.06 * SR))
    x = x / (np.abs(x).max() + 1e-9); add(fx, x, tt, g)
for c in C[1:-1]: sfx("whoosh/whoosh_0", c - 0.15, 0.4, 0.7)
# S1
sfx("whoosh/whoosh_2", 0.05, 0.4, 0.6); sfx("ambiance/pop_2", 0.45, 0.5, 0.4); sfx("impact/impact_2", at("système") + 0.1, 0.8); sfx("ambiance/pop_1", at("moi") - 0.05, 0.35, 0.4)
sfx("ambiance/pop_0", at("slime"), 0.4, 0.4); sfx("magie/notif_1", at("expliqué") - 0.1, 0.8)
# S2
sfx("impact/reveal_1", at("magicules") + 0.05, 0.7); sfx("ambiance/pop_3", at("mana"), 0.4, 0.4); sfx("ambiance/sparkle_0", at("l'énergie") - 0.1, 0.6)
sfx("magie/name_1", at("monstres"), 0.6); sfx("ambiance/poof_1", at("concentrée") + 0.2, 0.8); sfx("impact/impact_1", at("concentrée") + 0.2, 0.6)
sfx("magie/levelup_1", at("plus", 14.5), 0.6); sfx("magie/levelup_3", at("puissant"), 0.8)
# S3
sfx("impact/impact_3", at("l'aura") + 0.1, 0.8); sfx("magie/aura_0", at("l'enveloppe"), 0.9); sfx("magie/aura_2", at("l'enveloppe") + 1.0, 0.5)
sfx("whoosh/whoosh_1", at("frapper") - 0.1, 0.6, 0.6); sfx("impact/impact_0", at("frapper") + 0.1, 0.9)
sfx("menace/rumble_1", at("quand", 23.5) - 0.1, 0.7); sfx("magie/haki_1", at("libère"), 0.9); sfx("magie/haki_3", at("écraser"), 0.8); sfx("impact/impact_2", at("écraser") + 0.05, 0.6)
sfx("magie/haki_2", at("haki") + 0.05, 1.0); sfx("impact/reveal_2", at("haki") + 0.1, 0.7)
# S4
sfx("ambiance/stamp_0", at("nomination") + 0.05, 0.7); sfx("ambiance/pop_1", at("nom", 31) - 0.05, 0.45, 0.4); sfx("magie/name_2", at("transfère") - 0.1, 0.9)
sfx("magie/levelup_1", at("évoluer"), 1.0); sfx("impact/reveal_0", at("évoluer") + 0.02, 0.6); sfx("ambiance/pop_2", at("gobelins"), 0.4, 0.4); sfx("ambiance/pop_3", at("hobgobelins"), 0.45, 0.4)
# S5
sfx("ambiance/stamp_1", at("compétences", 40) + 0.05, 0.7); sfx("ambiance/pop_0", at("cinq", 41.5), 0.4, 0.4)
for k in range(5): sfx("whoosh/whoosh_%d" % (k % 3), at("cinq", 41.5) + k * 0.14 - 0.05, 0.25, 0.35)
sfx("magie/levelup_2", at("cinq", 41.5) + 0.8, 0.5)
# S6
sfx("ambiance/stamp_0", C[5] + 0.05, 0.7)
for k, w in enumerate(("liées", "à", "la")): sfx("ambiance/pop_%d" % k, at(w, 45.5) + k * 0.12, 0.4, 0.4)
sfx("horreur/crack_1", at("avec.", 46.5) - 0.1, 0.6, 0.6); sfx("magie/notif_0", at("avec.", 46.5) + 0.3, 0.8)
# S7
sfx("ambiance/stamp_2", C[6] + 0.05, 0.7); sfx("ambiance/pop_1", at("basiques") - 0.1, 0.4, 0.4)
for k in range(8): sfx("whoosh/whoosh_%d" % (k % 3), at("n'importe") + 0.1 + k * 0.5, 0.25, 0.3)
sfx("magie/notif_2", at("s'entraînant") + 0.25, 0.8)
# S8
sfx("ambiance/stamp_1", C[7] + 0.05, 0.7); sfx("ambiance/pop_2", at("rares"), 0.35, 0.4); sfx("ambiance/pop_3", at("puissantes"), 0.35, 0.4)
for k in range(8): sfx("whoosh/whoosh_%d" % (k % 3), at("entraînement", 57) + k * 0.22, 0.3, 0.25)
sfx("magie/levelup_0", at("évolution", 59), 0.9); sfx("ambiance/beam_1", at("perception"), 0.5); sfx("magie/notif_3", at("magique", 60) - 0.05, 0.7, 1.8)
# S9
sfx("ambiance/stamp_0", C[8] + 0.05, 0.7); sfx("impact/impact_1", at("désir") + 0.1, 0.7); sfx("impact/impact_3", at("volonté") + 0.1, 0.7); sfx("impact/impact_2", at("extrême") + 0.1, 0.9)
sfx("horreur/heart_1", at("souvent") + 0.2, 0.6, 1.2); sfx("horreur/crack_2", at("mort"), 0.8); sfx("magie/ultime_1", at("renaissance"), 0.8)
sfx("ambiance/pop_0", at("propres", 69), 0.4, 0.4); sfx("magie/notif_1", at("grand", 72) - 0.1, 0.8); sfx("magie/notif_0", at("prédateur") - 0.1, 0.8)
# S10
sfx("ambiance/stamp_1", C[9] + 0.05, 0.8); sfx("magie/ultime_3", at("sommet") + 0.05, 0.9)
sfx("magie/levelup_2", V["evo"][0], 0.5); sfx("ambiance/pop_1", at("unique", 78), 0.35, 0.4)
sfx("magie/aura_1", V["evo"][1], 0.8); sfx("menace/rumble_2", V["evo"][1] + 0.3, 0.6); sfx("magie/haki_0", at("immense"), 0.8)
sfx("magie/ultime_0", V["harvest"][0], 0.9); sfx("impact/reveal_3", V["harvest"][0] + 0.05, 0.6)
sfx("magie/ultime_3", V["raph"][0], 0.9); sfx("ambiance/pop_2", at("grand", 86), 0.35, 0.4); sfx("magie/levelup_3", at("raphaël"), 0.7)
sfx("magie/haki_1", V["belz"][0], 0.7); sfx("ambiance/glitch_2", V["belz"][0] + 0.1, 0.4); sfx("ambiance/pop_3", at("prédateur", 88), 0.35, 0.4)
sfx("whoosh/whoosh_1", at("ultime,", 91.5) - 0.3, 0.6, 0.5); sfx("impact/impact_2", at("ultime,", 91.5), 0.9); sfx("ambiance/glitch_1", at("ultime,", 91.5) + 0.1, 0.5)
sfx("ambiance/stamp_0", at("seule"), 0.5); sfx("whoosh/whoosh_2", at("autre", 93) + 0.1, 0.6, 0.5); sfx("impact/impact_3", at("autre", 93) + 0.4, 1.0); sfx("magie/haki_2", at("autre", 93) + 0.42, 0.7)
sfx("magie/ultime_2", at("résister"), 0.7)
# S11
sfx("ambiance/stamp_2", at("quelle") + 0.05, 0.7); sfx("ambiance/pop_0", at("voudrais") - 0.1, 0.4, 0.4); sfx("ambiance/pop_1", at("voudrais") + 0.05, 0.4, 0.4); sfx("ambiance/pop_2", at("avoir"), 0.4, 0.4)
sfx("ambiance/stamp_0", at("abonne") + 0.05, 0.7); sfx("magie/levelup_1", at("abonne") + 0.3, 0.5)

# ---------- mixage ----------
fx /= np.abs(fx).max() + 1e-9; vo = vo / (np.abs(vo).max() + 1e-9) * 0.92
ve = np.convolve(np.abs(vo), np.ones(int(0.12 * SR)) / int(0.12 * SR), "same"); act = np.clip(ve / 0.04, 0, 1)
def master(music, gm):
    music = music / (np.abs(music).max() + 1e-9)
    m = vo + gm * music * (1 - 0.5 * act) + 0.42 * fx * (1 - 0.25 * act)
    return (np.tanh(1.1 * m) / np.tanh(1.1)).astype(np.float32)
sf.write(f"{R}/audio/mix.wav", master(mus, 0.3), SR)
sf.write(f"{R}/audio/vo-sfx.wav", master(np.zeros(N), 0), SR)
ost = sorted(glob.glob(f"{R}/src/ost.*"))
if ost:
    o = load(ost[0])[:N]; o = np.pad(o, (0, N - len(o))); o *= np.minimum(1, t_all / 0.3) * np.clip((TOT - t_all) / 1.5, 0, 1)
    sf.write(f"{R}/audio/mix_ost.wav", master(o, 0.32), SR); print("ost", ost[0])
print("mix ok", TOT)
