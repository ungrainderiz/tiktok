import json, sys
R = sys.argv[1]
T = json.load(open(f"{R}/timing.json")); h = open(f"{R}/tools/index.src.html").read()
h = h.replace("{{TOTAL}}", str(T["total"])).replace("{{TIMING}}", json.dumps(T, ensure_ascii=False, separators=(",", ":")))
for s in T["scenes"]: h = h.replace("{{S%s}}" % s["id"], str(s["start"])).replace("{{D%s}}" % s["id"], str(s["dur"]))
assert "{{" not in h; open(f"{R}/index.html", "w").write(h); print("built")
