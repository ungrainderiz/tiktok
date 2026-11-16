"""
Low-poly "coral reef dragon" reconstruction (Blender / bpy).

Run:  blender -b -P build_reef_dragon.py      (or: python build_reef_dragon.py with the bpy module)
Out:  reef_dragon.blend + renders/front.png, side.png, back.png

Conventions: dragon faces -Y, up +Z, +X is its LEFT side. 1 unit ~ 100 px of the side reference.
"""
import bpy, bmesh, math, random, os
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
RENDER_DIR = os.path.join(HERE, "renders")
os.makedirs(RENDER_DIR, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
SC = bpy.context.scene
random.seed(5)

# ----------------------------------------------------------------------------- colours
def _lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def C(h):
    h = h.lstrip("#")
    return tuple(_lin(int(h[i:i + 2], 16) / 255.0) for i in (0, 2, 4))


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def jit(col, amt=0.07, rnd=random):
    f = 1.0 + rnd.uniform(-amt, amt)
    return tuple(max(0.0, min(1.0, c * f)) for c in col)


def pick(pal, rnd=random, amt=0.05):
    return jit(rnd.choice(pal), amt, rnd)



# ----------------------------------------------------------------------------- materials
def _set(bsdf, names, val):
    for n in names:
        if n in bsdf.inputs:
            bsdf.inputs[n].default_value = val
            return


def mat_lowpoly(name, rough=0.85):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    a = nt.nodes.new("ShaderNodeAttribute")
    a.attribute_name = "Col"
    a.location = (-300, 200)
    nt.links.new(a.outputs["Color"], bsdf.inputs["Base Color"])
    _set(bsdf, ["Roughness"], rough)
    _set(bsdf, ["Specular IOR Level", "Specular"], 0.25)
    return m


def mat_glow(name, strength=1.6):
    m = mat_lowpoly(name, 0.4)
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    a = nt.nodes["Attribute"]
    for n in ("Emission Color", "Emission"):
        if n in bsdf.inputs:
            nt.links.new(a.outputs["Color"], bsdf.inputs[n])
            break
    _set(bsdf, ["Emission Strength"], strength)
    return m


def mat_bubble(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    _set(bsdf, ["Base Color"], (0.42, 0.68, 1.0, 1.0))
    _set(bsdf, ["Roughness"], 0.15)
    _set(bsdf, ["Alpha"], 0.45)
    for n in ("Emission Color", "Emission"):
        if n in bsdf.inputs:
            bsdf.inputs[n].default_value = (0.8, 0.9, 1.0, 1.0)
            break
    _set(bsdf, ["Emission Strength"], 0.0)
    m.blend_method = "BLEND" if hasattr(m, "blend_method") else None
    return m



# ----------------------------------------------------------------------------- mesh helpers
def build(name, V, F, FC, coll, mat, matrix=None, recalc=True):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in V], [], [list(f) for f in F])
    me.update()
    if recalc:
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(me)
        bm.free()
    attr = me.color_attributes.new("Col", "FLOAT_COLOR", "CORNER")
    for p in me.polygons:
        c = FC[p.index]
        for li in p.loop_indices:
            attr.data[li].color = (c[0], c[1], c[2], 1.0)
        p.use_smooth = False
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    if matrix is not None:
        ob.matrix_world = matrix
    return ob


def ico(sub, r=1.0):
    bm = bmesh.new()
    try:
        bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    except TypeError:
        bmesh.ops.create_icosphere(bm, subdivisions=sub, diameter=r)
    bm.verts.ensure_lookup_table()
    bm.verts.index_update()
    V = [v.co.copy() for v in bm.verts]
    F = [[v.index for v in f.verts] for f in bm.faces]
    bm.free()
    return V, F


def centroid(V, f):
    s = Vector((0, 0, 0))
    for i in f:
        s += V[i]
    return s / len(f)


def fnormal(V, f):
    a, b, c = V[f[0]], V[f[1]], V[f[2]]
    n = (b - a).cross(c - a)
    return n.normalized() if n.length > 1e-9 else Vector((0, 0, 1))


def axes_matrix(X, Y, Z, p):
    return Matrix(((X.x, Y.x, Z.x, p.x), (X.y, Y.y, Z.y, p.y), (X.z, Y.z, Z.z, p.z), (0, 0, 0, 1)))


def frame(d):
    d = d.normalized()
    up = Vector((0, 0, 1)) if abs(d.z) < 0.95 else Vector((1, 0, 0))
    u = d.cross(up).normalized()
    v = d.cross(u).normalized()
    return u, v


def add_prism(V, F, FC, p0, p1, r0, r1, col, n=6, rot=0.0, caps=True):
    u, v = frame(p1 - p0)
    b = len(V)
    for p, r in ((p0, r0), (p1, r1)):
        for k in range(n):
            a = rot + 2 * math.pi * k / n
            V.append(p + (u * math.cos(a) + v * math.sin(a)) * r)
    for k in range(n):
        k2 = (k + 1) % n
        F.append([b + k, b + k2, b + n + k2, b + n + k]); FC.append(col())
    if caps:
        F.append([b + k for k in range(n)][::-1]); FC.append(col())
        F.append([b + n + k for k in range(n)]); FC.append(col())


def add_ico(V, F, FC, c, r, col, sub=0, scale=(1, 1, 1), jitter=0.0, rnd=random):
    vs, fs = ico(sub, 1.0)
    b = len(V)
    for p in vs:
        q = Vector((p.x * scale[0], p.y * scale[1], p.z * scale[2])) * r
        if jitter:
            q += Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * jitter * r
        V.append(c + q)
    for f in fs:
        F.append([b + i for i in f]); FC.append(col())



