"""
Low-poly "void Pegasus" reconstruction (Blender / bpy).

Run:  blender -b -P build_void_pegasus.py     (or: python build_void_pegasus.py with the bpy module)
Out:  void_pegasus.blend + renders/front.png, side.png, back.png

Conventions: horse faces -Y, up +Z, +X is its LEFT side. 1 unit ~ 100 px of the side reference.
"""
import bpy, bmesh, math, random, os
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
RENDER_DIR = os.path.join(HERE, "renders")
os.makedirs(RENDER_DIR, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
SC = bpy.context.scene
random.seed(9)
XAX = Vector((1, 0, 0))

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



# ============================================================================= VOID PEGASUS
PAL = dict(
    body=[C("231640"), C("2B1B4E"), C("1B1133"), C("35225E")],
    body_hi=[C("4A2F8A"), C("5A3AA8")],
    wingdark=[C("1E1438"), C("2A1A4C"), C("171029"), C("33205C")],
    indigo=[C("3A22B0"), C("4A2AC8"), C("2F1C98")],
    violet=[C("5B2FE0"), C("6A3CEC"), C("7848F2"), C("4E27D0")],
    lilac=[C("9D5CFF"), C("AC70FF"), C("B983FF")],
    pink=[C("C98AFF"), C("D69CFF"), C("BD78FF")],
)
MAT = dict(
    body=mat_lowpoly("M_Void_Body", 0.7), feather=mat_glow("M_Void_Feather", 0.06),
    flame=mat_glow("M_Void_Flame", 0.12), gem=mat_glow("M_Void_Gem", 0.25), eye=mat_glow("M_Eye_Glow", 3.0),
)
ROOT = bpy.data.collections.new("VOID_PEGASUS")
SC.collection.children.link(ROOT)
COLL = {}
for cname in ["HEAD", "EYES", "BODY", "LEGS", "HOOVES", "WINGS", "MANE", "TAIL", "GEMS", "SHARDS"]:
    c = bpy.data.collections.new(cname); ROOT.children.link(c); COLL[cname] = c
COLL["CAMERAS_LIGHTS"] = bpy.data.collections.new("CAMERAS_LIGHTS")
SC.collection.children.link(COLL["CAMERAS_LIGHTS"])


def grad(stops, t, rnd, amt=0.06):
    """Colour along a list of palettes (t in 0..1)."""
    t = max(0.0, min(0.999, t)) * (len(stops) - 1)
    i = int(t)
    return jit(lerp(rnd.choice(PAL[stops[i]]), rnd.choice(PAL[stops[i + 1]]), t - i), amt, rnd)


def two_tone(base_fn, tip_fn):
    """add_spike asks colours in (base face, tip face) order -> gradient along the blade."""
    state = [0]

    def col():
        state[0] += 1
        return base_fn() if state[0] % 2 else tip_fn()
    return col


def body_col(rnd, hi=0.10):
    return pick(PAL["body_hi"] if rnd.random() < hi else PAL["body"], rnd)


# ----------------------------------------------------------------------------- torso + neck
def build_body():
    rnd = random.Random(1)
    torso = [(-1.15, 2.55, .34, .42), (-0.85, 2.50, .52, .64), (-0.35, 2.42, .58, .68), (0.30, 2.42, .55, .62),
             (0.90, 2.50, .56, .62), (1.35, 2.56, .46, .54), (1.62, 2.52, .24, .30)]
    rings = [(Vector((0, y, z)), rw, rh) for (y, z, rw, rh) in catmull(torso, 2)]
    V, F, FC = loft(rings, 8, lambda sa, k: body_col(rnd), rnd)
    build("Body_Torso", V, F, FC, COLL["BODY"], MAT["body"])
    neck = [(-0.60, 2.72, .44, .66), (-0.80, 3.15, .36, .56), (-0.96, 3.58, .29, .46), (-1.08, 3.98, .24, .36),
            (-1.14, 4.22, .21, .30)]
    rings = [(Vector((0, y, z)), rw, rh) for (y, z, rw, rh) in catmull(neck, 2)]
    V, F, FC = loft(rings, 7, lambda sa, k: body_col(rnd), rnd)
    build("Body_Neck", V, F, FC, COLL["BODY"], MAT["body"])
    return rings


# ----------------------------------------------------------------------------- head
HEAD_M = Matrix.Translation((0, -1.22, 4.20)) @ Matrix.Rotation(math.radians(52), 4, "X") @ Matrix.Scale(1.3, 4)


def build_head():
    rnd = random.Random(21)
    UP = [(0.28, 0.17, 0.19, -0.16), (0.08, 0.205, 0.22, -0.24), (-0.18, 0.175, 0.18, -0.19),
          (-0.42, 0.125, 0.12, -0.12), (-0.62, 0.115, 0.10, -0.11)]
    rings = []
    for (y, w, zt, zb) in UP:
        zm = (zt + zb) / 2
        rings.append([Vector(q) for q in ((0, y, zt), (.6 * w, y, .85 * zt), (w, y, zm + 0.04), (.8 * w, y, zb * .8),
                                          (0, y, zb), (-.8 * w, y, zb * .8), (-w, y, zm + 0.04), (-.6 * w, y, .85 * zt))])
    V, F, FC = ring_mesh(rings, Vector((0, 0.40, 0.0)), Vector((0, -0.72, -0.02)), lambda k, j: body_col(rnd, 0.06))
    head = build("Head_Skull", V, F, FC, COLL["HEAD"], MAT["body"], HEAD_M)

    tree = BVHTree.FromPolygons(V, F)
    cutters = []
    for side, sx in (("L", 1), ("R", -1)):
        d = Vector((0.80 * sx, -0.40, 0.42)).normalized()
        hit, nrm, _, _ = tree.ray_cast(Vector((0, 0.02, 0.0)), d)
        if nrm.dot(d) < 0:
            nrm = -nrm
        Z = (nrm + d).normalized()
        slant = Vector((0, -1, -0.35))
        Xa = (slant - Z * slant.dot(Z)).normalized(); Ya = Z.cross(Xa)
        M = HEAD_M @ axes_matrix(Xa, Ya, Z, hit)
        r1, r2, dep, n = 0.075, 0.06, 0.02, 4
        CV, CF, CC = [], [], []
        for (r, z) in ((r2, -dep), (r1, 0.0), (r1 * 1.8, 0.2)):
            for k in range(n):
                a = 2 * math.pi * k / n
                CV.append(Vector((r * 1.6 * math.cos(a), r * 0.8 * math.sin(a), z)))
        for ring in range(2):
            for k in range(n):
                k2 = (k + 1) % n
                CF.append([ring * n + k, ring * n + k2, (ring + 1) * n + k2, (ring + 1) * n + k]); CC.append(C("5A2FD0"))
        CF.append(list(range(n))[::-1]); CC.append(C("5A2FD0"))
        CF.append([2 * n + k for k in range(n)]); CC.append(C("5A2FD0"))
        cut = build(f"_cut_{side}", CV, CF, CC, SC.collection, MAT["body"], M)
        cutters.append(cut)
        mod = head.modifiers.new(f"Socket_{side}", "BOOLEAN"); mod.operation = "DIFFERENCE"; mod.object = cut
        GV = [Vector((r2 * 1.55 * math.cos(2 * math.pi * k / n), r2 * 0.78 * math.sin(2 * math.pi * k / n), -dep + 0.003))
              for k in range(n)] + [Vector((0, 0, -dep + 0.012))]
        GF = [[k, (k + 1) % n, n] for k in range(n)]
        build(f"Eye_{side}_Glow", GV, GF, [jit(C("F070FF"), 0.05, rnd) for _ in GF], COLL["EYES"], MAT["eye"], M, recalc=False)
    dg = bpy.context.evaluated_depsgraph_get(); dg.update()
    new_me = bpy.data.meshes.new_from_object(head.evaluated_get(dg))
    old = head.data; head.modifiers.clear(); head.data = new_me; bpy.data.meshes.remove(old)
    for pl in new_me.polygons:
        pl.use_smooth = False
    for c in cutters:
        me = c.data; bpy.data.objects.remove(c); bpy.data.meshes.remove(me)

    for side, sx in (("L", 1), ("R", -1)):
        V, F, FC = [], [], []
        add_spike(V, F, FC, Vector((0.11 * sx, 0.20, 0.14)), Vector((0.17 * sx, 0.50, 0.42)), 0.075,
                  lambda: body_col(rnd, 0.2), n=4, belly=0.35, flat=1.0, flat_u=0.6)
        build(f"Head_Ear_{side}", V, F, FC, COLL["HEAD"], MAT["body"], HEAD_M)
    V, F, FC = [], [], []
    add_spike(V, F, FC, Vector((0, -0.02, 0.16)), Vector((0, 0.02, 0.34)), 0.075,
              two_tone(lambda: pick(PAL["violet"], rnd), lambda: pick(PAL["lilac"], rnd)), n=4, belly=0.5, flat=1.0, flat_u=1.4)
    build("Gem_Forehead", V, F, FC, COLL["GEMS"], MAT["gem"], HEAD_M)


# ----------------------------------------------------------------------------- legs
LEGS = {
    "Front": [(0.33, -0.78, 2.25, .32), (0.34, -0.74, 1.75, .26), (0.34, -0.80, 1.12, .16), (0.34, -0.76, 0.70, .13),
              (0.34, -0.74, 0.34, .125), (0.34, -0.80, 0.16, .15)],
    "Hind": [(0.36, 1.12, 2.35, .40), (0.37, 0.98, 1.75, .31), (0.37, 1.34, 1.12, .17), (0.37, 1.24, 0.70, .135),
             (0.37, 1.18, 0.34, .13), (0.37, 1.12, 0.16, .155)],
}


def build_legs():
    for which, ctrl in LEGS.items():
        for side, sx in (("L", 1), ("R", -1)):
            rnd = random.Random(hash((which, sx)) % 1000)
            pts = catmull([(x * sx, y, z, r) for (x, y, z, r) in ctrl], 2)
            rings = [(Vector((x, y, z)), r, r * 1.15) for (x, y, z, r) in pts]
            V, F, FC = loft(rings, 6, lambda sa, k: body_col(rnd, 0.08), rnd)
            build(f"Leg_{which}_{side}", V, F, FC, COLL["LEGS"], MAT["body"])
            x, y, z, r = pts[-1]
            V, F, FC = [], [], []
            add_prism(V, F, FC, Vector((x, y, 0.20)), Vector((x, y - 0.04, 0.0)), 0.16, 0.21, lambda: pick(PAL["pink"], rnd), 6)
            build(f"Hoof_{which}_{side}", V, F, FC, COLL["HOOVES"], MAT["flame"])
            # crystal growth on the lower leg: lilac near the hoof, violet higher up
            V, F, FC = [], [], []
            for i in range(16):
                h = rnd.uniform(0.12, 1.15)
                c = Vector((x, y + 0.04 * (h > 0.6), h))
                a = rnd.uniform(0, 2 * math.pi)
                rad = Vector((math.cos(a), math.sin(a), 0))
                base = c + rad * 0.09 - Vector((0, 0, 0.08))
                L = rnd.uniform(0.32, 0.55)
                tip = base + (rad * rnd.uniform(0.35, 0.6) + Vector((0, 0, 1))).normalized() * L
                t = 1 - h / 1.15
                add_spike(V, F, FC, base, tip, rnd.uniform(0.11, 0.15),
                          two_tone(lambda t=t: grad(["indigo", "violet", "lilac"], t, rnd),
                                   lambda t=t: grad(["violet", "lilac", "pink"], t, rnd)), n=4, belly=0.4)
            build(f"Leg_{which}_{side}_Crystals", V, F, FC, COLL["LEGS"], MAT["flame"])


# ----------------------------------------------------------------------------- wings (3 feather layers)
def build_wing(side, sx):
    rnd = random.Random(80 + sx)
    R0 = Vector((0.34 * sx, -0.30, 2.92))
    sw = math.radians(36)
    u = Vector((math.cos(sw) * sx, math.sin(sw), 0.0))
    v = Vector((0, -0.08, 1.0)); v = (v - u * v.dot(u)).normalized()
    nrm = u.cross(v) * sx
    K = 1.50

    def P(a, b, c=0.0):
        return R0 + u * (a * K) + v * b + nrm * c

    def A(t):                                      # leading-edge arm, slightly bowed
        return (2.45 * t - 0.12 * math.sin(math.pi * t), 1.70 * t + 0.22 * math.sin(math.pi * t))

    arm = [(P(*A(t)), r, r * 0.8) for t, r in ((0, .26), (.2, .23), (.4, .19), (.6, .15), (.8, .11), (1.0, .07))]
    V, F, FC = loft(arm, 6, lambda sa, k: pick(PAL["wingdark"], rnd), rnd, side_ref=nrm, jitter=0.03)
    add_ico(V, F, FC, R0, 0.34, lambda: pick(PAL["body"], rnd), 1, scale=(1, 1.2, 0.9), jitter=0.05, rnd=rnd)
    build(f"Wing_{side}_Arm", V, F, FC, COLL["WINGS"], MAT["body"])

    def feathers(name, count, t0, t1, lscale, width, base_stops, tip_stops, offsets, mat):
        V, F, FC = [], [], []
        for c_off in offsets:
            for i in range(count):
                t = t0 + (t1 - t0) * i / (count - 1)
                ang = math.radians(-72 + 84 * t ** 0.85 + rnd.uniform(-3, 3))
                L = (1.10 + 0.45 * t + 0.75 * math.sin(math.pi * t)) * lscale * rnd.uniform(0.92, 1.08)
                a, b = A(t)
                base = P(a - 0.10 * math.cos(ang), b - 0.10 * math.sin(ang), c_off)
                tip = P(a + L * math.cos(ang) / K, b + L * math.sin(ang), c_off * 0.4)
                add_spike(V, F, FC, base, tip, width, two_tone(lambda t=t: grad(base_stops, t, rnd), lambda t=t: grad(tip_stops, t, rnd)),
                          n=4, belly=0.42, flat=1.0, flat_u=0.16)
        build(f"Wing_{side}_{name}", V, F, FC, COLL["WINGS"], mat)

    feathers("Primaries", 17, 0.08, 1.0, 1.25, 0.38, ["indigo", "indigo", "violet"], ["violet", "lilac", "pink"], (0.0,), MAT["feather"])
    feathers("Secondaries", 15, 0.05, 0.98, 0.92, 0.42, ["wingdark", "wingdark", "indigo"], ["indigo", "indigo", "violet"], (0.07, -0.07), MAT["feather"])
    feathers("Coverts", 13, 0.03, 0.96, 0.64, 0.44, ["wingdark", "wingdark"], ["wingdark", "wingdark", "indigo"], (0.13, -0.13), MAT["body"])


# ----------------------------------------------------------------------------- flame mane and tail
def flame_shards(V, F, FC, origin, main, spread_a, spread_b, n, Lr, r, stops_base, stops_tip, t, rnd, sa=0.7, sb=0.5):
    for _ in range(n):
        d = (main + spread_a * rnd.uniform(-sa, sa) + spread_b * rnd.uniform(-sb, sb)).normalized()
        L = rnd.uniform(*Lr)
        add_spike(V, F, FC, origin - d * 0.1, origin + d * L, r * rnd.uniform(0.8, 1.2),
                  two_tone(lambda: grad(stops_base, t, rnd), lambda: grad(stops_tip, t, rnd)), n=4, belly=0.35,
                  flat=1.0, flat_u=0.32)


def build_mane(neck_rings):
    """Flame mane: rides the crest of the neck and flares up behind the poll; never in front of the face."""
    rnd = random.Random(31)
    V, F, FC = [], [], []
    m = len(neck_rings)
    for k, (c, rw, rh) in enumerate(neck_rings):
        tng = (neck_rings[min(k + 1, m - 1)][0] - neck_rings[max(k - 1, 0)][0]).normalized()
        crest = -XAX.cross(tng).normalized()            # neck runs upward, so its crest faces backward
        t = k / (m - 1)
        flame_shards(V, F, FC, c + crest * rh * 0.9, crest * 0.75 + Vector((0, 0.45, 0.55)), XAX, tng, 6,
                     (0.6, 1.15), 0.30, ["indigo", "indigo", "violet"], ["violet", "violet", "lilac", "pink"],
                     0.2 + 0.7 * t, rnd, sa=0.8, sb=0.25)
    top = Vector((0, -0.98, 4.42))
    flame_shards(V, F, FC, top, Vector((0, 0.45, 1)), XAX, Vector((0, 1, 0)), 20, (0.7, 1.35), 0.32,
                 ["indigo", "violet"], ["violet", "lilac", "pink"], 0.8, rnd, sa=1.0, sb=0.35)
    build("Mane_Flame", V, F, FC, COLL["MANE"], MAT["flame"])


def build_tail():
    rnd = random.Random(41)
    ctrl = [(0.0, 1.50, 2.66, .24), (0.08, 2.15, 2.70, .48), (0.30, 2.95, 2.15, .62), (0.62, 3.70, 2.05, .60),
            (0.95, 4.40, 1.40, .52), (1.25, 5.05, 1.40, .40), (1.55, 5.75, 0.85, .18)]
    pts = catmull(ctrl, 3)
    rings = [(Vector((x, y, z)), r * 0.45, r) for (x, y, z, r) in pts]
    m = len(rings)
    V, F, FC = loft(rings, 6, lambda sa, k: grad(["indigo", "indigo", "indigo", "violet", "violet"], k / m, rnd), rnd, jitter=0.06)
    for k, (c, rw, rh) in enumerate(rings):
        if k == 0:
            continue
        tng = (rings[min(k + 1, m - 1)][0] - rings[k - 1][0]).normalized()
        dorsal = XAX.cross(tng).normalized()
        t = k / (m - 1)
        flame_shards(V, F, FC, c, tng, dorsal, XAX, 3, (1.0, 1.9), 0.22 + rh * 0.5,
                     ["indigo", "indigo", "indigo", "violet"], ["indigo", "violet", "violet", "lilac", "pink"], t, rnd, sa=0.5, sb=0.3)
    build("Tail_Flame", V, F, FC, COLL["TAIL"], MAT["flame"])


# ----------------------------------------------------------------------------- gems, harness, floating shards
def rhombus(name, center, normal, up, size, rnd, frame_only=False):
    """Diamond emblem: lilac frame (4 bars) + dark-violet faceted gem."""
    n = normal.normalized()
    upv = (up - n * up.dot(n)).normalized()
    sidev = n.cross(upv)
    corners = [center + upv * size, center + sidev * size * 0.62, center - upv * size, center - sidev * size * 0.62]
    V, F, FC = [], [], []
    for i in range(4):
        add_prism(V, F, FC, corners[i] + n * 0.02, corners[(i + 1) % 4] + n * 0.02, size * 0.13, size * 0.13,
                  lambda: pick(PAL["lilac"], rnd), 4)
    build(f"{name}_Frame", V, F, FC, COLL["GEMS"], MAT["gem"])
    V = [center + n * (size * 0.28)] + [center + (c - center) * 0.72 for c in corners] + [center - n * 0.05]
    F = [[0, 1 + i, 1 + (i + 1) % 4] for i in range(4)] + [[5, 1 + (i + 1) % 4, 1 + i] for i in range(4)]
    FC = [pick(PAL["indigo"] + PAL["violet"][:2], rnd) for _ in F]
    build(f"{name}_Gem", V, F, FC, COLL["GEMS"], MAT["gem"])


def build_gems():
    rnd = random.Random(51)
    rhombus("Emblem_Chest", Vector((0, -1.27, 2.58)), Vector((0, -1, 0.15)), Vector((0, 0, 1)), 0.34, rnd)
    rhombus("Emblem_Back", Vector((0, -0.05, 3.06)), Vector((0, 0.25, 1)), Vector((0, -1, 0)), 0.22, rnd)
    for side, sx in (("L", 1), ("R", -1)):
        rhombus(f"Emblem_Shoulder_{side}", Vector((0.56 * sx, -0.80, 2.50)), Vector((sx, -0.25, 0.1)), Vector((0, 0, 1)), 0.20, rnd)
        rhombus(f"Emblem_Hip_{side}", Vector((0.58 * sx, 1.00, 2.50)), Vector((sx, 0.1, 0.15)), Vector((0, 0, 1)), 0.13, rnd)
        V, F, FC = [], [], []
        path = [Vector((0.10 * sx, -1.22, 2.90)), Vector((0.40 * sx, -1.02, 2.97)), Vector((0.55 * sx, -0.60, 2.98)),
                Vector((0.30 * sx, -0.10, 3.06))]
        for a, b in zip(path, path[1:]):
            add_prism(V, F, FC, a, b, 0.035, 0.035, lambda: pick(PAL["lilac"], rnd), 4)
        build(f"Harness_{side}", V, F, FC, COLL["GEMS"], MAT["gem"])


def build_shards():
    rnd = random.Random(61)
    V, F, FC = [], [], []
    spots = []
    for sx in (1, -1):
        for _ in range(9):
            spots.append(Vector((sx * rnd.uniform(1.3, 5.2), rnd.uniform(0.2, 3.2), rnd.uniform(1.4, 3.3))))
        for _ in range(3):
            spots.append(Vector((sx * rnd.uniform(0.5, 1.0), rnd.uniform(-1.4, -0.6), rnd.uniform(3.6, 4.8))))
    for _ in range(9):
        spots.append(Vector((rnd.uniform(0.2, 2.3), rnd.uniform(3.0, 6.3), rnd.uniform(0.2, 2.6))))
    for p in spots:
        d = Vector((rnd.uniform(-.5, .5), rnd.uniform(-.5, .5), 1)).normalized()
        L = rnd.uniform(0.22, 0.48)
        pal = rnd.choice((["indigo", "violet"], ["violet", "lilac"], ["indigo", "indigo"]))
        add_spike(V, F, FC, p - d * L / 2, p + d * L / 2, L * 0.30,
                  two_tone(lambda: pick(PAL[pal[0]], rnd), lambda: pick(PAL[pal[1]], rnd)), n=4, belly=0.5, flat=1.0, flat_u=0.6)
    build("Floating_Shards", V, F, FC, COLL["SHARDS"], MAT["gem"])


# ----------------------------------------------------------------------------- cameras / lights / render
def setup_lights_cameras():
    L = COLL["CAMERAS_LIGHTS"]
    for name, energy, ang, loc in (("Light_Key_Sun", 1.25, 30, (-5, -9, 10)), ("Light_Fill_Sun", 0.6, 60, (7, 6, 4)),
                                   ("Light_Back_Sun", 0.9, 60, (-3, 9, 6))):
        sun = bpy.data.lights.new(name, "SUN"); sun.energy = energy; sun.angle = math.radians(ang)
        so = bpy.data.objects.new(name, sun); L.objects.link(so); so.location = loc; look_at(so, (0, 0, 0))
    cams = {}
    el = math.radians(3)
    for name, d, tgt, scale, res in (
            ("CAM_Front_Ortho", Vector((0, -math.cos(el), math.sin(el))), Vector((0.3, 0, 2.55)), 12.4, (1254, 620)),
            ("CAM_Side_Ortho", Vector((math.cos(el), 0, math.sin(el))), Vector((0, 2.4, 2.6)), 10.4, (1000, 660)),
            ("CAM_Back_Ortho", Vector((0, math.cos(el), math.sin(el))), Vector((-0.3, 0, 2.55)), 12.4, (1254, 620))):
        cd = bpy.data.cameras.new(name); cd.type = "ORTHO"; cd.ortho_scale = scale; cd.clip_end = 200
        co = bpy.data.objects.new(name, cd); L.objects.link(co)
        co.location = tgt + d * 40; look_at(co, tgt); co["res"] = res
        cams[name] = co
    SC.camera = cams["CAM_Front_Ortho"]
    return cams


neck_rings = build_body()
build_head()
build_legs()
for _side, _sx in (("L", 1), ("R", -1)):
    build_wing(_side, _sx)
build_mane(neck_rings)
build_tail()
build_gems()
build_shards()
setup_world()
cams = setup_lights_cameras()
SC.render.engine = "CYCLES"
SC.cycles.device = "CPU"
SC.cycles.samples = int(os.environ.get("PEGASUS_SAMPLES", "48"))
SC.cycles.use_denoising = True
SC.view_settings.view_transform = "Standard"
QUAL = float(os.environ.get("PEGASUS_SCALE", "1.0"))
BLEND = os.path.join(HERE, "void_pegasus.blend")
SC.render.resolution_x, SC.render.resolution_y = 1254, 620
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
if os.environ.get("PEGASUS_NO_RENDER") != "1":
    for key, fname in (("CAM_Front_Ortho", "front.png"), ("CAM_Side_Ortho", "side.png"), ("CAM_Back_Ortho", "back.png")):
        SC.camera = cams[key]
        SC.render.resolution_x, SC.render.resolution_y = int(cams[key]["res"][0] * QUAL), int(cams[key]["res"][1] * QUAL)
        SC.render.filepath = os.path.join(RENDER_DIR, fname)
        bpy.ops.render.render(write_still=True)
    SC.camera = cams["CAM_Front_Ortho"]
    SC.render.resolution_x, SC.render.resolution_y = 1254, 620
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print("DONE")
