import json, sys
R = sys.argv[1]; OFF = 2.2  # cold open before the voice starts
words = json.load(open(f"{R}/audio/words.json"))["words"]
ws = [w for w in words if w["type"] == "word"]
def at(txt, after=0):
    for w in ws:
        if w["start"] >= after and txt in w["text"].lower(): return w["start"] + OFF
    raise SystemExit("missing " + txt)
end_vo = ws[-1]["end"] + OFF
cuts = [0, at("maxx", 7.5) - 0.1, at("son", 15.9) - 0.1, at("imagine") - 0.1, at("et", 32.2) - 0.04, at("mais", 41) - 0.04, at("limp", 46) - 0.04, at("abonne") - 0.05, end_vo + 2.8]
cuts = [round(c, 3) for c in cuts]
scenes = [{"start": cuts[i], "dur": round(cuts[i + 1] - cuts[i], 3)} for i in range(len(cuts) - 1)]
T = cuts[-1]
h = "".join(open(f"{R}/tools/{f}").read() for f in ("head_body.html", "_generic.js", "scenes.js"))
open(f"{R}/tools/index.src.html", "w").write(h)
h = h.replace("{{TOTAL}}", str(T)).replace("{{OFF}}", str(OFF)).replace("{{WORDS}}", json.dumps(words, ensure_ascii=False, separators=(",", ":"))).replace("{{SCENES}}", json.dumps(scenes))
for i, s in enumerate(scenes, 1): h = h.replace("{{S%d}}" % i, str(s["start"])).replace("{{D%d}}" % i, str(s["dur"]))
assert "{{" not in h
open(f"{R}/index.html", "w").write(h)
json.dump({"total": T, "cuts": cuts, "off": OFF}, open(f"{R}/timing.json", "w"))
print("total", T, cuts)