def setup_world():
    w = bpy.data.worlds.new("World_Ocean")
    SC.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (*C("68C9F9"), 1)
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements[1].color = (*C("2F6DE2"), 1)
    bg_cam = nt.nodes.new("ShaderNodeBackground")
    bg_amb = nt.nodes.new("ShaderNodeBackground")
    bg_amb.inputs["Color"].default_value = (0.86, 0.93, 1.0, 1)
    bg_amb.inputs["Strength"].default_value = 0.92
    lp = nt.nodes.new("ShaderNodeLightPath")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(tc.outputs["Window"], sep.inputs[0])
    nt.links.new(sep.outputs["Y"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg_cam.inputs["Color"])
    add = nt.nodes.new("ShaderNodeMath")
    add.operation = "ADD"
    add.use_clamp = True
    nt.links.new(lp.outputs["Is Camera Ray"], add.inputs[0])
    nt.links.new(lp.outputs["Transparent Depth"], add.inputs[1])
    nt.links.new(add.outputs[0], mix.inputs["Fac"])
    nt.links.new(bg_amb.outputs[0], mix.inputs[1])
    nt.links.new(bg_cam.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])


def look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()



# ============================================================================= DRAGON
PAL = dict(
    body=[C("4A9BEA"), C("5AABF0"), C("3E8CE2"), C("6DB9F3")],
    back=[C("7CC6F4"), C("93D4F7"), C("68B8F0")],
    belly=[C("E9EEFB"), C("DCE4F7"), C("F4F7FD")],
    leg=[C("4594E6"), C("55A4EE"), C("3A86DE"), C("66B2F1")],
    head=[C("8FD3F6"), C("A8DFF9"), C("79C4F2"), C("6AB8EE")],
    ice=[C("7FD4F5"), C("A5E3F9"), C("5FC0F0"), C("C9EFFB")],
    lav=[C("B9B5F0"), C("A9A3EA"), C("C9C6F5")],
    bone=[C("93CFF6"), C("A9DAF9"), C("82C3F2"), C("BDE4FB")],
    claw=[C("F3EBD0"), C("E8DDB8"), C("FBF6E4")],
    membrane=[C("3FA9EE"), C("55B8F2"), C("6CC6F5"), C("369DE8"), C("86D2F8")],
    red=[C("EE4466"), C("F25A70"), C("E63A6E"), C("F56E80")],
    pink=[C("F0509A"), C("F564A8"), C("E63E8C"), C("F878B4")],
    purple=[C("A35BE6"), C("B06CEC"), C("9550DC"), C("BC7EF0")],
    orange=[C("F4A63C"), C("F7B74F"), C("F09632")],
    kelp=[C("3CB043"), C("55C94F"), C("2E9E3E"), C("47BB48")],
    kelp_light=[C("7FDB5A"), C("6CCF4F")],
)
MAT = dict(
    body=mat_lowpoly("M_Body_Blue"), belly=mat_lowpoly("M_Belly_White"), head=mat_lowpoly("M_Head_Ice"),
    ice=mat_lowpoly("M_Ice_Crystal", 0.5), bone=mat_lowpoly("M_Wing_Bone"), claw=mat_lowpoly("M_Claw_Cream", 0.6),
    membrane=mat_lowpoly("M_Wing_Membrane", 0.7), coral=mat_lowpoly("M_Coral"), kelp=mat_lowpoly("M_Kelp_Green"),
    eye_glow=mat_glow("M_Eye_Glow", 1.3),
)
ROOT = bpy.data.collections.new("REEF_DRAGON")
SC.collection.children.link(ROOT)
COLL = {}
for cname in ["HEAD", "EYES", "HORNS", "BODY", "BELLY_PLATES", "LEGS", "CLAWS", "WINGS", "TAIL_FIN", "CORAL", "KELP"]:
    c = bpy.data.collections.new(cname)
    ROOT.children.link(c)
    COLL[cname] = c
COLL["CAMERAS_LIGHTS"] = bpy.data.collections.new("CAMERAS_LIGHTS")
SC.collection.children.link(COLL["CAMERAS_LIGHTS"])
XAX = Vector((1, 0, 0))


def catmull(pts, sub):
    """Catmull-Rom resample of a list of equal-length tuples."""
    out = []
    n = len(pts)
    for i in range(n - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, n - 1)]
        for s in range(sub):
            t = s / sub
            out.append(tuple(0.5 * ((2 * b) + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t * t +
                                    (-a + 3 * b - 3 * c + d) * t ** 3) for a, b, c, d in zip(p0, p1, p2, p3)))
    out.append(tuple(pts[-1]))
    return out


def add_spike(V, F, FC, base, tip, r, col, n=4, belly=0.25, flat=1.0, rot=0.0, flat_u=1.0):
    """Elongated faceted crystal (bipyramid): base point -> ring -> tip."""
    u, v = frame(tip - base)
    mid = base + (tip - base) * belly
    b = len(V)
    V.append(base)
    for k in range(n):
        a = rot + 2 * math.pi * k / n
        V.append(mid + (u * math.cos(a) * flat_u + v * math.sin(a) * flat) * r)
    V.append(tip)
    for k in range(n):
        k2 = (k + 1) % n
        F.append([b, b + 1 + k2, b + 1 + k]); FC.append(col())
        F.append([b + 1 + k, b + 1 + k2, b + n + 1]); FC.append(col())


def loft(rings, n, colfn, rnd, side_ref=XAX, jitter=0.02):
    """rings: list of (center Vector, r_side, r_dorsal). colfn(sin_a, ring_idx)->colour. Returns V,F,FC."""
    V, F, FC, idx = [], [], [], []
    m = len(rings)
    for k, (c, rw, rh) in enumerate(rings):
        t = (rings[min(k + 1, m - 1)][0] - rings[max(k - 1, 0)][0]).normalized()
        dorsal = side_ref.cross(t).normalized()
        side = t.cross(dorsal).normalized()
        row = []
        for j in range(n):
            a = 2 * math.pi * (j + (k % 2) * 0.5) / n
            p = c + side * rw * math.cos(a) + dorsal * rh * math.sin(a)
            p += Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * jitter * max(rw, rh) * 2
            V.append(p); row.append(len(V) - 1)
        idx.append(row)
    for k in range(m - 1):
        a, b = idx[k], idx[k + 1]
        for j in range(n):
            j2 = (j + 1) % n
            ang = 2 * math.pi * (j + 0.75) / n
            for tri in ([a[j], a[j2], b[j2]], [a[j], b[j2], b[j]]):
                F.append(tri); FC.append(colfn(math.sin(ang), k))
    for row, c, flip in ((idx[0], rings[0][0], True), (idx[-1], rings[-1][0], False)):
        V.append(c); ci = len(V) - 1
        for j in range(n):
            tri = [row[j], row[(j + 1) % n], ci]
            F.append(tri[::-1] if flip else tri); FC.append(colfn(0.0, 0))
    return V, F, FC


