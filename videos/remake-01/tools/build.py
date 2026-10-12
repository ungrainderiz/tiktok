import json, sys
R = sys.argv[1]; TOTAL = 86.0
words = json.load(open(f"{R}/src/words_fixed.json"))["words"]
ws = [w for w in words if w["type"] == "word"]
def at(txt, after=0):
    for w in ws:
        if w["start"] >= after and txt in w["text"].lower(): return w["start"]
    raise SystemExit("missing " + txt)
cuts = [0, at("koyuki", 7) - 0.06, at("ils") - 0.06, at("beck", 20) - 0.06, at("et", 30.8) - 0.04, at("là", 38.8) - 0.04, at("et", 43.9) - 0.04,
        at("des", 52) - 0.04, at("certains") - 0.06, at("et", 66.8) - 0.04, at("alors") - 0.04, at("tu", 81.5) - 0.06, TOTAL]
cuts = [round(c, 3) for c in cuts]
scenes = [{"start": cuts[i], "dur": round(cuts[i + 1] - cuts[i], 3)} for i in range(len(cuts) - 1)]
h = open(f"{R}/tools/index.src.html").read()
h = h.replace("{{TOTAL}}", str(TOTAL)).replace("{{WORDS}}", json.dumps(words, ensure_ascii=False, separators=(",", ":"))).replace("{{SCENES}}", json.dumps(scenes))
for i, s in enumerate(scenes, 1): h = h.replace("{{S%d}}" % i, str(s["start"])).replace("{{D%d}}" % i, str(s["dur"]))
assert "{{" not in h, h[h.index("{{"):h.index("{{") + 20]
open(f"{R}/index.html", "w").write(h)
json.dump({"total": TOTAL, "cuts": cuts}, open(f"{R}/timing.json", "w"))
print("total", TOTAL, cuts)
