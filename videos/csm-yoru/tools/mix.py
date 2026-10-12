"""Voix Mattyang + OST « Kingdom of Predators » (HxH 2011, fournie par l'utilisateur) + bruitages ElevenLabs."""
import json, sys, io, subprocess, numpy as np, soundfile as sf
R = sys.argv[1]; SR = 44100; OST_OFF = 42.0
T = json.load(open(f"{R}/timing.json")); TOT = T["total"]; LEAD = T["lead"]; C = T["cuts"]; N = int(TOT * SR)
WD = [w for w in json.load(open(f"{R}/audio/words.json"))["words"] if w["type"] == "word"]
def at(txt, after=0):
    for w in WD:
        if w["start"] >= after and txt in w["text"].lower(): return w["start"] + LEAD
    raise SystemExit("missing " + txt)
def load(p, extra=()):
    b = subprocess.run(["ffmpeg", "-v", "quiet", *extra, "-i", p, "-ac", "1", "-ar", str(SR), "-f", "wav", "-"], capture_output=True).stdout
    return sf.read(io.BytesIO(b))[0]
def add(buf, x, t, g=1.0):
    i = int(t * SR); j = min(len(buf), i + len(x))
    if j > i: buf[i:j] += g * x[: j - i]
vo = np.zeros(N); add(vo, load(f"{R}/audio/vo.mp3"), LEAD)
ost = load(f"{R}/src/ost_kingdom_of_predators.mp3", ("-ss", str(OST_OFF)))[:N]; ost = np.pad(ost, (0, N - len(ost)))
t = np.arange(N) / SR
ost *= np.minimum(1, t / 0.25) * np.clip((TOT - t) / 1.5, 0, 1)
fx = np.zeros(N)
def sfx(name, tt, g=1.0, maxd=None, lib=False):
    p = f"../../library/sfx/{name}.mp3" if lib else f"{R}/audio/sfx/{name}.mp3"
    x = load(p)
    if maxd: x = x[: int(maxd * SR)]; x = x * np.minimum(1, (len(x) - np.arange(len(x))) / (0.06 * SR))
    x = x / (np.abs(x).max() + 1e-9); add(fx, x, tt, g)
for c in C[1:-1]: sfx("whoosh/whoosh_0", c - 0.15, 0.4, 0.7, lib=True)
# S1
for i in range(6): sfx("missile_" + str(i % 4), 0.6 + i * 0.25, 0.25, 0.8); sfx("impact/impact_" + str(i % 4), 1.4 + i * 0.25, 0.3, 0.8, lib=True)
sfx("impact/impact_2", at("troisième"), 1.0, lib=True); sfx("reveal_0" if False else "impact/reveal_2", at("troisième") + 0.05, 0.6, lib=True)
sfx("powerup_0", at("juste"), 0.8); sfx("powerup_2", at("forte"), 0.7)
# S2
sfx("impact/impact_1", at("yoru", 5), 0.8, lib=True); sfx("ambiance/glitch_3", at("yoru", 5) + 0.3, 0.4, lib=True); sfx("menace/rumble_2", at("démon"), 0.6, lib=True)
sfx("ambiance/heart_3" if False else "horreur/heart_3", at("peur"), 0.6, lib=True); sfx("powerup_1", at("puissante") - 0.3, 0.7)
# S3
sfx("ambiance/stamp_1", C[2] + 0.05, 0.7, lib=True); sfx("ambiance/glitch_0", C[2] + 0.35, 0.4, lib=True)
sfx("bang_1", at("pistolet") - 0.05, 0.8); sfx("ambiance/door_0", at("golfe"), 0.4, lib=True)
sfx("impact/impact_3", at("tank"), 0.9, lib=True); sfx("menace/rumble_3", at("gardé"), 0.6, lib=True)
# S4
sfx("ambiance/stamp_0", at("stratégiques"), 0.8, lib=True); sfx("radar_0", at("croire"), 0.5); sfx("ambiance/pop_1", at("chaque", 28), 0.4, 0.4, lib=True); sfx("ambiance/pop_2", at("l'autre"), 0.4, 0.4, lib=True); sfx("impact/impact_2", at("attaqué"), 0.8, lib=True)
# S5
sfx("ambiance/stamp_1", C[4] + 0.05, 0.7, lib=True); sfx("ambiance/glitch_3", at("dégénère"), 0.6, lib=True)
sfx("menace/rumble_0", at("statue"), 0.6, lib=True); sfx("impact/impact_1", at("géante"), 0.9, lib=True)
for i in range(6): sfx("ambiance/pop_0", at("quarante") + 0.15 + i * 0.3, 0.25, 0.3, lib=True)
sfx("horreur/crack_2", at("index"), 0.8, lib=True)
sfx("bang_0", at("balle") - 0.02, 1.0); sfx("bang_2", at("balle") + 0.05, 0.5)
sfx("missile_1", at("new") - 0.1, 0.5); sfx("radar_2", at("survolant"), 0.5)
# S6
sfx("radar_1", C[5] + 0.05, 0.6, 2.5); sfx("siren_0", at("missile"), 0.8); sfx("siren_1", at("missile") + 0.9, 0.6)
for k, tt in enumerate([at("ripostent") + 0.0, at("coup") - 0.1, at("coup", 52) - 0.1, at("l'escalade") - 0.4]):
    sfx("missile_" + str(k), tt, 0.7); sfx("impact/impact_" + str(k), tt + 0.6, 0.8, lib=True)
