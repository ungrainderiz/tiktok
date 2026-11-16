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
BODY_SURF = []


def on_body(target, lift=0.03):
    """Snap a point onto the outer body surface (torso or neck), so straps and emblems never float."""
    o = Vector((0, max(target.y, -0.70), 2.55))
    d = (target - o).normalized()
    best = None
    for V, F in BODY_SURF:
        hit = BVHTree.FromPolygons(V, F).ray_cast(o + d * 3.0, -d)[0]
        if hit is not None and (best is None or (hit - o).length > (best - o).length):
            best = hit
    return (best if best is not None else target) + d * lift


def build_body():
    rnd = random.Random(1)
    torso = [(-1.18, 2.66, .34, .44), (-0.88, 2.58, .54, .68), (-0.35, 2.46, .58, .68), (0.30, 2.40, .54, .60),
             (0.90, 2.44, .56, .62), (1.35, 2.50, .46, .54), (1.62, 2.46, .24, .30)]
    rings = [(Vector((0, y, z)), rw, rh) for (y, z, rw, rh) in catmull(torso, 2)]
    V, F, FC = loft(rings, 8, lambda sa, k: body_col(rnd), rnd)
    build("Body_Torso", V, F, FC, COLL["BODY"], MAT["body"])
    BODY_SURF.append((list(V), list(F)))
    neck = [(-0.58, 2.70, .46, .78), (-0.66, 3.15, .40, .68), (-0.70, 3.62, .33, .54), (-0.82, 4.02, .27, .42),
            (-1.04, 4.30, .23, .33), (-1.24, 4.36, .20, .27)]
    rings = [(Vector((0, y, z)), rw, rh) for (y, z, rw, rh) in catmull(neck, 2)]
    V, F, FC = loft(rings, 7, lambda sa, k: body_col(rnd), rnd)
    build("Body_Neck", V, F, FC, COLL["BODY"], MAT["body"])
    BODY_SURF.append((list(V), list(F)))
    return rings


# ----------------------------------------------------------------------------- head
HEAD_M = Matrix.Translation((0, -1.38, 4.26)) @ Matrix.Rotation(math.radians(50), 4, "X") @ Matrix.Scale(1.22, 4)


