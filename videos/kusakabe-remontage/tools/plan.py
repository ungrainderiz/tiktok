#!/usr/bin/env python3
"""Plan de montage du remontage Kusakabe → tools/scenes/01-montage.src + transcript.json.

Montage très nerveux : un plan par groupe de mots (≈ 1,5 s), chaque plan entre en « whip », « slam » ou « zoom »,
fond flou de la même image, poussée de caméra continue dans la carte, mots-clés qui claquent en haut de l'écran.
Le minutage des mots vient du surlignage jaune des sous-titres de la vidéo d'origine (voir README de ce dossier).
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOTAL = 67.81

# ---------------------------------------------------------------- texte + minutage (début de chaque mot)
INTRO = [("Le", 0.0), ("jour", 0.28), ("où", 0.42), ("Kusakabe", 0.60), ("a", 1.18), ("choqué", 1.46), ("tout", 1.68),
         ("le", 1.94), ("monde", 2.00), ("avec", 2.22), ("la", 2.50), ("maîtrise…", 2.68)]
CHUNKS = [
    ("Dans l'univers de", [3.60, 3.77, 4.17]), ("Jujutsu Kaisen,", [4.37, 4.87]), ("tout le monde", [5.37, 5.57, 5.73]),
    ("connaissait Kusakabe", [5.90, 6.33]), ("comme un simple", [7.13, 7.23, 7.50]), ("exorciste de rang", [7.90, 8.53, 8.73]),
    ("1.", [8.93]), ("Quelqu'un de fiable,", [9.43, 9.70, 9.80]), ("respecté, mais loin", [10.23, 10.93, 11.17]),
    ("d'être une légende", [11.37, 11.57, 11.77]), ("vivante.", [12.13]), ("Pourtant, ce jour-là,", [12.53, 13.00, 13.27]),
    ("il s'est dressé", [13.63, 13.83, 14.03]), ("face à Sukuna,", [14.43, 14.63, 14.80]), ("le roi des", [15.30, 15.53, 15.70]),
    ("fléaux, sans trembler.", [15.83, 16.20, 16.53]), ("Alors que tous", [17.03, 17.27, 17.47]), ("les exorcistes", [17.63, 17.80]),
    ("tombaient un à", [18.50, 18.90, 19.57]), ("un sous la", [19.63, 19.70, 19.93]), ("puissance", [20.10]),
    ("écrasante de Sukuna,", [20.73, 21.33, 21.57]), ("Kusakabe est entré", [22.10, 22.70, 22.90]), ("en scène.", [23.13, 23.33]),
    ("Pas avec une", [23.57, 23.77, 24.00]), ("extension de territoire,", [24.27, 24.70, 24.80]), ("pas avec une", [25.33, 25.53, 25.80]),
    ("technique occulte dévastatrice.", [26.00, 26.50, 26.93]), ("Non, juste avec", [27.97, 28.37, 28.53]),
    ("sa maîtrise parfaite", [28.77, 28.93, 29.37]), ("du domaine simple,", [29.87, 29.93, 30.33]),
    ("son sang-froid et", [30.63, 30.90, 31.33]), ("sa détermination inébranlable.", [31.53, 31.70, 32.50]),
    ("Il a tenu", [33.23, 33.37, 33.50]), ("tête à Sukuna", [33.73, 33.90, 34.07]), ("bien plus longtemps", [34.47, 34.73, 34.87]),
    ("que", [35.27]), ("personne n'aurait jamais", [35.53, 35.83, 36.20]), ("osé l'imaginer.", [36.57, 36.77]),
    ("Il a esquivé,", [37.30, 37.47, 37.67]), ("contré,", [38.20]), ("frappé, pas pour", [38.83, 39.20, 39.40]),
    ("le vaincre, mais", [39.53, 39.63, 39.93]), ("pour protéger,", [40.17, 40.37]), ("pour ralentir l'inévitable.", [40.97, 41.20, 41.67]),
    ("Et pendant ce", [42.30, 42.47, 42.73]), ("combat,", [42.90]), ("même Sukuna a", [43.30, 43.60, 44.13]),
    ("reconnu, ne serait-ce", [44.33, 44.80, 44.97]), ("qu'un instant,", [45.40, 45.67]), ("que ce professeur", [46.13, 46.30, 46.43]),
    ("ordinaire", [47.13]), ("était un vrai", [47.77, 48.00, 48.20]), ("sorcier.", [48.45]), ("Ce qui est", [48.95, 49.05, 49.15]),
    ("intéressant avec cet", [49.30, 49.80, 50.10]), ("affrontement,", [50.20]), ("c'est que tout", [51.37, 51.50, 51.73]),
    ("le monde a", [51.93, 52.17, 52.33]), ("compris ce jour-là", [52.47, 52.77, 52.90]), ("que Kusakabe", [53.63, 53.97]),
    ("n'était pas un", [54.63, 55.13, 55.50]), ("prodige béni par", [55.77, 56.23, 56.63]), ("l'énergie maudite,", [56.77, 57.20]),
    ("ni un monstre", [57.73, 58.00, 58.17]), ("comme Satoru Gojo.", [58.73, 58.93, 59.37]), ("C'était juste un", [59.73, 60.20, 60.57]),
    ("homme prêt à", [60.80, 61.10, 61.33]), ("faire face à", [61.50, 61.63, 61.87]), ("l'enfer avec ce", [61.93, 62.37, 62.60]),
    ("qu'il avait.", [62.73, 62.93]), ("Et parfois,", [63.63, 63.97]), ("c'est exactement ce", [64.73, 65.20, 65.73]),
    ("qu'il faut pour", [65.87, 66.10, 66.27]), ("changer une bataille.", [66.40, 66.67, 66.77]),
]
LAST_END = 67.2  # fin de « bataille »

# ---------------------------------------------------------------- plans : (début, média, entrée, cadrage dans la carte)
# média : nom d'image (assets/images/plans/<nom>.jpg), « clip:<nom> » (assets/clips) ou « noir » (typo seule)
SHOTS = [
    (0.0, "fan-a", "none", "50% 50%"), (3.60, "clip:anime-ville", "whip", "50% 50%"), (5.37, "clip:anime-glitch", "slam", "50% 50%"),
    (7.13, "manga-voiture", "whip", "50% 30%"), (9.43, "clip:anime-face", "zoom", "50% 50%"), (12.53, "fan-comic", "slam", "30% 50%"),
    (14.43, "fan-comic", "whip", "85% 50%"), (15.83, "illus-duo", "slam", "50% 40%"), (17.63, "manga-noir", "whip", "50% 30%"),
    (19.63, "manga-rayon", "slam", "50% 60%"),
    (22.10, "noir", "none", ""), (23.57, "clip:anime-rouge", "slam", "50% 50%"), (24.27, "clip:anime-bouche", "whip", "50% 50%"),
    (25.33, "clip:anime-feu", "slam", "50% 50%"), (27.97, "manga-ecole", "zoom", "30% 30%"),
    (29.87, "manga-ecole", "whip", "50% 90%"), (30.63, "manga-tchac", "slam", "50% 80%"), (33.23, "manga-gang", "whip", "50% 40%"),
    (35.27, "manga-gang2", "zoom", "50% 60%"),
    (37.30, "fan-b", "whip", "50% 60%"), (38.20, "clip:contre", "slam", "50% 50%"), (38.83, "sukuna-orange", "slam", "50% 45%"),
    (40.97, "illus-duo", "whip", "90% 40%"), (42.30, "manga-haha", "zoom", "50% 30%"),
    (44.33, "manga-close", "whip", "60% 40%"), (46.13, "manga-action", "slam", "50% 40%"), (48.30, "clip:meme", "zoom", "50% 50%"),
    (51.10, "clip:anime-sombre", "whip", "50% 50%"), (52.47, "clip:anime-bleu", "slam", "50% 50%"),
    (54.63, "clip:anime-main", "whip", "50% 50%"), (55.77, "clip:anime-lumiere", "slam", "50% 50%"),
    (56.77, "clip:anime-yeux", "zoom", "50% 50%"), (57.73, "clip:anime-oeil", "slam", "50% 50%"),
    (58.73, "clip:anime-ombre", "whip", "50% 50%"),
    (59.73, "manga-atsuya", "whip", "50% 60%"), (61.93, "manga-atsuya2", "slam", "50% 70%"), (63.63, "portraits", "zoom", "50% 40%"),
    (64.73, "fan-a", "whip", "50% 50%"),
]
CLIP_LEN = {"anime-ville": 1.4, "anime-glitch": 1.9, "anime-face": 2.45, "anime-rouge": 0.75, "anime-bouche": 0.75,
            "anime-feu": 2.2, "contre": 1.05, "meme": 2.7, "anime-sombre": 1.45, "anime-bleu": 2.0, "anime-main": 1.3,
            "anime-lumiere": 1.25, "anime-yeux": 0.72, "anime-oeil": 1.18, "anime-ombre": 1.35}

# ---------------------------------------------------------------- mots qui claquent : (début, fin, texte, style, taille, y, effets)
# style : w blanc, y jaune, r rouge ; effets : « hit » (flash + secousse), « strike@t » (barré à t), « big » (centre écran)
SLAMS = [
    (0.05, 1.40, "le jour où", "w", 100, 180, ""), (0.60, 1.40, "kusakabe", "y", 190, 285, "hit"),
    (1.46, 3.45, "a choqué", "w", 120, 175, ""), (1.68, 3.45, "tout le monde", "y", 150, 310, "hit"),
    (4.37, 5.30, "jujutsu kaisen", "y", 140, 250, "hit"), (6.33, 7.05, "kusakabe", "w", 190, 230, "hit"),
    (8.93, 9.40, "rang 1", "y", 200, 230, "hit"), (10.23, 11.30, "respecté", "w", 150, 240, ""),
    (11.77, 12.50, "légende", "y", 170, 240, "strike@12.15"), (13.63, 14.40, "il s'est dressé", "w", 120, 260, "hit"),
    (14.80, 15.25, "sukuna", "r", 200, 230, "hit"), (15.30, 16.45, "le roi des", "w", 110, 180, ""),
    (15.83, 16.45, "fléaux", "r", 170, 300, "hit"), (16.53, 17.55, "sans trembler", "y", 140, 260, ""),
    (18.90, 19.60, "un à un", "w", 190, 240, "hit"), (20.73, 22.00, "écrasante", "r", 160, 250, "hit"),
    (22.10, 23.50, "kusakabe", "y", 230, 760, "hit big"), (22.70, 23.50, "est entré", "w", 120, 600, "big"),
    (23.13, 23.50, "en scène", "w", 150, 1000, "hit big"),
    (24.27, 25.30, "extension de territoire", "w", 92, 250, "strike@24.85"),
    (26.00, 27.90, "technique occulte", "w", 110, 250, "strike@26.95"),
    (27.97, 28.70, "non.", "r", 220, 210, "hit"), (29.37, 29.85, "maîtrise parfaite", "y", 110, 250, ""),
    (30.33, 30.60, "domaine simple", "y", 140, 240, "hit"), (30.90, 31.50, "sang-froid", "w", 170, 240, ""),
    (32.50, 33.20, "inébranlable", "y", 150, 250, "hit"), (33.73, 34.40, "tête à sukuna", "w", 120, 250, ""),
    (34.87, 35.25, "bien plus longtemps", "y", 100, 260, ""), (36.57, 37.25, "osé l'imaginer", "w", 120, 250, ""),
    (37.67, 38.15, "esquivé", "y", 190, 240, "hit"), (38.20, 38.80, "contré", "w", 190, 240, "hit"),
    (38.83, 39.50, "frappé", "r", 190, 240, "hit"), (39.63, 40.30, "vaincre", "w", 170, 250, "strike@39.93"),
    (40.37, 40.95, "protéger", "y", 170, 250, "hit"), (41.67, 42.25, "l'inévitable", "w", 140, 250, ""),
    (43.60, 44.30, "même sukuna", "r", 140, 250, "hit"), (45.67, 46.10, "qu'un instant", "y", 130, 250, ""),
    (47.13, 47.75, "ordinaire", "w", 160, 240, ""), (48.20, 48.95, "vrai sorcier", "y", 150, 250, "hit"),
    (49.30, 50.15, "intéressant", "w", 140, 240, ""), (50.20, 51.05, "affrontement", "y", 130, 250, "hit"),
    (52.90, 53.60, "ce jour-là", "w", 140, 240, ""), (53.97, 54.60, "kusakabe", "y", 190, 240, "hit"),
    (56.23, 56.75, "prodige", "y", 180, 240, "strike@56.5"), (57.20, 57.70, "énergie maudite", "r", 120, 250, ""),
    (58.17, 58.70, "monstre", "r", 190, 240, "hit"), (59.37, 59.72, "gojo", "w", 230, 220, "hit"),
    (60.80, 61.45, "un homme", "y", 200, 240, "hit"), (61.93, 62.70, "l'enfer", "r", 200, 240, "hit"),
    (63.97, 64.70, "parfois", "w", 160, 240, ""), (66.40, 67.35, "changer", "y", 190, 190, "hit"),
    (66.77, 67.35, "une bataille", "w", 150, 375, "hit"),
]

SCENES = [0.0, 7.13, 14.43, 22.10, 29.87, 37.30, 44.33, 51.10, 59.73]
ZOOM_RATE = 0.0167  # poussée de caméra dans la carte (par seconde) ; la fin rejoint pile le cadrage du début


def transcript():
    words = [(w, t) for w, t in INTRO]
    for text, ts in CHUNKS:
        ws = text.split()
        assert len(ws) == len(ts), text
        words += list(zip(ws, ts))
    out = []
    for i, (w, t) in enumerate(words):
        nxt = words[i + 1][1] if i + 1 < len(words) else LAST_END
        if w == "maîtrise…":
            nxt = 3.45
        out.append({"text": w, "type": "word", "start": round(t, 3), "end": round(max(t + 0.08, min(nxt - 0.02, t + 0.7)), 3)})
    json.dump({"words": out}, open(os.path.join(ROOT, "transcript.json"), "w"), ensure_ascii=False, indent=1)
    return len(out)


def scene_of(t):
    k = 0
    for i, s in enumerate(SCENES):
        if t >= s - 1e-6:
            k = i
    return k


def media_html(sid, j, media, pos):
    if media.startswith("clip:"):
        name = media[5:]
        poster = f"assets/images/plans/{name}-poster.jpg"
        inner = f'<video class="clip" src="assets/clips/{name}.mp4" data-start="__S{j}__" data-duration="__D{j}__" muted playsinline style="object-position:{pos}"></video>'
        return poster, inner
    img = f"assets/images/plans/{media}.jpg"
    return img, f'<img src="{img}" alt="" style="object-position:{pos}">'


def build():
    ends = [s[0] for s in SHOTS[1:]] + [TOTAL]
    blocks = []
    for k, s0 in enumerate(SCENES):
        sid = f"s{k + 1:02d}"
        s1 = SCENES[k + 1] if k + 1 < len(SCENES) else TOTAL
        markup, js = [], []
        shots = [(i, sh) for i, sh in enumerate(SHOTS) if scene_of(sh[0]) == k]
        for j, (i, (t, media, entry, pos)) in enumerate(shots):
            lt, le = round(t - s0, 3), round(ends[i] - s0, 3)
            dur = round(le - lt, 3)
            pid = f"{sid}-p{j}"
            if media == "noir":
                markup.append(f'<div class="shot" id="{pid}"><div class="bd" style="background:#050506"></div></div>')
            else:
                bdimg, inner = media_html(sid, j, media, pos)
                if media.startswith("clip:"):
                    clen = CLIP_LEN[media[5:]]
                    inner = inner.replace(f"__S{j}__", str(lt)).replace(f"__D{j}__", str(round(min(dur, clen), 3)))
                markup.append(
                    f'<div class="shot" id="{pid}"><div class="bd" id="{pid}-bd" style="background-image:url({bdimg})"></div>'
                    f'<div class="persp"><div class="card" id="{pid}-c" style="background-image:url({bdimg})">'
                    f'<div class="inner" id="{pid}-in">{inner}</div><div class="shine"></div></div></div></div>')
            # visibilité : coupe sèche au début et à la fin du plan
            js.append(f'tl.set("#{pid}", {{ opacity: 0 }}, 0);' if lt > 0 else "")
            js.append(f'tl.set("#{pid}", {{ opacity: 1 }}, {lt});')
            if le < s1 - s0 - 1e-3:
                js.append(f'tl.set("#{pid}", {{ opacity: 0 }}, {le});')
            if media == "noir":
                continue
            # poussée continue (dans la carte) + fond qui respire ; le dernier plan rejoint le cadrage d'ouverture
            if i == len(SHOTS) - 1:
                z0 = round(1 - ZOOM_RATE * dur, 4)
                js.append(f'tl.fromTo("#{pid}-in", {{ scale: {z0} }}, {{ scale: 1, duration: {dur}, ease: "none" }}, {lt});')
            elif i == 0:
                js.append(f'tl.fromTo("#{pid}-in", {{ scale: 1 }}, {{ scale: {round(1 + ZOOM_RATE * dur, 4)}, duration: {dur}, ease: "none" }}, {lt});')
            else:
                js.append(f'tl.fromTo("#{pid}-in", {{ scale: 1.0 }}, {{ scale: 1.12, duration: {dur}, ease: "none" }}, {lt});')
                js.append(f'tl.fromTo("#{pid}-bd", {{ scale: 1.25 }}, {{ scale: 1.15, duration: {dur}, ease: "none" }}, {lt});')
            side = 1 if i % 2 else -1
            if entry == "whip":
                js.append(f'tl.fromTo("#{pid}-c", {{ x: {side * 1000}, rotationY: {side * -35}, filter: "blur(18px)" }}, '
                          f'{{ x: 0, rotationY: 0, filter: "blur(0px)", duration: 0.22, ease: "power3.out" }}, {lt});')
                js.append(f'tl.fromTo("#{pid}-bd", {{ x: {side * 300} }}, {{ x: 0, duration: 0.3, ease: "power3.out" }}, {lt});')
            elif entry == "slam":
                js.append(f'tl.fromTo("#{pid}-c", {{ scale: 1.5, rotation: {side * 4} }}, {{ scale: 1, rotation: 0, duration: 0.18, ease: "power4.in" }}, {lt});')
                js.append(f'flash({lt + 0.17}, 0.6);')
                js.append(f'shake("#{pid}-c", {lt + 0.18}, 0.25, 16, {i});')
            elif entry == "zoom":
                js.append(f'tl.fromTo("#{pid}-c", {{ scale: 0.45, z: -500, rotationX: 25 }}, {{ scale: 1, z: 0, rotationX: 0, duration: 0.3, ease: "back.out(1.6)" }}, {lt});')
        # mots qui claquent
        for n, (a, b, text, style, size, y, fx) in enumerate([x for x in SLAMS if scene_of(x[0]) == k]):
            tid = f"{sid}-t{n}"
            cls = {"w": "t", "y": "t yel", "r": "t red"}[style]
            markup.append(f'<div class="{cls} slam" id="{tid}" style="top:{y}px;font-size:{size}px">{text}</div>')
            la, lb = round(a - s0, 3), round(b - s0, 3)
            js.append(f'tl.fromTo("#{tid}", {{ scale: 2.4, opacity: 0, rotation: {(-1) ** n * 3} }}, {{ scale: 1, opacity: 1, rotation: 0, duration: 0.16, ease: "power4.in" }}, {la});')
            hold = round(lb - 0.1 - (la + 0.16) - 0.005, 3)
            if hold > 0.05:
                js.append(f'tl.to("#{tid}", {{ scale: 1.06, duration: {hold}, ease: "none" }}, {round(la + 0.16, 3)});')
            js.append(f'tl.to("#{tid}", {{ opacity: 0, scale: 0.85, duration: 0.1, ease: "power2.in" }}, {round(lb - 0.1, 3)});')
            if "hit" in fx:
                js.append(f'shake("#{tid}", {la + 0.16}, 0.22, 14, {n + 3});')
                if "big" not in fx:
                    js.append(f'flash({la + 0.15}, 0.35);')
            for f in fx.split():
                if f.startswith("strike@"):
                    ts = round(float(f[7:]) - s0, 3)
                    markup.append(f'<div class="strike" id="{tid}-x" style="top:{y + int(size * 0.45)}px;left:120px;width:840px"></div>')
                    js.append(f'strike("#{tid}-x", {ts}, 0.18);')
                    js.append(f'tl.to("#{tid}", {{ opacity: 0.45, duration: {round(min(0.15, lb - 0.1 - ts - 0.01), 3)} }}, {ts});')
                    js.append(f'tl.to("#{tid}-x", {{ opacity: 0, duration: 0.1 }}, {round(lb - 0.1, 3)});')
                    js.append(f'shake("#{tid}", {ts}, 0.2, 12, {n + 7});')
        markup.append(f'<div class="flash" id="{sid}-fl"></div><div class="vig"></div>')
        body = (f"@@@ {sid}\n@bg #050506\n" + "\n".join(markup) + "\n@@@js\n"
                f'const flash = (t, a) => tl.fromTo("#{sid}-fl", {{ opacity: a }}, {{ opacity: 0, duration: 0.18, ease: "power1.out", immediateRender: false }}, t);\n'
                f'gsap.set("#{sid}-fl", {{ opacity: 0 }});\n' + "\n".join(x for x in js if x) + "\n")
        blocks.append(body)
    open(os.path.join(ROOT, "tools", "scenes", "01-montage.src"), "w", encoding="utf-8").write("\n".join(blocks))
    return len(SHOTS), len(SLAMS)


if __name__ == "__main__":
    n = transcript()
    print(n, "mots ;", "%d plans, %d mots-clés" % build())
