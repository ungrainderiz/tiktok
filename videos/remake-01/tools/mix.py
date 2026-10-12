"""Audio d'origine (voix + musique du TikTok) + bruitages ElevenLabs calés sur le montage."""
import json, sys, io, subprocess, numpy as np, soundfile as sf
R = sys.argv[1]; SR = 44100
T = json.load(open(f"{R}/timing.json")); C = T["cuts"]; TOT = T["total"]; N = int(TOT * SR)
WD = [w for w in json.load(open(f"{R}/src/words_fixed.json"))["words"] if w["type"] == "word"]
def at(txt, after=0):
    for w in WD:
        if w["start"] >= after and txt in w["text"].lower(): return w["start"]
    raise SystemExit("missing " + txt)
def load(p, ch=1):
    b = subprocess.run(["ffmpeg", "-v", "quiet", "-i", p, "-ac", str(ch), "-ar", str(SR), "-f", "wav", "-"], capture_output=True).stdout
    return sf.read(io.BytesIO(b))[0]
base = load(f"{R}/src/original.mp4", 2)[:N]; base = np.pad(base, ((0, N - len(base)), (0, 0)))
fx = np.zeros(N)
def sfx(name, t, g=1.0, maxd=None):
    x = load(f"{R}/audio/sfx/{name}.mp3")
    if maxd: n = int(maxd * SR); x = x[:n] * np.minimum(1, (n - np.arange(min(n, len(x)))) / (0.05 * SR))[: len(x[:n])]
    x = x / (np.abs(x).max() + 1e-9); i = int(t * SR); j = min(N, i + len(x))
    if j > i: fx[i:j] += g * x[: j - i]
# transitions
for k, c in enumerate(C[1:-1]): sfx(["whoosh_0", "whoosh_1", "whoosh_2"][k % 3], c - 0.15, 0.5, 0.8)
# S1
sfx("guitar_0", 0.08, 0.9); sfx("drums_1", 0.2, 0.5); sfx("pop_0", at("mongolian"), 0.35, 0.4); sfx("pop_0", at("chop"), 0.35, 0.4); sfx("pop_0", at("squad"), 0.35, 0.4)
sfx("stamp_0", at("incontournable"), 0.8); sfx("pop_1", at("musique"), 0.4, 0.5); sfx("pop_2", at("d'histoire"), 0.4, 0.5)
# S2
sfx("pop_3", at("ado"), 0.4, 0.5); sfx("scratch_0", at("bouleversée"), 0.6); sfx("stamp_1", at("rencontrant"), 0.8); sfx("guitar_2", at("ryusuke"), 0.7); sfx("pop_0", at("guitariste"), 0.4, 0.4)
# S3
sfx("whoosh_2", at("plongés") - 0.4, 0.6, 0.9); sfx("guitar_1", at("rock"), 0.8, 2.0); sfx("pop_1", at("hauts"), 0.4, 0.4); sfx("pop_2", at("bas", 16), 0.4, 0.4)
sfx("sparkle_0", at("ascension"), 0.4); sfx("pop_3", at("pas", 18.9), 0.4, 0.4); sfx("scratch_1", at("facile"), 0.6, 1.0)
# S4
sfx("stamp_2", at("réalisme"), 0.8)
for k, w in enumerate(["galères", "pression", "rivalités", "doute"]): sfx(["stamp_0", "stamp_1", "stamp_3", "stamp_0"][k], at(w), 0.6)
sfx("crowd_0", at("magie") - 0.2, 0.7); sfx("guitar_0", at("l'adrénaline"), 0.6); sfx("crowd_1", at("l'adrénaline") + 0.5, 0.6); sfx("pop_0", at("performances"), 0.35, 0.4)
# S5
sfx("drums_0", at("l'évolution"), 0.6); sfx("whoosh_0", at("incroyable") - 0.2, 0.5, 0.8); sfx("pop_1", at("d'ado"), 0.4, 0.4); sfx("pop_2", at("musicien"), 0.4, 0.4)
sfx("crowd_2", at("comme", 37), 0.6); sfx("crowd_3", at("était", 38), 0.5)
# S6
sfx("pop_3", at("narration"), 0.4, 0.4); sfx("pop_0", at("intensité"), 0.4, 0.4); sfx("scratch_2", at("manque"), 0.7); sfx("stamp_3", at("clé"), 0.6)
# S7
sfx("guitar_0", at("l'anime", 44), 0.9); sfx("drums_2", at("l'anime", 44) + 0.1, 0.5); sfx("scratch_3", at("ost") - 0.2, 0.5); sfx("stamp_0", at("inoubliable"), 0.6)
sfx("pop_1", at("dimension"), 0.4, 0.4); sfx("drums_3", at("groupe", 50), 0.6)
# S8
for w, a in (("moon", 0), ("slip", 0), ("face", 54)): sfx("pop_2", at(w, a), 0.35, 0.4)
sfx("stamp_2", at("gravés"), 0.8)
# S9
sfx("whoosh_1", at("temps", 59) - 0.4, 0.5, 0.8); sfx("stamp_1", at("authentique"), 0.9); sfx("guitar_2", at("rock", 62), 0.6)
for i in range(3): sfx("pop_0", at("semé") + i * 0.18, 0.35, 0.4)
sfx("drums_1", at("victoire"), 0.6); sfx("sparkle_2", at("mérite"), 0.4, 1.2)
# S10
sfx("stamp_3", at("l'anime", 67), 0.7); sfx("guitar_3", at("dispo"), 0.6); sfx("pop_3", at("d'excuses"), 0.4, 0.4); sfx("sparkle_0", at("pépite"), 0.7); sfx("sparkle_2", at("pépite") + 0.15, 0.4, 1.2)
# S11
for w, a in (("persévérance", 0), ("rock", 74), ("rêves", 0)): sfx("pop_1", at(w, a), 0.4, 0.4)
sfx("guitar_1", at("beck", 78), 0.9, 2.5); sfx("crowd_0", at("beck", 78) + 0.4, 0.6); sfx("stamp_0", at("must"), 0.9); sfx("crowd_3", at("must") + 0.2, 0.6)
# S12
sfx("pop_2", at("vu", 81), 0.45, 0.4); sfx("pop_3", at("lu", 82), 0.45, 0.4); sfx("sparkle_1", at("dis-moi"), 0.4); sfx("guitar_0", TOT - 1.8, 0.5)
# mix: SFX ducked a bit under the original voice
env = np.convolve(np.abs(base.mean(1)), np.ones(int(0.1 * SR)) / int(0.1 * SR), "same"); act = np.clip(env / 0.08, 0, 1)
fxd = 0.38 * fx * (1 - 0.35 * act)
mix = base + fxd[:, None]
mix = np.tanh(1.1 * mix) / np.tanh(1.1)
sf.write(f"{R}/audio/mix.wav", mix.astype(np.float32), SR)
print("mix ok", TOT)