sfx("siren_3", at("l'escalade"), 0.6, 2.0)
for i in range(4): sfx("radar_3", at("l'escalade") + 0.35 + i * 0.35, 0.5)
sfx("ambiance/stamp_3", at("face", 54.5), 0.5, lib=True); sfx("powerup_3", at("recréer"), 0.5); sfx("nuke_3", at("nucléaire"), 1.0); sfx("nuke_1", at("nucléaire") + 0.3, 0.8)
# S7
sfx("ambiance/stamp_1", C[6] + 0.05, 0.7, lib=True); sfx("nuke_3", at("éclate") + 0.05, 0.9); sfx("impact/impact_2", at("l'urss", 63) + 0.1, 0.9, lib=True)
# S8
sfx("powerup_0", at("n'existe") - 0.2, 0.9); sfx("impact/impact_1", at("power"), 1.0, lib=True); sfx("impact/reveal_2", at("power") + 0.05, 0.7, lib=True); sfx("ambiance/glitch_3", at("up", 68) + 0.3, 0.5, lib=True)
# S9
sfx("ambiance/stamp_0", at("abonne"), 0.7, lib=True); sfx("whoosh/whoosh_1", at("génie") - 0.15, 0.4, 0.6, lib=True); sfx("whoosh/whoosh_2", at("catastrophe") - 0.2, 0.4, 0.6, lib=True); sfx("impact/impact_3", at("catastrophe") + 0.2, 0.7, lib=True)
# mix
ost /= np.abs(ost).max() + 1e-9; fx /= np.abs(fx).max() + 1e-9; vo = vo / (np.abs(vo).max() + 1e-9) * 0.92
ve = np.convolve(np.abs(vo), np.ones(int(0.12 * SR)) / int(0.12 * SR), "same"); act = np.clip(ve / 0.04, 0, 1)
mix = vo + 0.32 * ost * (1 - 0.5 * act) + 0.42 * fx * (1 - 0.25 * act)
mix = np.tanh(1.1 * mix) / np.tanh(1.1)
sf.write(f"{R}/audio/mix.wav", mix.astype(np.float32), SR)
sf.write(f"{R}/audio/vo-sfx.wav", (np.tanh(1.1 * (vo + 0.42 * fx * (1 - 0.25 * act))) / np.tanh(1.1)).astype(np.float32), SR)
print("mix ok", TOT)
