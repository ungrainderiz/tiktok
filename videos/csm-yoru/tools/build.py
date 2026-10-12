import json, sys
R = sys.argv[1]; LEAD = 0.3
words = json.load(open(f"{R}/audio/words.json"))["words"]
ws = [w for w in words if w["type"] == "word"]
def at(txt, after=0):
    for w in ws:
        if w["start"] >= after and txt in w["text"].lower(): return round(w["start"] + LEAD, 3)
    raise SystemExit("missing " + txt)
TOTAL = round(ws[-1]["end"] + LEAD + 1.7, 3)
cuts = [0, at("dans") - 0.06, at("chapitre") - 0.06, at("problème") - 0.06, at("chapitre", 30) - 0.06, at("pour", 46) - 0.06, at("chapitre", 59) - 0.06, at("et", 65) - 0.06, at("abonne") - 0.06, TOTAL]
cuts = [round(c, 3) for c in cuts]
scenes = [{"start": cuts[i], "dur": round(cuts[i + 1] - cuts[i], 3)} for i in range(len(cuts) - 1)]
# extraits vidéo (clip, début, fin) en temps final
V = [("yoru_face", cuts[1], at("règle") - 0.2), ("yoru_street", at("règle") - 0.2, cuts[2]),
     ("gun_txt", at("pistolet") - 0.3, at("enfermé") + 0.3), ("gulf", at("enfermé") + 0.3, at("démon", 20) - 0.1), ("tank_txt", at("démon", 20) - 0.1, at("gardé")), ("elbrus", at("gardé"), cuts[3]),
     ("vault", at("volant") - 0.1, at("croire") - 0.1),
     ("statue_face", at("yoru", 33) - 0.05, at("arme", 35) - 0.05), ("statue_gun", at("arme", 35) - 0.05, at("quarante") - 0.05), ("hands2", at("quarante") - 0.05, at("tire") - 0.3),
     ("statue_aim", at("tire") - 0.3, at("balle") - 0.05), ("bang", at("balle") - 0.05, at("new") - 0.2),
     ("explode", cuts[6], cuts[6] + 4.3), ("ak", cuts[6] + 4.3, cuts[7]),
     ("yoru_eye", cuts[7], at("n'existe") - 0.2), ("yoru_street", cuts[8], TOTAL)]
vids = "\n".join(f'<video class="vid clip" id="v{i}" src="clips/{c}.mp4" data-start="{round(a,3)}" data-duration="{round(b-a,3)}" data-track-index="2" muted playsinline></video>' for i, (c, a, b) in enumerate(V))
M = json.load(open(f"{R}/sprites/map.json"))
path = " ".join(f"{round(x*900,1)},{round(y*900,1)}" for x, y in M["path"])
h = open(f"{R}/tools/index.src.html").read()
h = (h.replace("{{VIDEOS}}", vids).replace("{{TOTAL}}", str(TOTAL)).replace("{{LEAD}}", str(LEAD)).replace("{{PATH}}", path).replace("{{MAP}}", json.dumps(M))
      .replace("{{WORDS}}", json.dumps(words, ensure_ascii=False, separators=(",", ":"))).replace("{{SCENES}}", json.dumps(scenes)))
for i, s in enumerate(scenes, 1): h = h.replace("{{S%d}}" % i, str(s["start"])).replace("{{D%d}}" % i, str(s["dur"]))
assert "{{" not in h, h[h.index("{{"):h.index("{{") + 30]
open(f"{R}/index.html", "w").write(h)
json.dump({"total": TOTAL, "cuts": cuts, "lead": LEAD, "videos": V}, open(f"{R}/timing.json", "w"))
print("total", TOTAL, cuts)
