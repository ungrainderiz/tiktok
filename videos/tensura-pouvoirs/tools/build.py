import json, re, sys
R = sys.argv[1]; LEAD = 0.3
words = json.load(open(f"{R}/audio/words.json"))["words"]
ws = [w for w in words if w["type"] == "word"]
norm = lambda s: re.sub(r"[^\wà-ÿ'-]", "", s.lower())
def at(txt, after=0, exact=False):
    for w in ws:
        if w["start"] >= after and (norm(w["text"]) == txt if exact else txt in w["text"].lower()): return round(w["start"] + LEAD, 3)
    raise SystemExit("missing " + txt)
TOTAL = round(ws[-1]["end"] + LEAD + 1.9, 3)
cuts = [0, at("tout"), at("ensuite"), at("il", 29, True), at("maintenant"), at("un", 43, True), at("deux"), at("trois"), at("quatre"), at("cinq", 74), at("alors"), TOTAL]
cuts = [round(c - (0.06 if 0 < i < len(cuts) - 1 else 0), 3) for i, c in enumerate(cuts)]
scenes = [{"start": cuts[i], "dur": round(cuts[i + 1] - cuts[i], 3)} for i in range(len(cuts) - 1)]
# extraits Grand Sage (clip, début, fin) en temps final
V = [("evo", at("une", 77.5, True) - 0.05, at("quand", 80) - 0.05),
     ("harvest", at("par", 82.5, True) - 0.05, at("lors") - 0.05),
     ("raph", at("lors") - 0.05, at("et", 88.5, True) - 0.05),
     ("belz", at("et", 88.5, True) - 0.05, at("et", 91, True) - 0.05)]
vids = "\n".join(f'<video class="vid clip" id="v{i}" src="clips/{c}.mp4" data-start="{round(a,3)}" data-duration="{round(b-a,3)}" data-track-index="2" muted playsinline></video>' for i, (c, a, b) in enumerate(V))
h = open(f"{R}/tools/index.src.html").read()
h = (h.replace("{{VIDEOS}}", vids).replace("{{TOTAL}}", str(TOTAL)).replace("{{LEAD}}", str(LEAD))
      .replace("{{WORDS}}", json.dumps(words, ensure_ascii=False, separators=(",", ":"))).replace("{{SCENES}}", json.dumps(scenes))
      .replace("{{CLIPS}}", json.dumps([[c, round(a, 3), round(b, 3)] for c, a, b in V])))
for i, s in reversed(list(enumerate(scenes, 1))): h = h.replace("{{S%d}}" % i, str(s["start"])).replace("{{D%d}}" % i, str(s["dur"]))
assert "{{" not in h, h[h.index("{{"):h.index("{{") + 30]
open(f"{R}/index.html", "w").write(h)
json.dump({"total": TOTAL, "cuts": cuts, "lead": LEAD, "videos": V}, open(f"{R}/timing.json", "w"))
print("total", TOTAL, cuts)