def orient(p, up, hint, scale=1.0, flat=1.0):
    Z = up.normalized()
    X = hint - Z * hint.dot(Z)
    X = X.normalized() if X.length > 1e-5 else frame(Z)[0]
    Y = Z.cross(X)
    return axes_matrix(X * scale, Y * scale * flat, Z * scale, p)


def add_tube(V, F, FC, pts, radii, col, n=6):
    """Continuous faceted tube through pts (shared rings, no seams), blunt angular tip."""
    rings = []
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        u, v = frame(t)
        row = []
        for k in range(n):
            a = 2 * math.pi * (k + 0.5 * (i % 2)) / n
            V.append(p + (u * math.cos(a) + v * math.sin(a)) * radii[i]); row.append(len(V) - 1)
        rings.append(row)
    for i in range(len(pts) - 1):
        a, b = rings[i], rings[i + 1]
        for k in range(n):
            k2 = (k + 1) % n
            F.append([a[k], a[k2], b[k2]]); FC.append(col())
            F.append([a[k], b[k2], b[k]]); FC.append(col())
    V.append(pts[0]); c0 = len(V) - 1
    V.append(pts[-1] + (pts[-1] - pts[-2]).normalized() * radii[-1] * 0.7); c1 = len(V) - 1
    for k in range(n):
        k2 = (k + 1) % n
        F.append([rings[0][k2], rings[0][k], c0]); FC.append(col())
        F.append([rings[-1][k], rings[-1][k2], c1]); FC.append(col())


def make_coral(name, pal, H, r0, depth, seed, matrix, kids_p3=0.15, ang=(34, 58), bias=0.32, tip_pal=None):
    """Staghorn coral: bent, tapering limbs with side nubs; planar (local XZ) with a little depth."""
    rnd = random.Random(seed)
    V, F, FC = [], [], []
    base_col = lambda: pick(pal, rnd)
    tip_col = lambda: pick(tip_pal or pal, rnd)
    rotY = lambda v, a: Matrix.Rotation(math.radians(a), 3, "Y") @ v

    def grow(p, d, L, r, lvl):
        col = tip_col if lvl == depth else base_col
        d1 = rotY(d, rnd.uniform(-12, 12))
        mid = p + d1 * L * 0.5
        d2 = (rotY(d, rnd.uniform(-16, 16)) + Vector((0, rnd.uniform(-.12, .12), 0.12))).normalized()
        q = mid + d2 * L * 0.5
        add_tube(V, F, FC, [p, mid, q], [r, r * 0.93, r * 0.82], col)
        if lvl > 0 and rnd.random() < 0.55:                       # short side nub
            nd = (rotY(d2, rnd.choice((-1, 1)) * rnd.uniform(50, 75)) + Vector((0, 0, 0.2))).normalized()
            add_tube(V, F, FC, [mid, mid + nd * L * 0.30], [r * 0.62, r * 0.50], tip_col if lvl == depth else col)
        if lvl == depth:
            return
        k = 3 if rnd.random() < kids_p3 else 2
        angs = [rnd.uniform(*ang), -rnd.uniform(*ang)] + ([rnd.uniform(-8, 8)] if k == 3 else [])
        for a in angs:
            nd = rotY(d2, a)
            nd = Matrix.Rotation(math.radians(rnd.uniform(-10, 10)), 3, "X") @ nd
            nd = (nd + Vector((0, 0, bias))).normalized()
            grow(q - d2 * r * 0.4, nd, L * rnd.uniform(0.74, 0.95), r * 0.80, lvl + 1)

    grow(Vector((0, 0, -0.08)), Vector((rnd.uniform(-.1, .1), 0, 1)).normalized(), H * 0.34, r0, 0)
    return build(name, V, F, FC, COLL["CORAL"], MAT["coral"], matrix)


def add_leaf(V, F, FC, base, d, side, nrm, L, W, col, rnd, n=9):
    """Broad serrated leaf: alternating wide/narrow sections, raised midrib, pointed tip, slight curl."""
    rings = []
    for i in range(n):
        t = i / n
        hw = W * math.sin(math.pi * min(1.0, t * 0.92 + 0.07)) ** 0.7 * (1.0 if i % 2 else 0.60)
        c = base + d * (L * t) + nrm * (0.10 * L * t * t)
        th = 0.035 * (1 - 0.5 * t) + 0.01
        row = []
        for q in (c - side * hw, c + nrm * th, c + side * hw, c - nrm * th):
            V.append(q); row.append(len(V) - 1)
        rings.append(row)
    V.append(base + d * L + nrm * 0.10 * L); tip = len(V) - 1
    for i in range(n - 1):
        a, b = rings[i], rings[i + 1]
        for k in range(4):
            k2 = (k + 1) % 4
            F.append([a[k], a[k2], b[k2]]); FC.append(col())
            F.append([a[k], b[k2], b[k]]); FC.append(col())
    for k in range(4):
        F.append([rings[-1][k], rings[-1][(k + 1) % 4], tip]); FC.append(col())
    F.append(rings[0][::-1]); FC.append(col())


