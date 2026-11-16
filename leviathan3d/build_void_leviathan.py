"""
Low-poly "void Leviathan" reconstruction (Blender / bpy).

Run:  blender -b -P build_void_leviathan.py     (or: python build_void_leviathan.py with the bpy module)
Out:  void_leviathan.blend + renders/face.png, profil.png, trois_quarts.png, dos.png

Conventions: head faces -Y, up +Z, +X is its LEFT side. 1 unit ~ 60 px of the profile reference.
"""
import bpy, bmesh, math, random, os
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
RENDER_DIR = os.path.join(HERE, "renders")
os.makedirs(RENDER_DIR, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
SC = bpy.context.scene
random.seed(13)
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




# ============================================================================= VOID LEVIATHAN
PAL = dict(
    body=[C("1E1438"), C("26184A"), C("181030"), C("2F1E5C")],
    body_hi=[C("3E2A8A"), C("4A2FA8")],
    belly=[C("B9A0F5"), C("A58CEE"), C("C8B4FA"), C("9A7FE6")],
    belly_shade=[C("7E62D8"), C("8A6EE0")],
    wingdark=[C("1E1438"), C("2A1A4C"), C("171029"), C("33205C")],
    indigo=[C("3A22B0"), C("4A2AC8"), C("2F1C98")],
    violet=[C("5B2FE0"), C("6A3CEC"), C("7848F2"), C("4E27D0")],
    lilac=[C("9D5CFF"), C("AC70FF"), C("B983FF")],
    pink=[C("C98AFF"), C("D69CFF"), C("E0A8FF")],
    teeth=[C("D9C4FF"), C("C6ACFA")],
    mouth=[C("7A2FB8"), C("9A3FD0"), C("5E2496")],
)
MAT = dict(
    body=mat_lowpoly("M_Void_Body", 0.7), crystal=mat_glow("M_Void_Crystal", 0.10),
    gem=mat_glow("M_Void_Gem", 0.35), eye=mat_glow("M_Eye_Glow", 3.0),
)
ROOT = bpy.data.collections.new("VOID_LEVIATHAN")
SC.collection.children.link(ROOT)
COLL = {}
for cname in ["HEAD", "EYES", "TEETH", "BODY", "CROWN", "DORSAL", "FLANKS", "TAIL", "WHISKERS", "GEMS"]:
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




def body_col(rnd, hi=0.10):
    return pick(PAL["body_hi"] if rnd.random() < hi else PAL["body"], rnd)


def blade(V, F, FC, base, d, L, r, base_stops, tip_stops, t, rnd, belly=0.42, thin=0.34):
    """One crystal blade: wide in its plane, thin across, dark root to bright tip."""
    d = d.normalized()
    add_spike(V, F, FC, base - d * 0.15, base + d * L, r,
              two_tone(lambda: grad(base_stops, t, rnd), lambda: grad(tip_stops, t, rnd)), n=4, belly=belly,
              flat=1.0, flat_u=thin)


# ----------------------------------------------------------------------------- serpentine spine (profile S-curve)
SPINE_CTRL = [  # (x, y, z, radius)   head end -> tail tip
    (0.00, -2.85, 7.40, .40), (0.00, -1.70, 7.00, .46), (0.05, -0.60, 6.15, .54), (0.10, -0.15, 5.00, .60),
    (0.08, -0.75, 3.90, .66), (0.00, -1.85, 3.15, .74), (-0.05, -2.75, 2.30, .78), (-0.10, -2.90, 1.40, .76),
    (-0.15, -2.10, 0.75, .70), (-0.25, -0.85, 0.72, .62), (-0.40, 0.50, 1.20, .54), (-0.60, 1.85, 1.95, .45),
    (-0.80, 3.15, 2.62, .36), (-0.95, 4.30, 3.12, .27), (-1.05, 5.15, 3.48, .16)]
SP = catmull(SPINE_CTRL, 3)
CEN = [Vector((x, y, z)) for (x, y, z, r) in SP]
RAD = [r * 1.38 for (*_a, r) in SP]
NS = len(CEN)


def sframe(k):
    tng = (CEN[min(k + 1, NS - 1)] - CEN[max(k - 1, 0)]).normalized()
    dorsal = XAX.cross(tng).normalized()
    side = tng.cross(dorsal).normalized()
    return tng, dorsal, side


def build_body():
    """ONE mesh: dark faceted back, lavender belly stepped into overlapping plates."""
    rnd = random.Random(1)
    ups = [sframe(k)[1] for k in range(NS)]
    tops = [r for r in RAD]
    bots = [r * (1.10 if k % 3 == 0 else 0.96) for k, r in enumerate(RAD)]
    widths = [r * 0.95 for r in RAD]

    def col(t, sa):
        if sa < -0.55:
            return pick(PAL["belly"], rnd)
        if sa < -0.25:
            return pick(PAL["belly_shade"], rnd)
        return body_col(rnd, 0.14 if sa > 0.6 else 0.06)
    flame_ribbon("Body_Serpent", CEN, ups, widths, tops, bots, col, COLL["BODY"], MAT["body"], rnd, n=10, jitter=0.025)


# ----------------------------------------------------------------------------- head
HEAD_M = Matrix.Translation((0, -3.95, 7.20)) @ Matrix.Rotation(math.radians(10), 4, "X") @ Matrix.Scale(2.05, 4)


def build_head():
    rnd = random.Random(21)
    UP = [(0.45, 0.22, 0.17, -0.10), (0.27, 0.33, 0.29, -0.11), (0.08, 0.31, 0.31, -0.09),
          (-0.12, 0.23, 0.22, -0.07), (-0.34, 0.16, 0.15, -0.06), (-0.52, 0.11, 0.09, -0.07),
          (-0.63, 0.06, 0.03, -0.11)]
    rings = []
    for (y, w, zt, zb) in UP:
        zm = zb + (zt - zb) * 0.45
        rings.append([Vector(q) for q in ((0, y, zt), (.55 * w, y, .88 * zt), (w, y, zm), (.92 * w, y, zb),
                                          (0, y, zb + 0.03), (-.92 * w, y, zb), (-w, y, zm), (-.55 * w, y, .88 * zt))])
    V, F, FC = ring_mesh(rings, Vector((0, 0.56, 0.02)), Vector((0, -0.72, -0.20)),
                         lambda k, j: pick(PAL["mouth"], rnd) if j in (3, 4) else body_col(rnd, 0.12))
    skull = build("Head_Skull", V, F, FC, COLL["HEAD"], MAT["body"], HEAD_M)

    tree = BVHTree.FromPolygons(V, F)
    cutters = []
    for side, sx in (("L", 1), ("R", -1)):
        d = Vector((0.66 * sx, -0.66, 0.34)).normalized()
        hit, nrm, _, _ = tree.ray_cast(Vector((0, 0.08, 0.10)), d)
        if nrm.dot(d) < 0:
            nrm = -nrm
        Z = (nrm + d).normalized()
        slant = Vector((0, -1, -0.35))
        Xa = (slant - Z * slant.dot(Z)).normalized(); Ya = Z.cross(Xa)
        M = HEAD_M @ axes_matrix(Xa, Ya, Z, hit)
        r1, r2, dep, n = 0.10, 0.085, 0.02, 4
        CV, CF, CC = [], [], []
        for (r, z) in ((r2, -dep), (r1, 0.0), (r1 * 1.8, 0.2)):
            for k in range(n):
                a = 2 * math.pi * k / n
                CV.append(Vector((r * 1.7 * math.cos(a), r * 0.7 * math.sin(a), z)))
        for ring in range(2):
            for k in range(n):
                k2 = (k + 1) % n
                CF.append([ring * n + k, ring * n + k2, (ring + 1) * n + k2, (ring + 1) * n + k]); CC.append(C("6A2FD8"))
        CF.append(list(range(n))[::-1]); CC.append(C("6A2FD8"))
        CF.append([2 * n + k for k in range(n)]); CC.append(C("6A2FD8"))
        cut = build(f"_cut_{side}", CV, CF, CC, SC.collection, MAT["body"], M)
        cutters.append(cut)
        mod = skull.modifiers.new(f"Socket_{side}", "BOOLEAN"); mod.operation = "DIFFERENCE"; mod.object = cut
        GV = [Vector((r2 * 1.65 * math.cos(2 * math.pi * k / n), r2 * 0.68 * math.sin(2 * math.pi * k / n), -dep + 0.003))
              for k in range(n)] + [Vector((0, 0, -dep + 0.014))]
        GF = [[k, (k + 1) % n, n] for k in range(n)]
        build(f"Eye_{side}_Glow", GV, GF, [jit(C("F06CFF"), 0.05, rnd) for _ in GF], COLL["EYES"], MAT["eye"], M, recalc=False)
    dg = bpy.context.evaluated_depsgraph_get(); dg.update()
    new_me = bpy.data.meshes.new_from_object(skull.evaluated_get(dg))
    old = skull.data; skull.modifiers.clear(); skull.data = new_me; bpy.data.meshes.remove(old)
    for pl in new_me.polygons:
        pl.use_smooth = False
    for c in cutters:
        me = c.data; bpy.data.objects.remove(c); bpy.data.meshes.remove(me)

    # lower jaw, wide open
    LO = [(0.40, 0.21, -0.11, -0.24), (0.12, 0.27, -0.12, -0.30), (-0.14, 0.19, -0.13, -0.26), (-0.36, 0.11, -0.14, -0.21)]
    hinge = Vector((0, 0.40, -0.10))
    Rj = Matrix.Rotation(math.radians(24), 3, "X")
    jr = lambda q: Rj @ (Vector(q) - hinge) + hinge
    rings = [[jr(q) for q in ((0, y, zt), (.6 * w, y, zt + 0.01), (w, y, (zt + zb) / 2), (.7 * w, y, zb),
                              (0, y, zb - 0.02), (-.7 * w, y, zb), (-w, y, (zt + zb) / 2), (-.6 * w, y, zt + 0.01))]
             for (y, w, zt, zb) in LO]
    V, F, FC = ring_mesh(rings, jr((0, 0.5, -0.15)), jr((0, -0.54, -0.10)),
                         lambda k, j: pick(PAL["mouth"], rnd) if j in (0, 7) else body_col(rnd, 0.12))
    build("Head_Jaw", V, F, FC, COLL["HEAD"], MAT["body"], HEAD_M)

    # teeth: one piece for each jaw
    for nm, pts, dz, xf in (("Upper", [(-0.56, 0.05), (-0.46, 0.10), (-0.34, 0.14), (-0.20, 0.19), (-0.05, 0.23)], -0.13, lambda q: Vector(q)),
                            ("Lower", [(-0.44, 0.07), (-0.32, 0.12), (-0.18, 0.16), (-0.04, 0.20)], 0.12, jr)):
        V, F, FC = [], [], []
        for (y, x) in pts:
            for sx in (1, -1):
                z0 = -0.07 if nm == "Upper" else -0.13
                L = dz * (1.0 if y < -0.4 else 0.65)
                add_spike(V, F, FC, xf((x * sx, y, z0)), xf((x * sx, y - 0.02, z0 + L)), 0.03, lambda: pick(PAL["teeth"], rnd), n=4, belly=0.3)
        build(f"Teeth_{nm}", V, F, FC, COLL["TEETH"], MAT["gem"], HEAD_M)

    # brow / cheek blades (one piece) and the forehead gem
    V, F, FC = [], [], []
    for sx in (1, -1):
        for b, tp, r in (((0.20 * sx, -0.04, 0.22), (0.40 * sx, 0.62, 0.50), 0.10), ((0.27 * sx, 0.16, 0.06), (0.62 * sx, 0.80, 0.14), 0.11),
                         ((0.22 * sx, 0.20, -0.06), (0.46 * sx, 0.70, -0.20), 0.09), ((0.10 * sx, -0.30, 0.15), (0.16 * sx, -0.12, 0.34), 0.05)):
            add_spike(V, F, FC, Vector(b), Vector(tp), r, two_tone(lambda: pick(PAL["wingdark"], rnd), lambda: pick(PAL["indigo"] + PAL["violet"], rnd)),
                      n=4, belly=0.3, flat=1.0, flat_u=0.5)
    build("Head_Blades", V, F, FC, COLL["HEAD"], MAT["crystal"], HEAD_M)
    c0 = Vector((0, -0.08, 0.30)); nv = Vector((0, -0.45, 1)).normalized(); upv = Vector((0, 1, 0.45)).normalized(); sv = nv.cross(upv)
    cor = [c0 + upv * 0.17, c0 + sv * 0.10, c0 - upv * 0.17, c0 - sv * 0.10]
    V = [c0 + nv * 0.07] + cor + [c0 - nv * 0.04]
    F = [[0, 1 + i, 1 + (i + 1) % 4] for i in range(4)] + [[5, 1 + (i + 1) % 4, 1 + i] for i in range(4)]
    build("Gem_Forehead", V, F, [pick(PAL["pink"] + PAL["lilac"], rnd) for _ in F], COLL["GEMS"], MAT["gem"], HEAD_M)


# ----------------------------------------------------------------------------- crown of long crystal blades
def build_crown():
    """Mane of long crystal blades: fans out around the head and streams backward (one cluster, shared root)."""
    rnd = random.Random(31)
    base = Vector((0, -3.00, 7.55))
    V, F, FC = [], [], []
    # outer ring: very long blades streaming back; thin stems swelling into a crystal near the tip
    for phi, L, back in ((0, 3.4, 0.9), (20, 3.8, 1.0), (-20, 3.8, 1.0), (42, 4.4, 1.1), (-42, 4.4, 1.1), (64, 5.0, 1.2), (-64, 5.0, 1.2),
                         (86, 5.4, 1.25), (-86, 5.4, 1.25), (106, 4.6, 1.3), (-106, 4.6, 1.3), (128, 3.4, 1.4), (-128, 3.4, 1.4)):
        a = math.radians(phi + rnd.uniform(-5, 5))
        d = Vector((math.sin(a), back, math.cos(a)))
        blade(V, F, FC, base + Vector((math.sin(a) * 0.3, 0, math.cos(a) * 0.25)), d, L * rnd.uniform(0.9, 1.08), 0.30,
              ["wingdark", "indigo"], ["violet", "lilac", "pink"], rnd.uniform(0.45, 1.0), rnd, belly=0.74, thin=0.30)
    # middle ring: shorter, darker
    for phi, L in ((10, 2.6), (-10, 2.6), (32, 2.8), (-32, 2.8), (54, 3.0), (-54, 3.0), (76, 3.1), (-76, 3.1), (98, 2.6), (-98, 2.6)):
        a = math.radians(phi + rnd.uniform(-5, 5))
        d = Vector((math.sin(a), 0.85, math.cos(a)))
        blade(V, F, FC, base + Vector((math.sin(a) * 0.25, -0.1, math.cos(a) * 0.2)), d, L * rnd.uniform(0.9, 1.1), 0.36,
              ["wingdark", "wingdark"], ["indigo", "violet", "lilac"], rnd.uniform(0.2, 1.0), rnd, belly=0.50, thin=0.32)
    # inner crown: upright dark horns
    for phi, L in ((0, 1.9), (18, 1.7), (-18, 1.7), (40, 1.5), (-40, 1.5), (66, 1.3), (-66, 1.3)):
        a = math.radians(phi)
        d = Vector((math.sin(a), 0.40, math.cos(a)))
        blade(V, F, FC, base + Vector((math.sin(a) * 0.2, -0.25, math.cos(a) * 0.1)), d, L, 0.26,
              ["wingdark", "wingdark"], ["wingdark", "indigo", "violet"], rnd.uniform(0.2, 1.0), rnd, belly=0.42, thin=0.36)
    build("Crown_Crystals", V, F, FC, COLL["CROWN"], MAT["crystal"])


# ----------------------------------------------------------------------------- dorsal crest + gems, flank and ventral crystals
def build_dorsal():
    rnd = random.Random(41)
    V, F, FC = [], [], []
    GV, GF, GC = [], [], []
    for k in range(2, NS - 1):
        tng, dorsal, side = sframe(k)
        f = k / (NS - 1)
        r = RAD[k]
        if (k % 2 == 0 and f < 0.32) or k % 3 == 0:
            L = (3.0 - 5.0 * f) if f < 0.32 else (1.5 + 0.6 * math.sin(f * 9))
            L = max(0.9, L) * rnd.uniform(0.85, 1.15)
            d = dorsal * 0.70 + tng * 1.05 + side * rnd.uniform(-0.22, 0.22)
            blade(V, F, FC, CEN[k] + dorsal * r * 0.8, d, L, 0.30 + 0.08 * (L > 1.6), ["wingdark", "wingdark", "indigo"],
                  ["wingdark", "indigo", "violet"] if f > 0.32 else ["violet", "lilac", "pink"], rnd.uniform(0.3, 1.0), rnd)
        elif k % 3 == 1 and f > 0.12:
            c0 = CEN[k] + dorsal * r * 0.98
            cor = [c0 + tng * 0.40, c0 + side * 0.20, c0 - tng * 0.40, c0 - side * 0.20]
            b0 = len(GV)
            GV += [c0 + dorsal * 0.14] + cor + [c0 - dorsal * 0.05]
            for i in range(4):
                GF.append([b0, b0 + 1 + i, b0 + 1 + (i + 1) % 4]); GC.append(pick(PAL["lilac"] + PAL["pink"], rnd))
                GF.append([b0 + 5, b0 + 1 + (i + 1) % 4, b0 + 1 + i]); GC.append(pick(PAL["violet"], rnd))
    build("Dorsal_Crystals", V, F, FC, COLL["DORSAL"], MAT["crystal"])
    build("Dorsal_Gems", GV, GF, GC, COLL["GEMS"], MAT["gem"])


def build_flanks():
    rnd = random.Random(51)
    for sname, sgn in (("L", 1), ("R", -1)):
        V, F, FC = [], [], []
        for k in range(NS):
            f = k / (NS - 1)
            if not (0.26 < f < 0.74) or k % 2:
                continue
            tng, dorsal, side = sframe(k)
            for _ in range(2):
                d = side * sgn * rnd.uniform(0.7, 1.0) - dorsal * rnd.uniform(0.2, 0.8) + tng * rnd.uniform(0.6, 1.2)
                blade(V, F, FC, CEN[k] + side * sgn * RAD[k] * 0.75 - dorsal * RAD[k] * 0.3, d, rnd.uniform(1.1, 2.1), 0.32, ["indigo", "violet"],
                      ["violet", "lilac", "pink"], rnd.uniform(0.3, 1.0), rnd)
        build(f"Flank_Crystals_{sname}", V, F, FC, COLL["FLANKS"], MAT["crystal"])
    V, F, FC = [], [], []
    for k in range(NS):
        f = k / (NS - 1)
        if not (0.58 < f < 0.82) or k % 3:
            continue
        tng, dorsal, side = sframe(k)
        d = -dorsal * 0.75 + tng * 1.0 + side * rnd.uniform(-0.3, 0.3)
        blade(V, F, FC, CEN[k] - dorsal * RAD[k] * 0.7, d, rnd.uniform(2.0, 3.0), 0.42, ["indigo", "violet"],
              ["violet", "lilac", "pink"], rnd.uniform(0.4, 1.0), rnd)
    build("Ventral_Crystals", V, F, FC, COLL["FLANKS"], MAT["crystal"])


def build_tail_fan():
    """Tail plume: long blades rooted along the last stretch of the tail, all streaming with it (one piece)."""
    rnd = random.Random(61)
    V, F, FC = [], [], []
    k0 = int(NS * 0.80)
    for k in range(k0, NS, 2):
        tng, dorsal, side = sframe(min(k, NS - 2))
        f = (k - k0) / (NS - 1 - k0)
        for sgn in (1, -1):
            ang = math.radians(sgn * (62 - 44 * f) + rnd.uniform(-6, 6))
            d = tng * math.cos(ang) + dorsal * math.sin(ang) + side * rnd.uniform(-0.2, 0.2)
            L = (3.0 + 1.8 * f) * (1.15 if sgn > 0 else 0.95) * rnd.uniform(0.88, 1.1)
            blade(V, F, FC, CEN[k], d, L, 0.50, ["wingdark", "indigo", "indigo"], ["violet", "lilac", "pink"],
                  rnd.uniform(0.35, 1.0), rnd, belly=0.50, thin=0.26)
            ang2 = math.radians(sgn * (40 - 28 * f) + rnd.uniform(-6, 6))
            d2 = tng * math.cos(ang2) + dorsal * math.sin(ang2) + side * rnd.uniform(-0.3, 0.3)
            blade(V, F, FC, CEN[k], d2, L * 0.6, 0.40, ["wingdark", "wingdark"], ["wingdark", "indigo", "violet"],
                  rnd.uniform(0.2, 1.0), rnd, belly=0.45, thin=0.34)
    tng, dorsal, side = sframe(NS - 2)
    blade(V, F, FC, CEN[-1], tng, 4.8, 0.5, ["indigo", "violet"], ["lilac", "pink"], 1.0, rnd, belly=0.5, thin=0.28)
    build("Tail_Fan", V, F, FC, COLL["TAIL"], MAT["crystal"])


def build_whiskers():
    rnd = random.Random(71)
    bz = lambda p, t: p[0] * (1 - t) ** 3 + p[1] * 3 * t * (1 - t) ** 2 + p[2] * 3 * t * t * (1 - t) + p[3] * t ** 3
    V, F, FC = [], [], []
    for sx in (1, -1):
        for ctrl, r0 in ((((0.26, -4.75, 6.35), (0.45, -5.25, 5.30), (0.32, -4.65, 4.40), (0.12, -5.15, 3.85)), 0.065),
                         (((0.62, -3.55, 6.85), (1.85, -3.35, 6.40), (2.45, -3.05, 5.10), (2.00, -3.20, 4.30)), 0.06),
                         (((0.50, -4.20, 6.60), (1.15, -4.45, 5.90), (1.25, -4.05, 5.10), (0.95, -4.30, 4.60)), 0.05)):
            P = [Vector((x * sx, y, z)) for (x, y, z) in ctrl]
            pts = [bz(P, i / 9) for i in range(10)]
            add_tube(V, F, FC, pts, [r0 * (1 - 0.55 * i / 9) for i in range(10)], lambda: pick(PAL["indigo"] + PAL["wingdark"][:2], rnd), n=5)
            d = (pts[-1] - pts[-2]).normalized()
            add_spike(V, F, FC, pts[-1] - d * 0.05, pts[-1] + d * 0.34, 0.07, two_tone(lambda: pick(PAL["violet"], rnd), lambda: pick(PAL["pink"], rnd)),
                      n=4, belly=0.45)
    build("Whiskers", V, F, FC, COLL["WHISKERS"], MAT["crystal"])


# ----------------------------------------------------------------------------- cameras / lights / render
def setup_lights_cameras():
    L = COLL["CAMERAS_LIGHTS"]
    for name, energy, ang, loc in (("Light_Key_Sun", 1.3, 30, (-5, -9, 10)), ("Light_Fill_Sun", 0.6, 60, (9, 4, 4)),
                                   ("Light_Back_Sun", 0.9, 60, (-3, 9, 6))):
        sun = bpy.data.lights.new(name, "SUN"); sun.energy = energy; sun.angle = math.radians(ang)
        so = bpy.data.objects.new(name, sun); L.objects.link(so); so.location = loc; look_at(so, (0, 0, 0))
    cams = {}
    el = math.radians(3)
    for name, d, tgt, scale, res in (
            ("CAM_Face_Ortho", Vector((0, -math.cos(el), math.sin(el))), Vector((-0.3, 0, 5.2)), 13.6, (900, 1000)),
            ("CAM_Profil_Ortho", Vector((math.cos(el), 0, math.sin(el))), Vector((0, 1.9, 4.9)), 17.0, (1150, 1000)),
            ("CAM_TroisQuarts_Ortho", Vector((0.72, -0.66, 0.22)).normalized(), Vector((-0.2, 1.5, 4.7)), 16.0, (1100, 1000)),
            ("CAM_Dos_Ortho", Vector((0, math.cos(el), math.sin(el))), Vector((-0.3, 0, 5.2)), 13.6, (900, 1000))):
        cd = bpy.data.cameras.new(name); cd.type = "ORTHO"; cd.ortho_scale = scale; cd.clip_end = 200
        co = bpy.data.objects.new(name, cd); L.objects.link(co)
        co.location = tgt + d * 40; look_at(co, tgt); co["res"] = res
        cams[name] = co
    SC.camera = cams["CAM_Face_Ortho"]
    return cams


build_body()
build_head()
build_crown()
build_dorsal()
build_flanks()
build_tail_fan()
build_whiskers()
setup_world()
cams = setup_lights_cameras()
SC.render.engine = "CYCLES"
SC.cycles.device = "CPU"
SC.cycles.samples = int(os.environ.get("LEVI_SAMPLES", "48"))
SC.cycles.use_denoising = True
SC.view_settings.view_transform = "Standard"
QUAL = float(os.environ.get("LEVI_SCALE", "1.0"))
BLEND = os.path.join(HERE, "void_leviathan.blend")
SC.render.resolution_x, SC.render.resolution_y = 900, 1000
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
if os.environ.get("LEVI_NO_RENDER") != "1":
    for key, fname in (("CAM_Face_Ortho", "face.png"), ("CAM_Profil_Ortho", "profil.png"),
                       ("CAM_TroisQuarts_Ortho", "trois_quarts.png"), ("CAM_Dos_Ortho", "dos.png")):
        SC.camera = cams[key]
        SC.render.resolution_x, SC.render.resolution_y = int(cams[key]["res"][0] * QUAL), int(cams[key]["res"][1] * QUAL)
        SC.render.filepath = os.path.join(RENDER_DIR, fname)
        bpy.ops.render.render(write_still=True)
    SC.camera = cams["CAM_Face_Ortho"]
    SC.render.resolution_x, SC.render.resolution_y = 900, 1000
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print("DONE")