def build_head():
    """Horse head (local: nose -> -Y, forehead -> +Z): deep jowl, tapering nasal bone, squared muzzle."""
    rnd = random.Random(21)
    #        y,    half-w, z_top, z_bottom
    UP = [(0.30, 0.190, 0.16, -0.21), (0.12, 0.255, 0.21, -0.34), (-0.07, 0.245, 0.20, -0.31),
          (-0.25, 0.190, 0.16, -0.21), (-0.41, 0.155, 0.135, -0.16), (-0.54, 0.160, 0.130, -0.17),
          (-0.62, 0.130, 0.09, -0.13)]
    rings = []
    for (y, w, zt, zb) in UP:
        zm = (zt + zb) / 2
        rings.append([Vector(q) for q in ((0, y, zt), (.72 * w, y, .90 * zt), (w, y, zm + 0.05), (.78 * w, y, zb * .78),
                                          (0, y, zb), (-.78 * w, y, zb * .78), (-w, y, zm + 0.05), (-.72 * w, y, .90 * zt))])
    V, F, FC = ring_mesh(rings, Vector((0, 0.44, -0.02)), Vector((0, -0.66, -0.03)), lambda k, j: body_col(rnd, 0.07))
    head = build("Head_Skull", V, F, FC, COLL["HEAD"], MAT["body"], HEAD_M)

    tree = BVHTree.FromPolygons(V, F)
    cutters = []
    for side, sx in (("L", 1), ("R", -1)):
        d = Vector((0.72 * sx, -0.46, 0.52)).normalized()
        hit, nrm, _, _ = tree.ray_cast(Vector((0, 0.0, -0.02)), d)
        if nrm.dot(d) < 0:
            nrm = -nrm
        Z = (nrm + d).normalized()
        slant = Vector((0, -1, -0.45))
        Xa = (slant - Z * slant.dot(Z)).normalized(); Ya = Z.cross(Xa)
        M = HEAD_M @ axes_matrix(Xa, Ya, Z, hit)
        r1, r2, dep, n = 0.095, 0.082, 0.018, 6
        ell = lambda r, k: Vector((r * 1.55 * math.cos(2 * math.pi * k / n), r * 0.80 * math.sin(2 * math.pi * k / n), 0))
        CV, CF, CC = [], [], []
        for (r, z) in ((r2, -dep), (r1, 0.0), (r1 * 1.8, 0.2)):
            for k in range(n):
                CV.append(ell(r, k) + Vector((0, 0, z)))
        for ring in range(2):
            for k in range(n):
                k2 = (k + 1) % n
                CF.append([ring * n + k, ring * n + k2, (ring + 1) * n + k2, (ring + 1) * n + k]); CC.append(C("7A3BE8"))
        CF.append(list(range(n))[::-1]); CC.append(C("7A3BE8"))
        CF.append([2 * n + k for k in range(n)]); CC.append(C("7A3BE8"))
        cut = build(f"_cut_{side}", CV, CF, CC, SC.collection, MAT["body"], M)
        cutters.append(cut)
        mod = head.modifiers.new(f"Socket_{side}", "BOOLEAN"); mod.operation = "DIFFERENCE"; mod.object = cut
        # glowing eye: magenta rim, pale hot core
        GV = [ell(r2, k) + Vector((0, 0, -dep + 0.003)) for k in range(n)] + \
             [ell(r2 * 0.5, k) + Vector((0, 0, -dep + 0.010)) for k in range(n)] + [Vector((0, 0, -dep + 0.014))]
        GF, GC = [], []
        for k in range(n):
            k2 = (k + 1) % n
            GF.append([k, k2, n + k2, n + k]); GC.append(jit(C("E050FF"), 0.05, rnd))
            GF.append([n + k, n + k2, 2 * n]); GC.append(C("FFD8FF"))
        build(f"Eye_{side}_Glow", GV, GF, GC, COLL["EYES"], MAT["eye"], M, recalc=False)
    dg = bpy.context.evaluated_depsgraph_get(); dg.update()
    new_me = bpy.data.meshes.new_from_object(head.evaluated_get(dg))
    old = head.data; head.modifiers.clear(); head.data = new_me; bpy.data.meshes.remove(old)
    for pl in new_me.polygons:
        pl.use_smooth = False
    for c in cutters:
        me = c.data; bpy.data.objects.remove(c); bpy.data.meshes.remove(me)

    for side, sx in (("L", 1), ("R", -1)):
        V, F, FC = [], [], []
        add_spike(V, F, FC, Vector((0.13 * sx, 0.24, 0.12)), Vector((0.21 * sx, 0.46, 0.46)), 0.10,
                  lambda: body_col(rnd, 0.25), n=4, belly=0.32, flat=1.0, flat_u=0.55)
        build(f"Head_Ear_{side}", V, F, FC, COLL["HEAD"], MAT["body"], HEAD_M)
        V, F, FC = [], [], []                                   # lilac streak under the eye
        add_spike(V, F, FC, Vector((0.235 * sx, -0.13, 0.02)), Vector((0.195 * sx, -0.30, 0.00)), 0.03,
                  lambda: pick(PAL["lilac"], rnd), n=4, belly=0.3, flat=1.0, flat_u=0.5)
        build(f"Head_CheekMark_{side}", V, F, FC, COLL["GEMS"], MAT["gem"], HEAD_M)
    V, F, FC = [], [], []
    add_spike(V, F, FC, Vector((0, -0.20, 0.155)), Vector((0, 0.10, 0.24)), 0.07,
              two_tone(lambda: pick(PAL["violet"], rnd), lambda: pick(PAL["lilac"], rnd)), n=4, belly=0.5, flat=0.45, flat_u=1.0)
    build("Gem_Forehead", V, F, FC, COLL["GEMS"], MAT["gem"], HEAD_M)