def make_kelp(name, H, blades, matrix, seed, wide=1.0):
    rnd = random.Random(seed)
    V, F, FC = [], [], []
    col = lambda: pick(PAL["kelp"] + PAL["kelp_light"], rnd)
    for b in range(blades):
        fan = math.radians((b - (blades - 1) / 2) * 26 + rnd.uniform(-5, 5))
        hh = H * (1.0 if b == blades // 2 else rnd.uniform(0.65, 0.9))
        d = Vector((math.sin(fan), 0, math.cos(fan)))
        side = Vector((math.cos(fan), 0, -math.sin(fan)))
        base = Vector(((b - (blades - 1) / 2) * 0.08, 0, -0.05))
        add_leaf(V, F, FC, base, d, side, Vector((0, 1, 0)), hh, (0.10 + 0.07 * H) * wide, col, rnd)
    return build(name, V, F, FC, COLL["KELP"], MAT["kelp"], matrix)


# ----------------------------------------------------------------------------- spine (neck + torso + tail)
SPINE_CTRL = [  # (Y, Z, half-width, half-height)
    (-1.62, 3.16, .17, .19), (-1.40, 3.04, .19, .22), (-1.17, 2.78, .21, .25), (-1.06, 2.45, .25, .30),
    (-0.96, 2.14, .33, .40), (-0.62, 1.96, .45, .52), (0.10, 1.82, .50, .54), (0.85, 1.64, .46, .48),
    (1.50, 1.47, .40, .42), (2.30, 1.26, .36, .38), (3.20, 1.08, .29, .31), (4.10, 0.94, .22, .24),
    (5.00, 0.84, .16, .17), (5.90, 0.78, .09, .10), (6.40, 0.76, .03, .03)]
SPINE = [(Vector((2.3 * max(0.0, (y - 1.2) / 5.2) ** 1.7, y, z)), rw, rh) for (y, z, rw, rh) in catmull(SPINE_CTRL, 2)]


def spine_frame(k):
    m = len(SPINE)
    t = (SPINE[min(k + 1, m - 1)][0] - SPINE[max(k - 1, 0)][0]).normalized()
    dorsal = XAX.cross(t).normalized()
    return t, dorsal


def build_body():
    rnd = random.Random(1)

    def col(sa, k):
        if sa < -0.88:
            return pick(PAL["belly"], rnd)
        if sa > 0.6 and rnd.random() < 0.6:
            return pick(PAL["back"], rnd)
        return pick(PAL["body"], rnd)

    V, F, FC = loft(SPINE, 8, col, rnd)
    build("Body_Spine_Neck_Torso_Tail", V, F, FC, COLL["BODY"], MAT["body"])

    # overlapping belly plates from throat to tail
    k = 1
    i = 0
    while k < len(SPINE) - 4:
        c, rw, rh = SPINE[k]
        t, dorsal = spine_frame(k)
        V, F, FC = [], [], []
        vs, fs = ico(1)
        w, ln, th = rw * (0.95 if rh < 0.40 else 0.62), max(0.16, rh * 0.46), rh * 0.24
        ctr = c - dorsal * rh * 0.93
        for p in vs:
            sx = p.x * w * (1 - 0.35 * max(0, p.y))        # chevron: narrower toward the tail side
            V.append(ctr + XAX * sx + t * (p.y * ln) - dorsal * (p.z * th + 0.25 * th * abs(p.x) * -1))
        for f in fs:
            FC.append(pick(PAL["belly"], rnd))
        build(f"Belly_Plate_{i:02d}", V, fs, FC, COLL["BELLY_PLATES"], MAT["belly"])
        i += 1
        k += 1 if rh > 0.3 else 2


# ----------------------------------------------------------------------------- legs
def build_legs():
    for side, sx in (("L", 1), ("R", -1)):
        rnd = random.Random(60 + sx)
        ctrl = [(0.50 * sx, 0.70, 1.62, .36), (0.62 * sx, 0.25, 1.28, .32), (0.66 * sx, -0.32, 0.98, .22),
                (0.66 * sx, 0.10, 0.68, .16), (0.66 * sx, 0.42, 0.44, .13), (0.66 * sx, 0.25, 0.25, .15),
                (0.66 * sx, 0.0, 0.15, .16)]
        rings = [(Vector((x, y, z)), r, r * 1.1) for (x, y, z, r) in catmull(ctrl, 2)]
        V, F, FC = loft(rings, 7, lambda sa, k: pick(PAL["leg"], rnd), rnd)
        add_ico(V, F, FC, Vector((0.62 * sx, 0.50, 1.42)), 1.0, lambda: pick(PAL["leg"] + PAL["body"][:2], rnd), 1,
                scale=(0.33, 0.48, 0.50), jitter=0.04, rnd=rnd)
        build(f"Leg_{side}", V, F, FC, COLL["LEGS"], MAT["body"])

        V, F, FC, CV, CF, CC = [], [], [], [], [], []
        foot = Vector((0.66 * sx, 0.0, 0.15))
        for ang in (-28, 0, 28):
            a = math.radians(ang)
            d = Vector((math.sin(a), -math.cos(a), 0))
            tip = foot + d * 0.34 + Vector((0, 0, -0.03))
            add_prism(V, F, FC, foot, tip, 0.10, 0.085, lambda: pick(PAL["leg"], rnd), 5)
            add_ico(V, F, FC, tip, 0.10, lambda: pick(PAL["leg"], rnd), 0, rnd=rnd)
            add_spike(CV, CF, CC, tip + Vector((0, 0, 0.03)), tip + d * 0.45 + Vector((0, 0, -0.12)), 0.10,
                      lambda: pick(PAL["claw"], rnd), n=4, belly=0.2)
        add_spike(CV, CF, CC, foot + Vector((0, 0.1, 0.05)), foot + Vector((0, 0.42, -0.1)), 0.07,
                  lambda: pick(PAL["claw"], rnd), n=4, belly=0.25)
        build(f"Foot_{side}_Toes", V, F, FC, COLL["LEGS"], MAT["body"])
        build(f"Foot_{side}_Claws", CV, CF, CC, COLL["CLAWS"], MAT["claw"])


# ----------------------------------------------------------------------------- head
HEAD_M = Matrix.Translation((0, -1.92, 3.26)) @ Matrix.Rotation(math.radians(14), 4, "X")
PAL["lav_coral"] = [C("C9A8F0"), C("D8BDF5"), C("B994EA")]
PAL["palate"] = [C("3B7ED8"), C("3270CC")]
PAL["gem"] = [C("F050A8"), C("E63E98"), C("F878C0")]


def ring_mesh(rings, back_c, front_tip, colfn):
    """Skin a list of equal-length vertex rings (hand-drawn cross-sections) into a closed faceted mesh."""
    V, F, FC, idx = [], [], [], []
    for r in rings:
        idx.append([len(V) + i for i in range(len(r))]); V += r
    n = len(rings[0])
    for k in range(len(rings) - 1):
        a, b = idx[k], idx[k + 1]
        for j in range(n):
            j2 = (j + 1) % n
            for tri in (([a[j], a[j2], b[j2]], [a[j], b[j2], b[j]]) if (j + k) % 2 else ([a[j], a[j2], b[j]], [a[j2], b[j2], b[j]])):
                F.append(tri); FC.append(colfn(k, j))
    V.append(back_c); bi = len(V) - 1
    V.append(front_tip); fi = len(V) - 1
    for j in range(n):
        j2 = (j + 1) % n
        F.append([idx[0][j2], idx[0][j], bi]); FC.append(colfn(0, j))
        F.append([idx[-1][j], idx[-1][j2], fi]); FC.append(colfn(len(rings) - 1, j))
    return V, F, FC


def build_head():
    """Hand-modelled wyvern head (head-local space: snout -> -Y, up -> +Z, ~1.25 long)."""
    rnd = random.Random(21)
    hp = lambda pal: pick(PAL[pal], rnd)

    # ---- upper skull + hooked beak: cross-sections from the nape to the beak
    #        y,    half-w, z_top, z_mouth
    UP = [(0.45, 0.20, 0.16, -0.10), (0.27, 0.32, 0.29, -0.11), (0.08, 0.31, 0.32, -0.09),
          (-0.10, 0.24, 0.23, -0.07), (-0.30, 0.17, 0.16, -0.06), (-0.47, 0.11, 0.09, -0.07),
          (-0.57, 0.06, 0.02, -0.12)]
    rings = []
    for (y, w, zt, zb) in UP:
        zm = zb + (zt - zb) * 0.45
        rings.append([Vector(q) for q in ((0, y, zt), (.55 * w, y, .88 * zt), (w, y, zm), (.92 * w, y, zb),
                                          (0, y, zb + 0.03), (-.92 * w, y, zb), (-w, y, zm), (-.55 * w, y, .88 * zt))])

    def ucol(k, j):
        if j in (3, 4):
            return hp("palate")
        if j in (2, 5):                                   # cheek band: white behind the eye, icy toward the beak
            return hp("belly") if k < 3 else hp("ice")
        if k >= 4:
            return pick(PAL["ice"][1:] + PAL["bone"][:2], rnd)   # pale beak
        return hp("head")

    V, F, FC = ring_mesh(rings, Vector((0, 0.55, 0.02)), Vector((0, -0.64, -0.24)), ucol)   # tip hooks downward
    skull = build("Head_Skull", V, F, FC, COLL["HEAD"], MAT["head"], HEAD_M)

    # ---- recessed almond eyes under the brow (boolean sockets)
    tree = BVHTree.FromPolygons(V, F)
    cutters = []
    for side, sx in (("L", 1), ("R", -1)):
        d = Vector((0.64 * sx, -0.70, 0.32)).normalized()
        hit, nrm, _, _ = tree.ray_cast(Vector((0, 0.08, 0.10)), d)
        if nrm.dot(d) < 0:
            nrm = -nrm
        Z = (nrm + d).normalized()
        slant = Vector((0, -1, -0.30))
        Xa = (slant - Z * slant.dot(Z)).normalized()
        Ya = Z.cross(Xa)
        M = HEAD_M @ axes_matrix(Xa, Ya, Z, hit)
        r1, r2, dep, n = 0.105, 0.09, 0.02, 4
        CV, CF, CC = [], [], []
        for (r, z) in ((r2, -dep), (r1, 0.0), (r1 * 1.8, 0.2)):
            for k in range(n):
                a = 2 * math.pi * k / n
                CV.append(Vector((r * 1.7 * math.cos(a), r * 0.75 * math.sin(a), z)))
        for ring in range(2):
            for k in range(n):
                k2 = (k + 1) % n
                CF.append([ring * n + k, ring * n + k2, (ring + 1) * n + k2, (ring + 1) * n + k])
                CC.append(jit(C("3F9BE6"), 0.08, rnd))
        CF.append(list(range(n))[::-1]); CC.append(C("1F4FB8"))
        CF.append([2 * n + k for k in range(n)]); CC.append(C("1F4FB8"))
        cut = build(f"_cut_{side}", CV, CF, CC, SC.collection, MAT["head"], M)
        cutters.append(cut)
        mod = skull.modifiers.new(f"Socket_{side}", "BOOLEAN")
        mod.operation = "DIFFERENCE"; mod.object = cut
        GV = [Vector((r2 * 1.65 * math.cos(2 * math.pi * k / n), r2 * 0.72 * math.sin(2 * math.pi * k / n), -dep + 0.004))
              for k in range(n)] + [Vector((0, 0, -dep + 0.016))]
        GF = [[k, (k + 1) % n, n] for k in range(n)]
        build(f"Eye_{side}_Glow", GV, GF, [jit(C("55E8FF"), 0.05, rnd) for _ in GF], COLL["EYES"], MAT["eye_glow"], M,
              recalc=False)
    dg = bpy.context.evaluated_depsgraph_get(); dg.update()
    new_me = bpy.data.meshes.new_from_object(skull.evaluated_get(dg))
    old = skull.data
    skull.modifiers.clear(); skull.data = new_me; bpy.data.meshes.remove(old)
    for pl in new_me.polygons:
        pl.use_smooth = False
    for c in cutters:
        me = c.data; bpy.data.objects.remove(c); bpy.data.meshes.remove(me)

    # ---- lower jaw (white), hinged open
    LO = [(0.40, 0.19, -0.11, -0.24), (0.12, 0.26, -0.12, -0.31), (-0.14, 0.18, -0.13, -0.28),
          (-0.34, 0.10, -0.14, -0.22)]
    hinge = Vector((0, 0.40, -0.10))
    Rj = Matrix.Rotation(math.radians(7), 3, "X")
    jr = lambda q: Rj @ (Vector(q) - hinge) + hinge
    rings = [[jr(q) for q in ((0, y, zt), (.6 * w, y, zt + 0.01), (w, y, (zt + zb) / 2), (.7 * w, y, zb),
                              (0, y, zb - 0.02), (-.7 * w, y, zb), (-w, y, (zt + zb) / 2), (-.6 * w, y, zt + 0.01))]
             for (y, w, zt, zb) in LO]
    V, F, FC = ring_mesh(rings, jr((0, 0.5, -0.15)), jr((0, -0.50, -0.11)),
                         lambda k, j: hp("palate") if j in (0, 7) and k < 3 else hp("belly"))
    build("Head_Jaw", V, F, FC, COLL["HEAD"], MAT["head"], HEAD_M)

    # ---- crystal pieces: (name, base, tip, radius, palette, thin-factor, collection)
    parts = []
    for side, sx in (("L", 1), ("R", -1)):
        parts += [
            (f"Horn_Crown_{side}", (0.12 * sx, 0.02, 0.24), (0.36 * sx, 0.78, 0.78), 0.19, "ice", 0.6),
            (f"Horn_Brow_{side}", (0.22 * sx, -0.04, 0.24), (0.42 * sx, 0.50, 0.52), 0.10, "ice", 0.7),
            (f"Crest_Back_{side}", (0.13 * sx, 0.28, 0.20), (0.22 * sx, 1.10, 0.52), 0.12, "ice", 0.45),
            (f"Crest_Low_{side}", (0.20 * sx, 0.34, 0.06), (0.30 * sx, 1.00, 0.20), 0.10, "bone", 0.45),
            (f"Fin_Cheek_{side}", (0.26 * sx, 0.14, 0.05), (0.90 * sx, 0.62, 0.32), 0.15, "lav", 0.35),
            (f"Plate_Cheek_{side}", (0.16 * sx, 0.00, -0.06), (0.68 * sx, 0.30, -0.10), 0.17, "belly", 0.3),
            (f"Fin_Jaw_{side}", (0.18 * sx, 0.20, -0.18), (0.46 * sx, 0.42, -0.44), 0.10, "belly", 0.4),
            (f"Fang_Up_{side}", (0.075 * sx, -0.42, -0.06), (0.075 * sx, -0.44, -0.20), 0.03, "claw", 1.0),
            (f"Fang_Low_{side}", (0.055 * sx, -0.36, -0.21), (0.055 * sx, -0.38, -0.09), 0.028, "claw", 1.0),
        ]
    parts += [("Crest_Back_Mid", (0, 0.32, 0.24), (0, 1.25, 0.44), 0.12, "ice", 0.4),
              ("Gem_Forehead", (0, -0.08, 0.26), (0, 0.10, 0.52), 0.09, "gem", 0.8)]
    for name, b, t, r, pal, thin in parts:
        V, F, FC = [], [], []
        add_spike(V, F, FC, Vector(b), Vector(t), r, lambda: pick(PAL[pal], rnd), n=5, belly=0.3 if pal != "gem" else 0.5,
                  flat=1.0, flat_u=thin)
        build(name, V, F, FC, COLL["HORNS"], MAT["claw" if pal == "claw" else "ice"], HEAD_M)

    # ---- reef crown (head-local, so it follows the head): antlers sweep up, out and back
    L = lambda M: HEAD_M @ M
    for side, sx in (("L", 1), ("R", -1)):
        make_coral(f"Antler_Red_{side}", PAL["red"], 2.0, 0.095, 2, 400 + sx,
                   L(orient(Vector((0.24 * sx, 0.26, 0.18)), Vector((0.95 * sx, 1.05, 1)), XAX)), kids_p3=0.3,
                   tip_pal=PAL["pink"] + PAL["purple"][:1])
        make_coral(f"Antler_Lavender_{side}", PAL["lav_coral"], 1.0, 0.065, 2, 410 + sx,
                   L(orient(Vector((0.08 * sx, 0.30, 0.20)), Vector((0.16 * sx, 0.80, 1)), XAX)), kids_p3=0.2)
        make_coral(f"Antler_Purple_{side}", PAL["purple"], 0.85, 0.065, 2, 420 + sx,
                   L(orient(Vector((0.24 * sx, 0.38, 0.10)), Vector((1.0 * sx, 0.75, 0.55)), Vector((0.4 * sx, 1, 0)))),
                   kids_p3=0.4, tip_pal=PAL["pink"])
        make_coral(f"Nape_Orange_{side}", PAL["orange"], 0.45, 0.05, 2, 425 + sx,
                   L(orient(Vector((0.20 * sx, 0.55, -0.02)), Vector((0.9 * sx, 0.6, -0.1)), Vector((0, 0, 1)))))
        for j, (up, H) in enumerate((((1.0 * sx, 0.30, 0.16), 1.15), ((1.0 * sx, 0.50, -0.10), 1.0),
                                     ((0.55 * sx, 1.0, 0.30), 0.8))):
            make_kelp(f"Frill_Leaf_{side}_{j}", H, 3,
                      L(orient(Vector((0.20 * sx, 0.42 + 0.05 * j, 0.06)), Vector(up), Vector((0, 1, 0.2)))), 430 + j + sx, wide=1.15)


# ----------------------------------------------------------------------------- wings
def bez(a, b, c, t):
    return a * (1 - t) ** 2 + b * 2 * t * (1 - t) + c * t * t


def build_wing(side, sx):
    rnd = random.Random(80 + sx)
    S = Vector((0.36 * sx, -0.25, 2.20))
    sw = math.radians(38)
    u = Vector((math.cos(sw) * sx, math.sin(sw), 0.0))
    v = Vector((0, -0.10, 1.0)); v = (v - u * v.dot(u)).normalized()
    nrm = u.cross(v) * sx                      # points to the front (-Y)

    def P(q, c=0.0):
        return S + u * q.x + v * q.y + nrm * c

    V2 = lambda a, b: Vector((a, b)) * 1.16
    W = V2(1.90, 1.72)
    fingers = [  # (control, tip)
        (V2(3.8, 2.10), V2(5.75, 1.10)),
        (V2(4.1, 0.85), V2(5.90, -0.80)),
        (V2(2.75, 0.65), V2(3.20, -0.78)),
        (V2(1.55, 0.60), V2(1.10, -0.62)),
        (V2(0.0, 0.0), V2(0.10, -0.80)),
    ]
    fpt = lambda i, r: bez(W, fingers[i][0], fingers[i][1], r)

    # membrane: one shared grid across the four panels
    NA, NR = 4, 5
    cols = (len(fingers) - 1) * NA
    V, F, FC, grid = [], [], [], []
    V.append(P(W)); wi = 0
    for c in range(cols + 1):
        i = min(c // NA, len(fingers) - 2)
        a = (c - i * NA) / NA
        col = []
        for rr in range(1, NR + 1):
            r = rr / NR
            q = fpt(i, r) * (1 - a) + fpt(i + 1, r) * a
            q = W + (q - W) * (1 - 0.24 * math.sin(math.pi * a) * r * r)     # scalloped trailing edge
            on_bone = (c % NA == 0)
            V.append(P(q, 0.0 if on_bone else rnd.uniform(-0.07, 0.07)))
            col.append(len(V) - 1)
        grid.append(col)
    mcol = lambda: pick(PAL["membrane"], rnd, 0.06)
    for c in range(cols):
        F.append([wi, grid[c][0], grid[c + 1][0]]); FC.append(mcol())
        for rr in range(NR - 1):
            a, b, c2, d = grid[c][rr], grid[c][rr + 1], grid[c + 1][rr + 1], grid[c + 1][rr]
            for tri in (([a, b, c2], [a, c2, d]) if (c + rr) % 2 else ([a, b, d], [b, c2, d])):
                F.append(tri); FC.append(mcol())
    build(f"Wing_{side}_Membrane", V, F, FC, COLL["WINGS"], MAT["membrane"], recalc=False)

    # bones (arm + fingers) and cream claws
    V, F, FC, CV, CF, CC = [], [], [], [], [], []
    bcol = lambda: pick(PAL["bone"], rnd)
    ccol = lambda: pick(PAL["claw"], rnd)
    # shoulder muscle + tapered arm (shoulder -> elbow bend -> wrist), blending from body blue to wing bone
    AV, AF, AC = [], [], []
    add_ico(AV, AF, AC, S + Vector((0.05 * sx, 0.05, -0.05)), 0.36, lambda: pick(PAL["body"], rnd), 1,
            scale=(1.0, 1.25, 0.95), jitter=0.05, rnd=rnd)
    elbow = W * 0.45 + V2(-0.22, 0.20)
    arm = [(P(bez(V2(0, 0), elbow, W, t)), r, r * 0.9) for t, r in
           ((0.0, .25), (0.2, .22), (0.4, .18), (0.6, .16), (0.8, .15), (1.0, .14))]
    aV, aF, aC = loft(arm, 6, lambda sa, k: pick(PAL["body"] if k < 1 else PAL["back"] if k < 2 else PAL["bone"], rnd),
                      rnd, side_ref=nrm, jitter=0.03)
    off = len(AV)
    AV += aV; AF += [[i + off for i in f] for f in aF]; AC += aC
    build(f"Wing_{side}_Shoulder_Arm", AV, AF, AC, COLL["WINGS"], MAT["body"])
    add_ico(V, F, FC, P(W), 0.22, bcol, 0, rnd=rnd)
    for i, (r0, r1) in enumerate(((0.21, 0.09), (0.16, 0.07), (0.16, 0.07), (0.15, 0.065))):
        seg = 4
        for s in range(seg):
            a, b = fpt(i, s / seg), fpt(i, (s + 1) / seg)
            ra, rb = r0 + (r1 - r0) * s / seg, r0 + (r1 - r0) * (s + 1) / seg
            add_prism(V, F, FC, P(a), P(b), ra, rb, bcol, 5, caps=(s == 0 or s == seg - 1))
            if s < seg - 1:
                add_ico(V, F, FC, P(b), rb * 1.08, bcol, 0, rnd=rnd)      # knuckle hides the seam
        tip = fpt(i, 1.0)
        d = (tip - fpt(i, 0.9)).normalized()
        add_spike(CV, CF, CC, P(tip - d * 0.15), P(tip + d * (0.75 if i < 2 else 0.6)), 0.10, ccol, n=4, belly=0.22)
    add_spike(CV, CF, CC, P(W), P(W + V2(0.15, 0.55)), 0.11, ccol, n=4, belly=0.25)       # thumb spike
    build(f"Wing_{side}_Bones", V, F, FC, COLL["WINGS"], MAT["bone"])
    build(f"Wing_{side}_Claws", CV, CF, CC, COLL["CLAWS"], MAT["claw"])

    # reef growing flat on the membrane (straddles it, so it shows on both faces)
    deco = [("Pink_Outer", "pink", (4.35, -0.05), 110, 2.0, 0.19), ("Purple_Outer", "purple", (4.9, -0.5), 50, 1.15, 0.115),
            ("Purple_Tip", "purple", (3.7, 1.1), 190, 1.0, 0.10), ("Pink_Inner", "pink", (2.1, -0.4), 80, 1.7, 0.165),
            ("Purple_Inner", "purple", (2.8, -0.45), 20, 0.85, 0.09), ("Orange_Outer", "orange", (3.95, -0.1), 250, 0.55, 0.07),
            ("Purple_Arm", "purple", (1.1, 0.15), 100, 0.95, 0.09)]
    for j, (nm, pal, (a, b), ang, H, r0) in enumerate(deco):
        g = u * math.cos(math.radians(ang)) + v * math.sin(math.radians(ang))
        make_coral(f"Wing_{side}_Coral_{nm}", PAL[pal], H, r0, 2, 300 + j + (0 if sx > 0 else 50),
                   orient(P(V2(a, b)), g, nrm.cross(g), 1.0, flat=0.55), kids_p3=0.35)
    for j, ((a, b), ang, H) in enumerate((((3.3, -0.5), 85, 1.3), ((4.9, 0.45), 60, 0.9), ((1.55, -0.45), 95, 1.0),
                                          ((2.7, 0.85), 40, 0.8))):
        g = u * math.cos(math.radians(ang)) + v * math.sin(math.radians(ang))
        make_kelp(f"Wing_{side}_Kelp_{j}", H, 3, orient(P(V2(a, b)), g, nrm.cross(g), 1.0, flat=1.0), 340 + j)


# ----------------------------------------------------------------------------- tail fin + reef on the body
def build_tail_fin():
    rnd = random.Random(90)
    V, F, FC = [], [], []
    col = lambda: pick(PAL["ice"], rnd)
    for k in range(len(SPINE)):
        c, rw, rh = SPINE[k]
        if c.y < 4.7:
            continue
        t, dorsal = spine_frame(k)
        f = (c.y - 4.7) / 1.7
        for sgn in (1, -1):
            for lat in (-0.25, 0.25):
                L = 0.55 + 0.75 * f + rnd.uniform(-0.1, 0.1)
                d = (t * 1.0 + dorsal * sgn * rnd.uniform(0.35, 0.6) + XAX * lat * rnd.uniform(0.6, 1.4)).normalized()
                add_spike(V, F, FC, c, c + d * (L * 0.95), 0.20, col, n=4, belly=0.4, flat=1.0, flat_u=0.35)
    end = SPINE[-1][0]
    add_spike(V, F, FC, end - Vector((0, 0.3, 0)), end + Vector((0.5, 1.2, 0.0)), 0.22, col, n=4, belly=0.4, flat=1.0, flat_u=0.35)
    build("Tail_Fin_Crystals", V, F, FC, COLL["TAIL_FIN"], MAT["ice"])


def build_reef():
    rnd = random.Random(100)
    for side, sx in (("L", 1), ("R", -1)):
        make_coral(f"Shoulder_Purple_{side}", PAL["purple"], 1.05, 0.085, 2, 450 + sx,
                   orient(Vector((0.50 * sx, -0.45, 2.45)), Vector((0.75 * sx, -0.1, 1)), XAX), kids_p3=0.4)
        make_coral(f"Shoulder_Pink_{side}", PAL["pink"], 0.6, 0.05, 2, 460 + sx,
                   orient(Vector((0.42 * sx, -0.75, 2.50)), Vector((0.9 * sx, -0.3, 0.6)), XAX))
    # dorsal reef: neck -> tail tip
    cyc = ["pink", "purple", "kelp", "red", "orange", "purple", "pink", "kelp"]
    k, j = 6, 0
    while k < len(SPINE) - 1:
        c, rw, rh = SPINE[k]
        t, dorsal = spine_frame(k)
        big = max(0.3, min(1.0, rh / 0.45))
        for lat in ((0,) if rh < 0.12 else (-0.5, 0.0, 0.5) if (j % 2 and rh > 0.3) else (-0.4, 0.4) if j % 2 else (0,)):
            kind = cyc[(j + (1 if lat > 0 else 2 if lat < 0 else 0)) % len(cyc)]
            up = (dorsal + XAX * lat * 0.9 + Vector((0, 0, 0.35))).normalized()
            p = c + (dorsal * math.cos(lat) + XAX * math.sin(lat)) * rh * 0.85
            th = rnd.uniform(0, math.pi)
            hint = XAX * math.cos(th) + t * math.sin(th)
            H = (0.55 + 0.40 * big) * rnd.uniform(0.8, 1.15)
            if c.y > 4.6:
                H *= 1.25
            if kind == "kelp":
                make_kelp(f"Dorsal_Kelp_{j:02d}_{int(lat > 0) + 2 * int(lat < 0)}", H * 0.9, 3, orient(p, up, hint), 500 + j)
            else:
                make_coral(f"Dorsal_Coral_{kind}_{j:02d}_{int(lat > 0) + 2 * int(lat < 0)}", PAL[kind], H, 0.052 * H / 0.6 + 0.012, 2,
                           520 + 3 * j + int(lat > 0) + 2 * int(lat < 0), orient(p, up, hint), kids_p3=0.3)
        j += 1
        k += 1


# ----------------------------------------------------------------------------- cameras / lights / render
def setup_lights_cameras():
    L = COLL["CAMERAS_LIGHTS"]
    for name, energy, ang, loc in (("Light_Key_Sun", 1.1, 30, (-5, -9, 10)), ("Light_Fill_Sun", 0.45, 60, (7, 6, 4)),
                                   ("Light_Back_Sun", 0.5, 60, (-3, 9, 6))):
        sun = bpy.data.lights.new(name, "SUN"); sun.energy = energy; sun.angle = math.radians(ang)
        so = bpy.data.objects.new(name, sun); L.objects.link(so); so.location = loc; look_at(so, (0, 0, 0))
    cams = {}
    el = math.radians(4)
    for name, d, tgt, scale, res in (
            ("CAM_Front_Ortho", Vector((0, -math.cos(el), math.sin(el))), Vector((0.4, 0, 2.3)), 14.2, (1536, 576)),
            ("CAM_Side_Ortho", Vector((math.cos(el), 0, math.sin(el))), Vector((0, 2.4, 2.4)), 11.0, (1280, 720)),
            ("CAM_Back_Ortho", Vector((0, math.cos(el), math.sin(el))), Vector((0.4, 0, 2.3)), 14.2, (1536, 576))):
        cd = bpy.data.cameras.new(name); cd.type = "ORTHO"; cd.ortho_scale = scale; cd.clip_end = 200
        co = bpy.data.objects.new(name, cd); L.objects.link(co)
        co.location = tgt + d * 40; look_at(co, tgt)
        co["res"] = res
        cams[name] = co
    SC.camera = cams["CAM_Front_Ortho"]
    return cams


build_body()
build_legs()
build_head()
for _side, _sx in (("L", 1), ("R", -1)):
    build_wing(_side, _sx)
build_tail_fin()
build_reef()
setup_world()
cams = setup_lights_cameras()
SC.render.engine = "CYCLES"
SC.cycles.device = "CPU"
SC.cycles.samples = int(os.environ.get("DRAGON_SAMPLES", "48"))
SC.cycles.use_denoising = True
SC.view_settings.view_transform = "Standard"
QUAL = float(os.environ.get("DRAGON_SCALE", "1.0"))
BLEND = os.path.join(HERE, "reef_dragon.blend")
SC.render.resolution_x, SC.render.resolution_y = 1536, 576
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
if os.environ.get("DRAGON_NO_RENDER") != "1":
    for key, fname in (("CAM_Front_Ortho", "front.png"), ("CAM_Side_Ortho", "side.png"), ("CAM_Back_Ortho", "back.png")):
        SC.camera = cams[key]
        SC.render.resolution_x, SC.render.resolution_y = int(cams[key]["res"][0] * QUAL), int(cams[key]["res"][1] * QUAL)
        SC.render.filepath = os.path.join(RENDER_DIR, fname)
        bpy.ops.render.render(write_still=True)
    SC.camera = cams["CAM_Front_Ortho"]
    SC.render.resolution_x, SC.render.resolution_y = 1536, 576
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print("DONE")
