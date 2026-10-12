import json, sys
R = sys.argv[1]; OFF = 0.3
words = json.load(open(f"{R}/audio/words.json"))["words"]
ws = [w for w in words if w["type"] == "word"]
def at(txt, after=0):
    for w in ws:
        if w["start"] >= after and txt in w["text"].lower(): return w["start"] + OFF
    raise SystemExit("missing " + txt)
end_vo = ws[-1]["end"] + OFF
cuts = [0, at("son", 11) - 0.12, at("pendant") - 0.12, at("le", 31.5) - 0.1, at("dans", 39.9) - 0.1, at("mais", 47) - 0.08, at("abonne") - 0.05, end_vo + 1.6]
cuts = [round(c, 3) for c in cuts]
scenes = [{"start": cuts[i], "dur": round(cuts[i + 1] - cuts[i], 3)} for i in range(len(cuts) - 1)]
T = cuts[-1]
h = open(f"{R}/tools/index.src.html").read()
h = h.replace("{{TOTAL}}", str(T)).replace("{{OFF}}", str(OFF)).replace("{{WORDS}}", json.dumps(words, ensure_ascii=False, separators=(",", ":"))).replace("{{SCENES}}", json.dumps(scenes))
for i, s in enumerate(scenes, 1): h = h.replace("{{S%d}}" % i, str(s["start"])).replace("{{D%d}}" % i, str(s["dur"]))
assert "{{" not in h
open(f"{R}/index.html", "w").write(h)
json.dump({"total": T, "cuts": cuts, "off": OFF}, open(f"{R}/timing.json", "w"))
print("total", T, cuts)