# ----------------------------------------------------------------------------- legs
LEGS = {   # (x, y, z, radius) from shoulder/hip down to the hoof — an airborne prance, not a standing square
    "Front_L": [(0.33, -0.80, 2.28, .32), (0.34, -0.98, 1.84, .26), (0.34, -1.36, 1.62, .17), (0.34, -1.30, 1.22, .135),
                (0.34, -1.12, 0.94, .13), (0.34, -1.08, 0.74, .15)],                       # raised and folded
    "Front_R": [(-0.33, -0.78, 2.28, .32), (-0.34, -0.70, 1.78, .26), (-0.34, -0.66, 1.15, .16), (-0.34, -0.56, 0.72, .13),
                (-0.34, -0.50, 0.36, .125), (-0.34, -0.54, 0.16, .15)],                    # reaching down, slightly back
    "Hind_L": [(0.36, 1.12, 2.32, .40), (0.37, 1.08, 1.74, .31), (0.37, 1.58, 1.24, .17), (0.37, 1.68, 0.80, .135),
               (0.37, 1.80, 0.46, .13), (0.37, 1.90, 0.28, .155)],                         # pushed out behind
    "Hind_R": [(-0.36, 1.10, 2.32, .40), (-0.37, 0.84, 1.74, .31), (-0.37, 1.08, 1.14, .17), (-0.37, 0.90, 0.72, .135),
               (-0.37, 0.78, 0.38, .13), (-0.37, 0.70, 0.18, .155)],                       # tucked under the belly
}


def build_legs():
    for name, ctrl in LEGS.items():
        rnd = random.Random(sum(ord(ch) for ch in name))
        pts = catmull(ctrl, 3)
        rings = [(Vector((x, y, z)), r, r * 1.15) for (x, y, z, r) in pts]
        V, F, FC = loft(rings, 6, lambda sa, k: body_col(rnd, 0.08), rnd)
        build(f"Leg_{name}", V, F, FC, COLL["LEGS"], MAT["body"])

        # crystal greave + hoof: ONE faceted piece that follows the lower leg from the hoof upward
        path = [Vector((x, y, z)) for (x, y, z, r) in pts][::-1]
        end_dir = (path[0] - path[1]).normalized()
        path = [path[0] + end_dir * 0.18] + path

        def along(dist):
            acc = 0.0
            for i in range(len(path) - 1):
                seg = (path[i + 1] - path[i]).length
                if acc + seg >= dist:
                    return path[i].lerp(path[i + 1], (dist - acc) / seg), (path[i + 1] - path[i]).normalized()
                acc += seg
            return path[-1], (path[-1] - path[-2]).normalized()
        levels = [(0.00, .20), (0.13, .16), (0.24, .20), (0.40, .165), (0.50, .21), (0.68, .155), (0.78, .185),
                  (0.94, .14), (1.06, .09)]
        n = 8
        V, F, FC, rows = [], [], [], []
        for k, (dq, rad) in enumerate(levels):
            c, tg = along(dq)
            uu, vv = frame(tg)
            row = []
            for j in range(n):
                a2 = 2 * math.pi * (j + 0.5 * (k % 2)) / n
                rr = rad * (1.45 if (j + k) % 2 else 0.78) * rnd.uniform(0.92, 1.08)
                lift = tg * (0.10 * rad / 0.2 if (j + k) % 2 and 0 < k < len(levels) - 1 else 0.0)   # tips sweep up the leg
                V.append(c + (uu * math.cos(a2) + vv * math.sin(a2)) * rr + lift); row.append(len(V) - 1)
            rows.append(row)
        for k in range(len(levels) - 1):
            t = (levels[k][0] + levels[k + 1][0]) / 2 / 1.06
            for j in range(n):
                j2 = (j + 1) % n
                for tri in ([rows[k][j], rows[k][j2], rows[k + 1][j2]], [rows[k][j], rows[k + 1][j2], rows[k + 1][j]]):
                    F.append(tri); FC.append(grad(["pink", "lilac", "violet", "violet", "indigo"], t, rnd))
        V.append(along(0.0)[0]); V.append(along(1.12)[0])
        for j in range(n):
            j2 = (j + 1) % n
            F.append([rows[0][j2], rows[0][j], len(V) - 2]); FC.append(pick(PAL["pink"], rnd))
            F.append([rows[-1][j], rows[-1][j2], len(V) - 1]); FC.append(pick(PAL["indigo"], rnd))
        build(f"Leg_{name}_CrystalHoof", V, F, FC, COLL["HOOVES"], MAT["flame"])


