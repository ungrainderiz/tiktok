import json, sys, numpy as np, soundfile as sf, subprocess, io
ROOT = sys.argv[1]; SR = 44100
T = json.load(open(f"{ROOT}/timing.json")); N = int((T["total"] + 0.2) * SR)
rng = np.random.default_rng(7)
S = {s["id"]: s["start"] for s in T["scenes"]}
def load(p):
    out = subprocess.run(["ffmpeg","-v","quiet","-i",p,"-ac","1","-ar",str(SR),"-f","wav","-"],capture_output=True).stdout
    return sf.read(io.BytesIO(out))[0]
def add(buf, x, t, g=1.0):
    i = int(t * SR); j = min(len(buf), i + len(x))
    if j > i: buf[i:j] += g * x[: j - i]
vo = np.zeros(N); 
for s in T["scenes"]: add(vo, load(f"{ROOT}/audio/vo-{s['id']}.wav"), s["vo"])
vo /= np.abs(vo).max() + 1e-9; vo *= 0.89
# ---- instruments
def env(n, a, d):
    t = np.arange(n) / SR; return np.minimum(1, t / a) * np.exp(-t / d)
def kick():
    n = int(.35*SR); t = np.arange(n)/SR; f = 45 + 110*np.exp(-t/.04)
    return np.sin(2*np.pi*np.cumsum(f)/SR) * env(n,.002,.12) * 1.0
def lp(x, a):
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)): acc += a*(x[i]-acc); y[i] = acc
    return y
def snare():
    n = int(.25*SR); t = np.arange(n)/SR
    nz = rng.standard_normal(n); nz = nz - lp(nz, .15)
    return (0.55*nz*env(n,.001,.07) + 0.4*np.sin(2*np.pi*190*t)*env(n,.001,.05))
def hat(open_=False):
    n = int((.25 if open_ else .06)*SR); nz = rng.standard_normal(n); nz = nz - lp(nz, .5)
    return 0.18*nz*env(n,.0005,.09 if open_ else .018)
def crash():
    n = int(1.8*SR); nz = rng.standard_normal(n); nz = nz - lp(nz, .35)
    return 0.22*nz*env(n,.001,.5)
def pluck(freq, dur, bright=.5):
    n = int(dur*SR); p = int(SR/freq); buf = rng.uniform(-1,1,p); out = np.empty(n)
    for i in range(n):
        out[i] = buf[i % p]; buf[i % p] = 0.996*(bright*buf[i % p] + (1-bright)*buf[(i+1) % p])
    return out
def chord(root, dur):  # distorted power chord
    x = pluck(root, dur, .5) + pluck(root*1.4983, dur, .5) + 0.7*pluck(root*2, dur, .5)
    x = np.tanh(4.5*x); x = lp(x, .35); return 0.32*x*np.minimum(1, np.linspace(6,0,len(x)))
def bassnote(f, dur):
    n = int(dur*SR); t = np.arange(n)/SR
    x = np.tanh(2.2*(np.sin(2*np.pi*f*t) + .35*np.sin(4*np.pi*f*t))) * env(n,.004,dur*.6)
    return 0.30*x
K, Sn, H, HO, C = kick(), snare(), hat(), hat(True), crash()
BPM = 132; b = 60/BPM
mus = np.zeros(N)
E2, A2, D3, B2, G2 = 82.41, 110.0, 146.83, 123.47, 98.0
def beat(t0, t1, full=True, bass=True, prog=(E2, E2, G2, A2)):
    t = t0; bar = 0
    while t < t1 - 1e-6:
        for q in range(4):
            tq = t + q*b
            if tq >= t1: break
            if q in (0,) or (full and q == 2) or (full and q == 3 and bar % 2): add(mus, K, tq if q != 3 else tq + b/2, .9)
            if full and q in (1, 3): add(mus, Sn, tq, .8)
            for e in (0, .5): add(mus, H if (q, e) != (3, .5) else HO, tq + e*b, 1.0 if e == 0 else .6)
            if bass and full:
                f = prog[bar % 4]
                for e in (0, .5): add(mus, bassnote(f, b*.48), tq + e*b)
        t += 4*b; bar += 1
def fill(t0):
    for i in range(4): add(mus, Sn, t0 + i*b/4, .5 + i*.12)
# hook: chord hit + hats only
add(mus, chord(E2, 2.2), 0.05, 1.0); add(mus, C, 0.05, .8)
for i in range(int(3.4/(b/2))): add(mus, H, 0.9 + i*b/2, .7)
fill(S["02"] - b)
add(mus, chord(E2, 1.2), S["02"], .8); add(mus, C, S["02"], .8)
beat(S["02"], S["03"], full=True, bass=True)
# grey life: heartbeat kick only
t = S["03"] + .2
while t < S["04"]: add(mus, K, t, .45); add(mus, K, t + .22, .3); t += 1.1
beat(S["04"], S["06"] - b, full=False, bass=False)
fill(S["06"] - b)
add(mus, chord(E2, 2.5), S["06"], 1.0); add(mus, C, S["06"], 1.0)
beat(S["06"], S["09"] - .05, full=True, bass=True, prog=(E2, G2, A2, D3/1))
# silence on 09: only a long chord tail at the end
add(mus, chord(A2, 3.0), S["09"] + 3.3, .55)
fill(S["10"] - b)
add(mus, C, S["10"], 1.0)
beat(S["10"], T["total"] - 1.6, full=True, bass=True, prog=(A2, G2, E2, E2))
add(mus, chord(E2, 2.0), T["total"] - 1.6, 1.0); add(mus, C, T["total"] - 1.6, .9)
# whooshes at cuts
for s in T["scenes"][1:]:
    n = int(.28*SR); nz = rng.standard_normal(n); nz = nz - lp(nz, .3)
    add(mus, 0.12*nz*np.sin(np.linspace(0, np.pi, n))**2, s["start"] - .14)
# duck music under voice
ve = np.abs(vo); win = int(.08*SR); ve = np.convolve(ve, np.ones(win)/win, "same")
duck = 1 - .45*np.clip(ve/0.08, 0, 1)
mus = mus/ (np.abs(mus).max()+1e-9)
mix = vo + 0.30*mus*duck
mix = np.tanh(1.1*mix)/np.tanh(1.1)
sf.write(f"{ROOT}/audio/mix.wav", mix.astype(np.float32), SR)
sf.write(f"{ROOT}/audio/music.wav", (0.30*mus).astype(np.float32), SR)
print("ok", len(mix)/SR)
