import json, sys
R = sys.argv[1]
T = json.load(open(f"{R}/audio/timeline.json")); words = T["words"]; TOTAL = T["total"]
def at(txt, after=0):
    for w in words:
        if w["start"] >= after and txt in w["text"].lower(): return w["start"]
    raise SystemExit("missing " + txt)
cuts = [0, at("fizz.") - 0.06, at("fizz", 9) - 0.06, at("avant") - 0.06, at("les", 26.8) - 0.06, at("anecdote") - 0.06, at("anecdote", 48) - 0.06,
        at("anecdote", 62) - 0.06, at("et", 70) - 0.06, at("alors") - 0.06, TOTAL]
cuts = [round(c, 3) for c in cuts]
scenes = [{"start": cuts[i], "dur": round(cuts[i + 1] - cuts[i], 3)} for i in range(len(cuts) - 1)]
h = open(f"{R}/tools/index.src.html").read()
h = (h.replace("{{TOTAL}}", str(TOTAL)).replace("{{WORDS}}", json.dumps(words, ensure_ascii=False, separators=(",", ":")))
      .replace("{{FIZZ}}", json.dumps(T["fizz"], ensure_ascii=False)).replace("{{SCENES}}", json.dumps(scenes)))
for i, s in enumerate(scenes, 1): h = h.replace("{{S%d}}" % i, str(s["start"])).replace("{{D%d}}" % i, str(s["dur"]))
assert "{{" not in h, h[h.index("{{"):h.index("{{") + 30]
open(f"{R}/index.html", "w").write(h)
json.dump({"total": TOTAL, "cuts": cuts}, open(f"{R}/timing.json", "w"))
print("total", TOTAL, cuts)