# ----------------------------------------------------------------------------- wings: one solid surface each
def build_wing(side, sx):
    """Whole wing = ONE closed mesh: thick dark leading edge thinning into a serrated, ridged feather sheet."""
    rnd = random.Random(80 + sx)
    R0 = Vector((0.30 * sx, -0.30, 2.90))
    sw = math.radians(36)
    u = Vector((math.cos(sw) * sx, math.sin(sw), 0.0))
    v = Vector((0, -0.08, 1.0)); v = (v - u * v.dot(u)).normalized()
    nrm = u.cross(v) * sx
    K = 1.50

    def A(t):
        return (2.40 * t - 0.12 * math.sin(math.pi * t), 2.05 * t + 0.24 * math.sin(math.pi * t))

    NF = 10
    cols = 2 * NF
    S = [0.0, 0.20, 0.42, 0.64, 0.84, 1.0]
    front, back, meta = [], [], []
    V, F, FC = [], [], []
    for c in range(cols + 1):
        t = 0.0 + 1.0 * c / cols
        center = (c % 2 == 1)
        ang = math.radians(-72 + 84 * t ** 0.85)
        L = (1.10 + 0.45 * t + 0.75 * math.sin(math.pi * t)) * 1.42 * (1.0 if center else 0.62) * rnd.uniform(0.94, 1.06)
        a0, b0 = A(t)
        fr, bk = [], []
        for si, sv in enumerate(S):
            a = a0 + (L * sv - 0.16) * math.cos(ang) / K
            b = b0 + (L * sv - 0.16) * math.sin(ang)
            ridge = (0.10 if center else -0.06) * sv
            th = 0.24 * (1 - 0.55 * t) * (1 - sv) ** 1.6 + 0.012
            base = R0 + u * (a * K) + v * b
            V.append(base + nrm * (ridge + th)); fr.append(len(V) - 1)
            V.append(base + nrm * (ridge - th)); bk.append(len(V) - 1)
        front.append(fr); back.append(bk); meta.append((t, rnd.uniform(-0.07, 0.07)))

    def wcol(c, si):
        t, dj = meta[c]
        sm = (S[si] + S[si + 1]) / 2 + dj
        if sm < 0.36:
            return pick(PAL["wingdark"], rnd)
        if sm < 0.58:
            return jit(lerp(rnd.choice(PAL["wingdark"]), rnd.choice(PAL["indigo"]), (sm - 0.30) / 0.28), 0.06, rnd)
        if sm < 0.80:
            return grad(["indigo", "violet"], (sm - 0.58) / 0.22, rnd)
        return grad(["violet", "lilac", "pink"], 0.35 + 0.65 * t, rnd)

    for c in range(cols):
        for si in range(len(S) - 1):
            for grid, flip in ((front, False), (back, True)):
                a, b, c2, d = grid[c][si], grid[c + 1][si], grid[c + 1][si + 1], grid[c][si + 1]
                for tri in (([a, b, c2], [a, c2, d]) if c % 2 else ([a, b, d], [b, c2, d])):
                    F.append(tri[::-1] if flip else tri); FC.append(wcol(c, si))
        for si, edge_col in ((0, lambda: pick(PAL["wingdark"], rnd)), (len(S) - 1, lambda: pick(PAL["pink"], rnd))):
            F.append([front[c][si], front[c + 1][si], back[c + 1][si], back[c][si]]); FC.append(edge_col())
    for c in (0, cols):
        for si in range(len(S) - 1):
            F.append([front[c][si], front[c][si + 1], back[c][si + 1], back[c][si]]); FC.append(pick(PAL["wingdark"], rnd))
    build(f"Wing_{side}", V, F, FC, COLL["WINGS"], MAT["feather"])


# ----------------------------------------------------------------------------- flame mane and tail: one sheet each
def saw(x):
    return x - math.floor(x)


