import json, re, subprocess, sys, wave
ROOT = sys.argv[1]
LEAD, TAIL, FINAL_HOLD = 0.25, 0.45, 1.6
def toks(s):
    out = []
    for t in s.split():
        if re.fullmatch(r"[^\w]+", t) and out: out[-1] += " " + t if t in ":?!" else t
        else: out.append(t)
    return out
def dur(p):
    with wave.open(p) as w: return w.getnframes() / w.getframerate()
def voiced(p, d):
    r = subprocess.run(["ffmpeg","-hide_banner","-i",p,"-af","silencedetect=noise=-38dB:d=0.12","-f","null","-"],capture_output=True,text=True).stderr
    ss = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r)]
    se = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r)]
    segs, cur = [], 0.0
    for a, b in zip(ss, se + [d]*(len(ss)-len(se))):
        if a > cur + 0.02: segs.append([cur, a])
        cur = b
    if cur < d - 0.02: segs.append([cur, d])
    return segs
phon = dict(l.rstrip("\n").split("\t") for l in open(f"{ROOT}/audio/lines.tsv"))
disp = dict(l.rstrip("\n").split("\t") for l in open(f"{ROOT}/audio/display.tsv"))
scenes, t = [], 0.0
for k in sorted(phon):
    p = f"{ROOT}/audio/vo-{k}.wav"; d = dur(p)
    pt, dt = toks(phon[k]), toks(disp[k])
    assert len(pt) == len(dt), (k, pt, dt)
    segs = voiced(p, d)
    total_v = sum(b - a for a, b in segs)
    w = [len(re.sub(r"[^\w]", "", x)) + 1.5 for x in pt]
    W = sum(w)
    def at(v):  # voiced-time -> real time
        for a, b in segs:
            if v <= b - a: return a + v
            v -= b - a
        return segs[-1][1]
    words, acc = [], 0.0
    for i, x in enumerate(dt):
        s = at(acc / W * total_v); acc += w[i]; e = at(acc / W * total_v - 1e-4)
        words.append({"w": x, "s": round(t + LEAD + s, 3), "e": round(t + LEAD + e, 3)})
    sd = LEAD + d + TAIL + (FINAL_HOLD if k == max(phon) else 0)
    scenes.append({"id": k, "start": round(t, 3), "dur": round(sd, 3), "vo": round(t + LEAD, 3), "voDur": round(d, 3), "words": words})
    t += sd
json.dump({"total": round(t, 3), "scenes": scenes}, open(f"{ROOT}/timing.json", "w"), ensure_ascii=False, indent=1)
print("total", round(t, 2)); [print(s["id"], s["start"], s["dur"]) for s in scenes]
