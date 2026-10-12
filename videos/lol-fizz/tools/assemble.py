"""Voix Mattyang + répliques officielles de Fizz insérées entre les phrases -> audio/voice.wav + audio/timeline.json"""
import json, io, subprocess, numpy as np, soundfile as sf
R = "."; SR = 44100; LEAD = 0.6  # petit silence d'ouverture
def load(p):
    b = subprocess.run(["ffmpeg", "-v", "quiet", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "wav", "-"], capture_output=True).stdout
    return sf.read(io.BytesIO(b))[0]
vo = load(f"{R}/audio/vo.mp3"); fz = load(f"{R}/src/fizz_voicelines.mp3")
words = [w for w in json.load(open(f"{R}/audio/words.json"))["words"] if w["type"] == "word"]
def fade(x, f=0.012):
    if len(x) < int(2 * f * SR): return x
    n = int(f * SR); e = np.ones(len(x)); e[:n] = np.linspace(0, 1, n); e[-n:] = np.linspace(1, 0, n); return x * e
# (point de coupe dans la voix, début/fin dans le fichier des répliques, texte)
INS = [(7.62, 53.80, 55.05, "Vous ne m'attraperez pas !"),
       (43.95, 0.15, 2.25, "Et plouf dans les dents !"),
       (52.99, 50.98, 53.52, "Sans crainte, j'ai toujours un bond d'avance."),
       (61.78, 49.45, 50.75, "Vous voulez voir un tour ?"),
       (66.84, 22.00, 23.30, "Ça sent le poisson."),
       (72.36, 87.55, 92.10, "Requin, c'est l'heure de manger. À table !")]
GAP = 0.22
rms = lambda x: np.sqrt(np.mean(x[np.abs(x) > 0.02] ** 2)) + 1e-9
RMS_VO = rms(vo)
segs = [np.zeros(int(LEAD * SR))]; prev = 0.0; shift = LEAD; out_words = []; lines = []; t_out = LEAD
cuts = [c for c, *_ in INS]
for k, (cut, a, b, txt) in enumerate(INS):
    seg = vo[int(prev * SR):int(cut * SR)]; segs.append(fade(seg))
    for w in words:
        if prev <= w["start"] < cut: out_words.append({"text": w["text"], "start": round(w["start"] - prev + t_out, 3), "end": round(w["end"] - prev + t_out, 3)})
    t_out += len(seg) / SR
    clip = fade(fz[int(a * SR):int(b * SR)]); clip *= min(4.0, RMS_VO / rms(clip))
    segs.append(np.zeros(int(GAP * SR))); t_out += GAP
    lines.append({"text": txt, "start": round(t_out, 3), "end": round(t_out + len(clip) / SR, 3)})
    segs.append(clip); t_out += len(clip) / SR
    segs.append(np.zeros(int(GAP * SR))); t_out += GAP
    prev = cut
tail = vo[int(prev * SR):]; segs.append(fade(tail)); t_out += len(tail) / SR
segs.append(np.zeros(int(1.2 * SR))); t_out += 1.2
y = np.concatenate(segs)
# niveau des répliques ~ niveau de la voix
sf.write(f"{R}/audio/voice.wav", (y / (np.abs(y).max() + 1e-9) * 0.95).astype(np.float32), SR)
json.dump({"words": out_words, "fizz": lines, "total": round(len(y) / SR, 3)}, open(f"{R}/audio/timeline.json", "w"), ensure_ascii=False, indent=0)
print("total", round(len(y) / SR, 2), "words", len(out_words)); [print(l) for l in lines]