def flame_ribbon(name, centers, ups, widths, tops, bots, colfn, coll, mat, rnd, n=8, jitter=0.03):
    """ONE closed mesh: a ribbon whose upper/lower crests rise and drop like licking flame tongues."""
    V, F, FC, rows = [], [], [], []
    m = len(centers)
    for k in range(m):
        tng = (centers[min(k + 1, m - 1)] - centers[max(k - 1, 0)]).normalized()
        up = (ups[k] - tng * ups[k].dot(tng)).normalized()
        side = tng.cross(up).normalized()
        row = []
        for j in range(n):
            a = 2 * math.pi * (j + 0.5 * (k % 2)) / n
            sa = math.sin(a)
            p = centers[k] + side * widths[k] * math.cos(a) + up * (tops[k] if sa >= 0 else bots[k]) * sa
            p += Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * jitter
            V.append(p); row.append(len(V) - 1)
        rows.append(row)
    for k in range(m - 1):
        for j in range(n):
            j2 = (j + 1) % n
            sa = math.sin(2 * math.pi * (j + 0.75) / n)
            for tri in ([rows[k][j], rows[k][j2], rows[k + 1][j2]], [rows[k][j], rows[k + 1][j2], rows[k + 1][j]]):
                F.append(tri); FC.append(colfn(k / (m - 1), sa))
    V.append(centers[0]); V.append(centers[-1] + (centers[-1] - centers[-2]))
    for j in range(n):
        j2 = (j + 1) % n
        F.append([rows[0][j2], rows[0][j], len(V) - 2]); FC.append(colfn(0.0, 0.0))
        F.append([rows[-1][j], rows[-1][j2], len(V) - 1]); FC.append(colfn(1.0, 1.0))
    return build(name, V, F, FC, coll, mat)


def build_mane(neck_rings):
    rnd = random.Random(31)
    ctrl = [(-1.30, 4.66, 0.0, -0.10, 1.0, 0.40, 0.12), (-1.12, 4.66, 0.0, 0.45, 1.0, 0.80, 0.26), (-0.96, 4.50, 0.0, 0.80, 0.9, 0.95, 0.30)]
    m = len(neck_rings)
    for k in range(m - 4, -1, -2):
        c, rw, rh = neck_rings[k]
        tng = (neck_rings[min(k + 1, m - 1)][0] - neck_rings[max(k - 1, 0)][0]).normalized()
        crest = -XAX.cross(tng).normalized()
        p = c + crest * rh * 0.72
        upv = (crest * 0.8 + Vector((0, 0.60, 0.40))).normalized()
        ctrl.append((p.y, p.z, upv.x, upv.y, upv.z, 1.0, 0.38))
    ctrl.append((-0.05, 3.10, 0.0, 0.8, 0.8, 0.45, 0.16))
    pts = catmull(ctrl, 5)
    M = len(pts)
    centers = [Vector((0.10 * math.sin(i * 0.7), y, z)) for i, (y, z, *_r) in enumerate(pts)]
    ups = [Vector((ux + 0.10 * math.sin(i * 1.3), uy, uz)).normalized() for i, (_y, _z, ux, uy, uz, _t, _w) in enumerate(pts)]
    tops = [tp * (0.22 + 1.25 * saw(i / 5.0 + 0.2) ** 1.4) for i, (*_a, tp, _w) in enumerate(pts)]
    widths = [w for (*_a, w) in pts]
    bots = [0.30] * M

    def col(t, sa):
        peak = saw(t * (M - 1) / 5.0 + 0.2)
        if sa > 0.55:
            return grad(["indigo", "violet", "lilac", "pink"], peak ** 0.7, rnd)
        if sa > -0.1:
            return grad(["indigo", "indigo", "violet", "lilac"], peak ** 0.9, rnd)
        return pick(PAL["indigo"], rnd)
    flame_ribbon("Mane_Flame", centers, ups, widths, tops, bots, col, COLL["MANE"], MAT["flame"], rnd, n=8)


def build_tail():
    rnd = random.Random(41)
    ctrl = [(0.0, 1.45, 2.58, .26), (0.05, 2.10, 2.95, .58), (0.22, 2.95, 2.62, .80), (0.48, 3.75, 2.80, .80),
            (0.78, 4.50, 2.10, .74), (1.05, 5.25, 2.00, .62), (1.30, 5.95, 1.35, .46), (1.50, 6.70, 1.05, .14)]
    pts = catmull(ctrl, 5)
    M = len(pts)
    centers = [Vector((x + 0.12 * math.sin(i * 0.8), y, z)) for i, (x, y, z, r) in enumerate(pts)]
    ups = [Vector((0.25 * math.sin(i * 0.6), 0, 1)) for i in range(M)]
    tops = [r * (0.25 + 1.35 * saw(i / 7.0 + 0.1) ** 1.4) for i, (*_a, r) in enumerate(pts)]
    bots = [r * (0.25 + 1.25 * saw(i / 7.0 + 0.55) ** 1.4) for i, (*_a, r) in enumerate(pts)]
    widths = [r * 0.26 for (*_a, r) in pts]

    def col(t, sa):
        i = t * (M - 1)
        peak = saw(i / 7.0 + 0.1) if sa > 0 else saw(i / 7.0 + 0.55)
        if abs(sa) > 0.6:
            return grad(["indigo", "violet", "violet", "lilac", "pink"], min(1.0, 0.15 + 0.6 * peak + 0.3 * t), rnd)
        return grad(["indigo", "indigo", "indigo", "violet"], t, rnd)
    flame_ribbon("Tail_Flame", centers, ups, widths, tops, bots, col, COLL["TAIL"], MAT["flame"], rnd, n=10, jitter=0.04)


# ----------------------------------------------------------------------------- gems, harness, floating shards
def add_rhombus(V, F, FC, center, normal, up, size, rnd):
    """Diamond emblem (lilac frame + dark-violet faceted gem) appended to one mesh."""
    n = normal.normalized()
    upv = (up - n * up.dot(n)).normalized()
    sidev = n.cross(upv)
    corners = [center + upv * size, center + sidev * size * 0.62, center - upv * size, center - sidev * size * 0.62]
    for i in range(4):
        add_prism(V, F, FC, corners[i] + n * 0.02, corners[(i + 1) % 4] + n * 0.02, size * 0.13, size * 0.13,
                  lambda: pick(PAL["lilac"], rnd), 4)
    b0 = len(V)
    V += [center + n * (size * 0.28)] + [center + (c - center) * 0.72 for c in corners] + [center - n * 0.05]
    for i in range(4):
        F.append([b0, b0 + 1 + i, b0 + 1 + (i + 1) % 4]); FC.append(pick(PAL["indigo"] + PAL["violet"][:2], rnd))
        F.append([b0 + 5, b0 + 1 + (i + 1) % 4, b0 + 1 + i]); FC.append(pick(PAL["indigo"], rnd))


def build_gems():
    rnd = random.Random(51)
    V, F, FC = [], [], []
    add_rhombus(V, F, FC, on_body(Vector((0, -1.40, 2.62)), 0.02), Vector((0, -1, 0.20)), Vector((0, 0, 1)), 0.34, rnd)
    for sx in (1, -1):                                 # straps hug the chest and run up to the withers
        tg = [(0.12, -1.40, 2.95), (0.30, -1.30, 3.05), (0.48, -1.10, 3.10), (0.62, -0.85, 3.10), (0.66, -0.60, 3.10),
              (0.50, -0.40, 3.30), (0.25, -0.25, 3.50)]
        path = [on_body(Vector((x * sx, y, z))) for (x, y, z) in tg]
        for a, b in zip(path, path[1:]):
            add_prism(V, F, FC, a, b, 0.04, 0.04, lambda: pick(PAL["lilac"], rnd), 4)
    add_rhombus(V, F, FC, Vector((0, -0.05, 3.06)), Vector((0, 0.25, 1)), Vector((0, -1, 0)), 0.22, rnd)
    build("Harness_Emblems", V, F, FC, COLL["GEMS"], MAT["gem"])
    for side, sx in (("L", 1), ("R", -1)):
        for nm, c, nv, sz in (("Shoulder", Vector((0.56 * sx, -0.80, 2.50)), Vector((sx, -0.25, 0.1)), 0.20),
                              ("Hip", Vector((0.58 * sx, 1.00, 2.50)), Vector((sx, 0.1, 0.15)), 0.13)):
            V, F, FC = [], [], []
            add_rhombus(V, F, FC, c, nv, Vector((0, 0, 1)), sz, rnd)
            build(f"Emblem_{nm}_{side}", V, F, FC, COLL["GEMS"], MAT["gem"])


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
            ("CAM_Front_Ortho", Vector((0, -math.cos(el), math.sin(el))), Vector((0.3, 0, 2.85)), 12.6, (1254, 620)),
            ("CAM_Side_Ortho", Vector((math.cos(el), 0, math.sin(el))), Vector((0, 2.6, 2.75)), 11.0, (1000, 660)),
            ("CAM_Back_Ortho", Vector((0, math.cos(el), math.sin(el))), Vector((-0.3, 0, 2.85)), 12.6, (1254, 620))):
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
